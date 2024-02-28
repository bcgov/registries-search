# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoints for searching entities - extended."""
from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import User, SearchHistory
from bor_api.services import jwt, solr_temp
from bor_api.services.bor_solr import SearchParams, entities_search, xlsx_response
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField
from bor_api.services.base_solr.utils import parse_facets, prep_query_str, prep_query_str_adv
from bor_api.utils.request_validators import validate_search_request


bp = Blueprint('EXTENDED', __name__, url_prefix='/extended')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
@jwt.requires_auth
def extended_search():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Return a list of entity results from solr including extended entity information."""
    try:
        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)
        request_json, errors = validate_search_request(user)
        if errors:
            return bad_request_response('Errors processing request.', errors)

        # set base query params
        query_json: dict = request_json.get('query', {})
        value = query_json.get('value', None)
        query = {
            'value': prep_query_str(value),
            'email_value': prep_query_str_adv(value),
            EntityField.BN_Q.value: prep_query_str(query_json.get(EntityField.BN.value, '')),
            EntityField.IDENTIFIER_Q.value: prep_query_str(query_json.get(EntityField.IDENTIFIER.value, '')),
            EntityField.LEGAL_NAME_SINGLE_Q.value: prep_query_str(query_json.get(EntityField.LEGAL_NAME.value, ''))
        }
        # set faceted category params
        categories_json: dict = request_json.get('categories', {})
        categories = {
            EntityField.ENTITY_TYPE: categories_json.get(EntityField.ENTITY_TYPE.value, None),
            EntityField.LEGAL_TYPE: categories_json.get(EntityField.LEGAL_TYPE.value, None),
            EntityField.STATE: categories_json.get(EntityField.STATE.value, None)
        }
        # set nested child query params
        roles_json: dict = query_json.get(EntityField.ROLES.value, {})
        child_query = {
            # addresses
            AddressField.ADDRESS_Q.value: prep_query_str(query_json.get(EntityField.ENTITY_ADDRESSES.value, '')),
            # roles
            EntityRoleField.RELATED_BN_Q.value: prep_query_str(roles_json.get(EntityRoleField.RELATED_BN.value, '')),
            EntityRoleField.RELATED_EMAIL_Q.value:
                prep_query_str_adv(roles_json.get(EntityRoleField.RELATED_EMAIL.value, '')),
            EntityRoleField.RELATED_IDENTIFIER_Q.value:
                prep_query_str(roles_json.get(EntityRoleField.RELATED_IDENTIFIER.value, '')),
            EntityRoleField.RELATED_NAME_SINGLE_Q.value:
                prep_query_str(roles_json.get(EntityRoleField.RELATED_NAME.value, '')),
            EntityRoleField.RELATED_Q.value: prep_query_str(roles_json.get('value', ''))
        }
        # set nested child faceted category params
        address_categories_json: dict = categories_json.get(EntityField.ENTITY_ADDRESSES.value, {})
        address_categories = {
            AddressField.ADDRESS_CITY: address_categories_json.get(AddressField.ADDRESS_CITY.value, None),
            AddressField.ADDRESS_COUNTRY: address_categories_json.get(AddressField.ADDRESS_COUNTRY.value, None),
            AddressField.ADDRESS_REGION: address_categories_json.get(AddressField.ADDRESS_REGION.value, None),
        }
        role_categories_json: dict = categories_json.get(EntityField.ROLES.value, {})
        role_categories = {
            EntityRoleField.RELATED_ENTITY_TYPE: role_categories_json.get(EntityRoleField.RELATED_ENTITY_TYPE.value,
                                                                          None),
            EntityRoleField.RELATED_STATE: role_categories_json.get(EntityRoleField.RELATED_STATE.value, None),
            EntityRoleField.ROLE_TYPE: role_categories_json.get(EntityRoleField.ROLE_TYPE.value, None)
        }
        child_categories = {**address_categories, **role_categories}
        # set nested date params
        child_date_ranges = {}
        role_date_range: dict = roles_json.get(EntityRoleField.ROLE_DATES.value, {})
        if role_date_range:
            child_date_ranges = {
                DateRangeField.START: role_date_range.get(DateRangeField.START.value, '*'),
                DateRangeField.END: role_date_range.get(DateRangeField.END.value, '*')
            }

        start = request_json.get('start', solr_temp.default_start)
        rows = request_json.get('rows', solr_temp.default_rows)
        try:
            start = int(start)
            rows = int(rows)
        except ValueError:  # catch invalid start/row entry
            return {'message': "Expected integer for params: 'start', 'rows'"}, HTTPStatus.BAD_REQUEST

        params = SearchParams(query=query,
                              rows=rows,
                              start=start,
                              categories=categories,
                              child_query=child_query,
                              child_categories=child_categories,
                              child_date_ranges=child_date_ranges)

        results = entities_search(params, solr_temp)
        docs = results.get('response', {}).get('docs')

        # save search in the db
        SearchHistory(params=request_json,
                      results=docs,
                      submitter_id=user.id).save()

        if str(request.accept_mimetypes) == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return xlsx_response(docs)

        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'categories': {
                        **categories,
                        EntityField.ENTITY_ADDRESSES.value: address_categories,
                        EntityField.ROLES.value: role_categories
                    },
                    'query': {
                        'value': query['value'],
                        EntityField.BN.value: query[EntityField.BN_Q.value],
                        EntityField.IDENTIFIER.value: query[EntityField.IDENTIFIER_Q.value],
                        EntityField.LEGAL_NAME.value: query[EntityField.LEGAL_NAME_SINGLE_Q.value],
                        EntityField.ENTITY_ADDRESSES.value: child_query[AddressField.ADDRESS_Q.value],
                        EntityField.ROLES.value: {
                            EntityRoleField.RELATED_BN.value: child_query[EntityRoleField.RELATED_BN_Q.value],
                            EntityRoleField.RELATED_EMAIL.value: child_query[EntityRoleField.RELATED_EMAIL_Q.value],
                            EntityRoleField.RELATED_IDENTIFIER.value:
                                child_query[EntityRoleField.RELATED_IDENTIFIER_Q.value],
                            EntityRoleField.RELATED_NAME.value:
                                child_query[EntityRoleField.RELATED_NAME_SINGLE_Q.value],
                            EntityRoleField.ROLE_DATES.value: child_date_ranges,
                            'value': child_query[EntityRoleField.RELATED_Q.value]
                        }
                    },
                    'rows': rows or solr_temp.default_rows,
                    'start': start or solr_temp.default_start
                },
                'totalResults': results.get('response', {}).get('numFound'),
                'results': docs}}

        return jsonify(response), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
