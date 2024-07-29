# Copyright © 2022 Province of British Columbia
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
import re
from contextlib import suppress
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
from search_api.services import business_solr
from search_api.services.base_solr.utils import QueryParams, parse_facets, prep_query_str
from search_api.services.business_solr.doc_fields import BusinessField, PartyField
from search_api.services.business_solr.utils import business_search, business_suggest, parties_search
import search_api.resources.utils as resource_utils


bp = Blueprint('SEARCH', __name__, url_prefix='/search')  # pylint: disable=invalid-name


def _clean_request_args(query: str) -> str:
    """Put backslash on expected param values that start with ':'."""
    expected_params = [
        BusinessField.NAME.value, BusinessField.IDENTIFIER.value, BusinessField.BN.value,
        PartyField.PARTY_NAME.value, PartyField.PARENT_NAME.value, PartyField.PARENT_IDENTIFIER.value,
        PartyField.PARENT_BN.value]
    query_cleaner_rgx = r'(::|^)(value|' + '|'.join(expected_params) + ')(::)'
    return re.sub(query_cleaner_rgx, r'\1\2:\:', query)


def _parse_url_param(param: str, param_str: str) -> str:
    """Return parsed param string if the param_str is for the param (i.e. 'value' for 'value:..')."""
    if f'{param}:' == param_str[:len(param) + 1]:
        return param_str[len(param) + 1:]
    return ''


@bp.get('/facets')
@cross_origin(origin='*')
def facets():  # pylint: disable=too-many-branches, too-many-locals
    """Return a list of business results from solr based from the given query."""
    try:
        # parse query params
        query = _clean_request_args(request.args.get('query', ''))
        if not query:
            return resource_utils.bad_request_response(
                'Invalid args', [{'missing param': "Expected url param 'query'."}])

        query_items = query.split('::')
        value = ''
        name = ''
        identifier = ''
        bn = ''  # pylint: disable=invalid-name
        for item in query_items:
            with suppress(AttributeError):
                if param := _parse_url_param('value', item):
                    value = param
                elif param := _parse_url_param(BusinessField.NAME.value, item):
                    name = param
                elif param := _parse_url_param(BusinessField.IDENTIFIER.value, item):
                    identifier = param
                elif param := _parse_url_param(BusinessField.BN.value, item):
                    bn = param  # pylint: disable=invalid-name

        if not value:
            return resource_utils.bad_request_response(
                'Invalid args',
                [{'query param': "Expected url param 'query' to have 'value:<string>'."}]
            )
        # clean query values
        query = {
            'value': prep_query_str(value, True),
            BusinessField.NAME_SINGLE.value: prep_query_str(name),
            BusinessField.IDENTIFIER_Q.value: prep_query_str(identifier),
            BusinessField.BN_Q.value: prep_query_str(bn)
        }
        # parse category params
        search_categories = {}
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if param := _parse_url_param(BusinessField.TYPE.value, category):
                        search_categories[BusinessField.TYPE] = param.upper().split(',')
                    elif param := _parse_url_param(BusinessField.STATE.value, category):
                        search_categories[BusinessField.STATE] = param.upper().split(',')

        # TODO: validate legal_type + state
        # parse paging params
        start = None
        rows = None
        try:
            with suppress(TypeError):  # suprress int cast over None
                start = int(request.args.get('start', None))
                rows = int(request.args.get('rows', None))
        except ValueError:  # catch invalid start/row entry
            return resource_utils.bad_request_response(
                'Invalid args',
                [{'start/row params': "Expected integer for params: 'start', 'rows'"}]
            )

        # set doc fields to return
        fields = business_solr.business_fields
        if request.args.get('parties') == 'true':
            fields = business_solr.business_with_parties_fields
        # create solr search params obj from parsed params
        params = QueryParams(query=query,
                             start=start,
                             rows=rows,
                             categories=search_categories,
                             fields=fields,
                             query_fields={
                                 BusinessField.NAME_Q: 'parent',
                                 BusinessField.NAME_STEM_AGRO: 'parent',
                                 BusinessField.NAME_SINGLE: 'parent',
                                 BusinessField.NAME_XTRA_Q: 'parent',
                                 BusinessField.BN_Q: 'parent',
                                 BusinessField.IDENTIFIER_Q: 'parent'},
                             query_boost_fields={
                                 BusinessField.NAME_Q: 2,
                                 BusinessField.NAME_STEM_AGRO: 2,
                                 BusinessField.NAME_SINGLE: 2},
                             query_fuzzy_fields={
                                 BusinessField.NAME_Q: {'short': 1, 'long': 2},
                                 BusinessField.NAME_STEM_AGRO: {'short': 1, 'long': 2},
                                 BusinessField.NAME_SINGLE: {'short': 1, 'long': 2}},
                             child_query={},
                             child_categories={},
                             child_date_ranges={})
        # execute search
        results = business_search(params, business_solr)
        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'query': {
                        'value': query['value'],
                        BusinessField.NAME.value: query[BusinessField.NAME_SINGLE.value] or '',
                        BusinessField.IDENTIFIER.value: query[BusinessField.IDENTIFIER_Q.value] or '',
                        BusinessField.BN.value: query[BusinessField.BN_Q.value] or ''
                    },
                    'categories': {
                        BusinessField.TYPE.value: search_categories.get(BusinessField.TYPE, ''),
                        BusinessField.STATE.value: search_categories.get(BusinessField.STATE, '')},
                    'rows': rows or business_solr.default_rows,
                    'start': start or 0
                },
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


@bp.get('/parties')
@cross_origin(origin='*')
def parties():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Return a list of business/parties results from solr based from the given query."""
    try:
        query = _clean_request_args(request.args.get('query', ''))
        if not query:
            return resource_utils.bad_request_response(
                'Invalid args', [{'missing param': "Expected url param 'query'."}])

        query_items = query.split('::')
        value = ''
        party_name = ''
        parent_name = ''
        parent_identifier = ''
        parent_bn = ''
        for item in query_items:
            with suppress(AttributeError):
                if param := _parse_url_param('value', item):
                    value = param
                elif param := _parse_url_param(PartyField.PARTY_NAME.value, item):
                    party_name = param
                elif param := _parse_url_param(PartyField.PARENT_NAME.value, item):
                    parent_name = param
                elif param := _parse_url_param(PartyField.PARENT_IDENTIFIER.value, item):
                    parent_identifier = param
                elif param := _parse_url_param(PartyField.PARENT_BN.value, item):
                    parent_bn = param
        if not value:
            return resource_utils.bad_request_response(
                'Invalid args',
                [{'query param': "Expected url param 'query' to have 'value:<string>'."}]
            )
        # clean query values
        query = {
            'value': prep_query_str(value, True),
            PartyField.PARTY_NAME_SINGLE.value: prep_query_str(party_name),
            PartyField.PARENT_NAME_SINGLE.value: prep_query_str(parent_name),
            PartyField.PARENT_IDENTIFIER_Q.value: prep_query_str(parent_identifier),
            PartyField.PARENT_BN_Q.value: prep_query_str(parent_bn)
        }

        search_categories = {}
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if param := _parse_url_param(PartyField.PARENT_TYPE.value, category):
                        search_categories[PartyField.PARENT_TYPE] = param.upper().split(',')
                    elif param := _parse_url_param(PartyField.PARENT_STATE.value, category):
                        search_categories[PartyField.PARENT_STATE] = param.upper().split(',')
                    elif param := _parse_url_param(PartyField.PARTY_ROLE.value, category):
                        search_categories[PartyField.PARTY_ROLE] = param.lower().split(',')

        # validate party roles
        party_roles = search_categories.get(PartyField.PARTY_ROLE)
        if not party_roles:
            return jsonify(
                {'message': f"Expected url param 'categories={PartyField.PARTY_ROLE.value}:...'."}
            ), HTTPStatus.BAD_REQUEST

        if [x for x in party_roles if x.lower() not in ['partner', 'proprietor']]:
            return jsonify({'message': f"Expected '{PartyField.PARTY_ROLE.value}:' with values 'partner' and/or " +
                                       "'proprietor'. Other partyRoles are not implemented."}), HTTPStatus.BAD_REQUEST

        start = None
        rows = None
        try:
            with suppress(TypeError):  # suprress int cast over None
                start = int(request.args.get('start', None))
                rows = int(request.args.get('rows', None))
        except ValueError:  # catch invalid start/row entry
            return {'message': "Expected integer for params: 'start', 'rows'"}, HTTPStatus.BAD_REQUEST

        # params = SearchParams(query, start, rows, legal_types, states, party_roles)
        params = QueryParams(query=query,
                             start=start,
                             rows=rows,
                             categories=search_categories,
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
                        PartyField.PARENT_TYPE.value: search_categories.get(PartyField.PARENT_TYPE, ''),
                        PartyField.PARENT_STATE.value: search_categories.get(PartyField.PARENT_STATE, ''),
                        PartyField.PARTY_ROLE.value: search_categories.get(PartyField.PARTY_ROLE, '')},
                    'rows': rows or business_solr.default_rows,
                    'start': start or 0},
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
