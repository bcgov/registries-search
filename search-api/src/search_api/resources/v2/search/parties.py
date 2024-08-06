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
"""API endpoints for Search."""
from http import HTTPStatus

from flask import jsonify, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
from search_api.services import business_solr
from search_api.services.base_solr.utils import QueryParams, parse_facets, prep_query_str
from search_api.services.business_solr.doc_fields import PartyField
from search_api.services.business_solr.utils import parties_search
import search_api.resources.utils as resource_utils
from search_api.utils.validators import validate_search_request


bp = Blueprint('PARTIES', __name__, url_prefix='/parties')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
def parties():
    """Return a list of parties results."""
    try:
        request_json, errors = validate_search_request()
        if errors:
            return resource_utils.bad_request_response('Errors processing request.', errors)
        # set base query params
        query_json: dict = request_json.get('query', {})
        value = query_json.get('value', None)
        query = {
            'value': prep_query_str(value, True),
            PartyField.PARTY_NAME_SINGLE.value: prep_query_str(query_json.get(PartyField.PARTY_NAME.value, '')),
            PartyField.PARENT_NAME_SINGLE.value: prep_query_str(query_json.get(PartyField.PARENT_NAME.value, '')),
            PartyField.PARENT_IDENTIFIER_Q.value: prep_query_str(query_json.get(
                PartyField.PARENT_IDENTIFIER.value, '')),
            PartyField.PARENT_BN_Q.value: prep_query_str(query_json.get(PartyField.PARENT_BN.value, ''))
        }

        # set faceted category params
        categories_json: dict = request_json.get('categories', {})
        categories = {
            PartyField.PARENT_TYPE: categories_json.get(PartyField.PARENT_TYPE.value, None),
            PartyField.PARENT_STATE: categories_json.get(PartyField.PARENT_STATE.value, None),
            PartyField.PARTY_ROLE: categories_json.get(PartyField.PARTY_ROLE.value, None)
        }

        # validate party roles
        if not (party_roles := categories.get(PartyField.PARTY_ROLE)):
            errors = [{'Invalid payload': f"Expected 'categories/{PartyField.PARTY_ROLE.value}:[...]'."}]
            return resource_utils.bad_request_response('Errors processing request.', errors)

        if [x for x in party_roles if x.lower() not in ['partner', 'proprietor']]:
            errors = [{
                'Invalid payload':
                    f"Expected 'categories/{PartyField.PARTY_ROLE.value}:' with values 'partner' and/or " +
                    "'proprietor'. Other party roles are not available."
            }]
            return resource_utils.bad_request_response('Errors processing request.', errors)

        params = QueryParams(query=query,
                             start=int(request_json.get('start', business_solr.default_start)),
                             rows=int(request_json.get('rows', business_solr.default_rows)),
                             categories=categories,
                             fields=business_solr.party_fields,
                             query_fields={
                                 PartyField.PARTY_NAME_Q: 'parent',
                                 PartyField.PARTY_NAME_STEM_AGRO: 'parent',
                                 PartyField.PARTY_NAME_SINGLE: 'parent',
                                 PartyField.PARTY_NAME_XTRA_Q: 'parent'},
                             query_boost_fields={
                                 PartyField.PARTY_NAME_Q: 2,
                                 PartyField.PARTY_NAME_STEM_AGRO: 2,
                                 PartyField.PARTY_NAME_SINGLE: 2},
                             query_fuzzy_fields={
                                 PartyField.PARTY_NAME_Q: {'short': 1, 'long': 2},
                                 PartyField.PARTY_NAME_STEM_AGRO: {'short': 1, 'long': 2},
                                 PartyField.PARTY_NAME_SINGLE: {'short': 1, 'long': 2}},
                             child_query={},
                             child_categories={},
                             child_date_ranges={})
        results = parties_search(params, business_solr)
        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'query': {
                        'value': query['value'],
                        PartyField.PARTY_NAME.value: query[PartyField.PARTY_NAME_SINGLE.value] or '',
                        PartyField.PARENT_NAME.value: query[PartyField.PARENT_NAME_SINGLE.value] or '',
                        PartyField.PARENT_IDENTIFIER.value: query[PartyField.PARENT_IDENTIFIER_Q.value] or '',
                        PartyField.PARENT_BN.value: query[PartyField.PARENT_BN_Q.value] or ''
                    },
                    'categories': {
                        PartyField.PARENT_TYPE.value: categories[PartyField.PARENT_TYPE],
                        PartyField.PARENT_STATE.value: categories[PartyField.PARENT_STATE],
                        PartyField.PARTY_ROLE.value: categories[PartyField.PARTY_ROLE]},
                    'rows': params.rows,
                    'start': params.start},
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')
            }
        }

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
