# Copyright © 2023 Province of British Columbia
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
"""API endpoints for searching entities."""
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from bor_api.exceptions import exception_response
from bor_api.services import bor_solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils import SearchParams, entities_search, parse_facets, prep_query_str


bp = Blueprint('ENTITIES', __name__, url_prefix='/entities')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
def entities():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Return a list of entity results from solr."""
    try:
        request_json = request.get_json()
        query_json = request_json.get('query', {})
        value = query_json.get('value', None)
        if not value or not isinstance(value, str):
            # update this later once we have other filters going
            return jsonify({'message': "Expected a string for 'value'."}), HTTPStatus.BAD_REQUEST

        # set base query params
        query = {
            'value': prep_query_str(value),
            Field.BN_Q.value: prep_query_str(query_json.get(Field.BN.value, '')),
            Field.IDENTIFIER_Q.value: prep_query_str(query_json.get(Field.IDENTIFIER.value, '')),
            Field.LEGAL_NAME_SINGLE_Q.value: prep_query_str(query_json.get(Field.LEGAL_NAME.value, ''))
        }
        # set faceted category params
        categories_json = request_json.get('categories', {})
        categories = {
            Field.ENTITY_TYPE: categories_json.get(Field.ENTITY_TYPE.value, None),
            Field.LEGAL_TYPE: categories_json.get(Field.LEGAL_TYPE.value, None),
            Field.STATE: categories_json.get(Field.STATE.value, None)
        }
        # set nested child query params
        roles_json = query_json.get(Field.ROLES.value, {})
        child_query = {
            # addresses
            Field.ADDRESS_Q.value: prep_query_str(query_json.get(Field.ENTITY_ADDRESSES.value, '')),
            # roles
            Field.RELATED_BN_Q.value: prep_query_str(roles_json.get(Field.RELATED_BN.value, '')),
            Field.RELATED_IDENTIFIER_Q.value: prep_query_str(roles_json.get(Field.RELATED_IDENTIFIER.value, '')),
            Field.RELATED_NAME_SINGLE_Q.value: prep_query_str(roles_json.get(Field.RELATED_NAME.value, ''))
        }
        # set nested child faceted category params
        address_categories_json = categories_json.get(Field.ENTITY_ADDRESSES.value, {})
        address_categories = {
            Field.ADDRESS_CITY: address_categories_json.get(Field.ADDRESS_CITY.value, None),
            Field.ADDRESS_COUNTRY: address_categories_json.get(Field.ADDRESS_COUNTRY.value, None),
            Field.ADDRESS_REGION: address_categories_json.get(Field.ADDRESS_REGION.value, None),
        }
        role_categories_json = categories_json.get(Field.ROLES.value, {})
        role_categories = {
            Field.RELATED_ENTITY_TYPE: role_categories_json.get(Field.RELATED_ENTITY_TYPE.value, None),
            Field.RELATED_STATE: role_categories_json.get(Field.RELATED_STATE.value, None),
            Field.ROLE_TYPE: role_categories_json.get(Field.ROLE_TYPE.value, None)
        }
        child_categories = {**address_categories, **role_categories}
        # set nested date params
        child_date_ranges = {}
        role_date_range = roles_json.get(Field.ROLE_DATES.value, {})
        if role_date_range:
            child_date_ranges = {
                Field.START: role_date_range.get(Field.START.value, '*'),
                Field.END: role_date_range.get(Field.END.value, '*')
            }

        start = request_json.get('start', bor_solr.default_start)
        rows = request_json.get('rows', bor_solr.default_rows)
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

        results = entities_search(params)
        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'categories': {
                        **categories,
                        Field.ENTITY_ADDRESSES.value: address_categories,
                        Field.ROLES.value: role_categories
                    },
                    'query': {
                        'value': query['value'],
                        Field.BN.value: query[Field.BN_Q.value],
                        Field.IDENTIFIER.value: query[Field.IDENTIFIER_Q.value],
                        Field.LEGAL_NAME.value: query[Field.LEGAL_NAME_SINGLE_Q.value],
                        Field.ENTITY_ADDRESSES.value: child_query[Field.ADDRESS_Q.value],
                        Field.ROLES.value: {
                            Field.RELATED_BN.value: child_query[Field.RELATED_BN_Q.value],
                            Field.RELATED_IDENTIFIER.value: child_query[Field.RELATED_IDENTIFIER_Q.value],
                            Field.RELATED_NAME.value: child_query[Field.RELATED_NAME_SINGLE_Q.value],
                            Field.ROLE_DATES.value: child_date_ranges
                        }
                    },
                    'rows': rows or bor_solr.default_rows,
                    'start': start or bor_solr.default_start
                },
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}
        return jsonify(response), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
