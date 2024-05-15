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
"""API endpoints for searching entities - public."""
from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

from bor_api.enums import SearchAccessLevel
from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import User, SearchHistory
from bor_api.services import jwt, solr
from bor_api.services.base_solr.utils import parse_facets, prep_query_str_adv
from bor_api.services.bor_solr import SearchParams, entities_search
from bor_api.services.bor_solr.fields import DateRangeField, EntityField, EntityRoleField
from bor_api.utils.request_validators import validate_search


# NOTE: this value determines access validation and data returned
_ACCESS_LEVEL = SearchAccessLevel.PUBLIC

bp = Blueprint('PUBLIC', __name__, url_prefix='/public')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
def public_search():
    """Return a list of entity results from solr for public users."""
    try:
        # NOTE: user may be None if they were not logged in
        user = None

        if 'Authorization' in request.headers:
            token = jwt.get_token_auth_header()
            jwt._validate_token(token)  # pylint: disable=protected-access; No unprotected option for what we need.
            user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        request_json, fields, _, errors = validate_search(user, _ACCESS_LEVEL)
        if errors:
            return bad_request_response('Errors processing request.', errors)

        # set base query params
        query_json: dict = request_json.get('query', {})
        value = query_json.get('value', None)
        query = {
            'value': prep_query_str_adv(value),
            EntityField.LEGAL_NAME_Q.value: prep_query_str_adv(query_json.get(EntityField.LEGAL_NAME.value, ''))
        }
        # set faceted category params
        categories_json: dict = request_json.get('categories', {})
        categories = {
            # NOTE: may be adding this back for citizenship filter
            # EntityField.NATIONALITIES: categories_json.get(EntityField.NATIONALITIES.value, None)
        }
        # set nested child query params
        roles_json: dict = query_json.get(EntityField.ROLES.value, {})
        child_query = {
            # roles
            EntityRoleField.RELATED_BN_Q.value:
                prep_query_str_adv(roles_json.get(EntityRoleField.RELATED_BN.value, '')),
            EntityRoleField.RELATED_IDENTIFIER_Q.value:
                prep_query_str_adv(roles_json.get(EntityRoleField.RELATED_IDENTIFIER.value, '')),
            EntityRoleField.RELATED_NAME_SINGLE_Q.value:
                prep_query_str_adv(roles_json.get(EntityRoleField.RELATED_NAME.value, '')),
            EntityRoleField.RELATED_Q.value: prep_query_str_adv(roles_json.get('value', ''))
        }
        role_categories_json: dict = categories_json.get(EntityField.ROLES.value, {})
        role_categories = {
            EntityRoleField.RELATED_ENTITY_TYPE: role_categories_json.get(EntityRoleField.RELATED_ENTITY_TYPE.value,
                                                                          None),
            EntityRoleField.RELATED_STATE: role_categories_json.get(EntityRoleField.RELATED_STATE.value, None),
            EntityRoleField.ROLE_TYPE: role_categories_json.get(EntityRoleField.ROLE_TYPE.value, None),
            # DateRange - for public search we only show active records
            DateRangeField.ACTIVE: [True]
        }

        start = request_json.get('start', solr.default_start)
        rows = request_json.get('rows', solr.default_rows)
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
                              child_categories=role_categories,
                              child_date_ranges=None,
                              fields=fields,
                              query_boost_fields={EntityField.LEGAL_NAME_Q: 2,
                                                  EntityField.LEGAL_NAME_AGRO_Q: 2,
                                                  EntityField.LEGAL_NAME_SINGLE_Q: 2,
                                                  EntityField.LEGAL_NAME_XTRA_Q: 2},
                              query_fields={EntityField.LEGAL_NAME_Q: 'parent',
                                            EntityField.LEGAL_NAME_AGRO_Q: 'parent',
                                            EntityField.LEGAL_NAME_SINGLE_Q: 'parent',
                                            EntityField.LEGAL_NAME_XTRA_Q: 'parent'},
                              query_fuzzy_fields={EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2},
                                                  EntityField.LEGAL_NAME_AGRO_Q: {'short': 1, 'long': 2},
                                                  EntityField.LEGAL_NAME_SINGLE_Q: {'short': 1, 'long': 2}},
                              query_synonym_fields={EntityField.LEGAL_NAME_SYN_Q: 'parent'})

        results = entities_search(params, solr)
        docs = results.get('response', {}).get('docs', [])
        # NOTE: Public search requires records with citizenships including canada to not show other citizenships
        # TODO: if this rule stands then create a secondary 'public' citizenships field in solr instead?
        # ticket: TBD
        for doc in docs:
            if 'CA' in doc.get(EntityField.NATIONALITIES.value, []):
                doc[EntityField.NATIONALITIES.value] = ['CA']

        # save search in the db
        SearchHistory(params=request_json,
                      results=docs,
                      submitter_id=user.id if user else None,
                      submitter_account_id=request.headers.get('Account-Id', None),
                      access_level=_ACCESS_LEVEL).save()

        if str(request.accept_mimetypes) == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            # return xlsx_response(docs)
            return {}, HTTPStatus.NOT_IMPLEMENTED

        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'categories': {
                        **categories,
                        EntityField.ROLES.value: role_categories
                    },
                    'query': {
                        'value': query['value'],
                        EntityField.LEGAL_NAME.value: query[EntityField.LEGAL_NAME_Q.value],
                        EntityField.ROLES.value: {
                            EntityRoleField.RELATED_BN.value: child_query[EntityRoleField.RELATED_BN_Q.value],
                            EntityRoleField.RELATED_IDENTIFIER.value:
                                child_query[EntityRoleField.RELATED_IDENTIFIER_Q.value],
                            EntityRoleField.RELATED_NAME.value:
                                child_query[EntityRoleField.RELATED_NAME_SINGLE_Q.value],
                            'value': child_query[EntityRoleField.RELATED_Q.value]
                        }
                    },
                    'rows': rows or solr.default_rows,
                    'start': start or solr.default_start
                },
                'totalResults': results.get('response', {}).get('numFound'),
                'results': docs}}

        return jsonify(response), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
