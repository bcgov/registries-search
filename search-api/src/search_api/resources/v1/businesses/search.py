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
"""API endpoints for Search Suggester."""
import re
from contextlib import suppress
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
from search_api.request_handlers import business_search, business_suggest, parties_search
from search_api.request_handlers.search import SearchParams
from search_api.services import search_solr
from search_api.services.solr import Solr
from search_api.services.solr.solr_fields import SolrField
import search_api.resources.utils as resource_utils


bp = Blueprint('SEARCH', __name__, url_prefix='/search')  # pylint: disable=invalid-name


def _clean_request_args(query: str) -> str:
    """Put backslash on expected param values that start with ':'."""
    expected_params = [
        SolrField.NAME.value, SolrField.IDENTIFIER.value, SolrField.BN.value,
        SolrField.PARTY_NAME.value, SolrField.PARENT_NAME.value, SolrField.PARENT_IDENTIFIER.value,
        SolrField.PARENT_BN.value]
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
        query_items = query.split('::')
        if not query_items:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        value = ''
        name = ''
        identifier = ''
        bn = ''  # pylint: disable=invalid-name
        for item in query_items:
            with suppress(AttributeError):
                if param := _parse_url_param('value', item):
                    value = param
                elif param := _parse_url_param(SolrField.NAME.value, item):
                    name = param
                elif param := _parse_url_param(SolrField.IDENTIFIER.value, item):
                    identifier = param
                elif param := _parse_url_param(SolrField.BN.value, item):
                    bn = param  # pylint: disable=invalid-name
        if not value:
            return jsonify({'message': "Expected url param 'query' to have 'value:<string>'."}), HTTPStatus.BAD_REQUEST
        # clean query values
        query = {
            'value': Solr.prep_query_str(value),
            SolrField.NAME_SINGLE.value: Solr.prep_query_str(name),
            SolrField.IDENTIFIER_Q.value: Solr.prep_query_str(identifier),
            SolrField.BN_Q.value: Solr.prep_query_str(bn)
        }
        # parse category params
        legal_types = None
        states = None
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if param := _parse_url_param(SolrField.TYPE.value, category):
                        legal_types = param.split(',')
                    elif param := _parse_url_param(SolrField.STATE.value, category):
                        states = param.split(',')

        # TODO: validate legal_type + state
        # TODO: add parties filter
        # parse paging params
        start = None
        rows = None
        try:
            with suppress(TypeError):  # suprress int cast over None
                start = int(request.args.get('start', None))
                rows = int(request.args.get('rows', None))
        except ValueError:  # catch invalid start/row entry
            return {'message': "Expected integer for params: 'start', 'rows'"}, HTTPStatus.BAD_REQUEST

        # create solr search params obj from parsed params
        params = SearchParams(query, start, rows, legal_types, states)
        # execute search
        results = business_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'rows': rows or search_solr.default_rows,
                    'query': {
                        'value': query['value'],
                        SolrField.NAME.value: query[SolrField.NAME_SINGLE.value] or '',
                        SolrField.IDENTIFIER.value: query[SolrField.IDENTIFIER_Q.value] or '',
                        SolrField.BN.value: query[SolrField.BN_Q.value] or ''
                    },
                    'categories': {
                        SolrField.TYPE.value: legal_types or '',
                        SolrField.STATE.value: states or ''},
                    'start': results.get('response', {}).get('start')},
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


@bp.get('/parties')
@cross_origin(origin='*')
def parties():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Return a list of business/parties results from solr based from the given query."""
    try:
        query = _clean_request_args(request.args.get('query', ''))
        query_items = query.split('::')
        if not query_items:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        value = ''
        party_name = ''
        parent_name = ''
        parent_identifier = ''
        parent_bn = ''
        for item in query_items:
            with suppress(AttributeError):
                if param := _parse_url_param('value', item):
                    value = param
                elif param := _parse_url_param(SolrField.PARTY_NAME.value, item):
                    party_name = param
                elif param := _parse_url_param(SolrField.PARENT_NAME.value, item):
                    parent_name = param
                elif param := _parse_url_param(SolrField.PARENT_IDENTIFIER.value, item):
                    parent_identifier = param
                elif param := _parse_url_param(SolrField.PARENT_BN.value, item):
                    parent_bn = param
        if not value:
            return jsonify({'message': "Expected url param 'query' to have 'value:<string>'."}), HTTPStatus.BAD_REQUEST
        # clean query values
        query = {
            'value': Solr.prep_query_str(value),
            SolrField.PARTY_NAME_SINGLE.value: Solr.prep_query_str(party_name),
            SolrField.PARENT_NAME_SINGLE.value: Solr.prep_query_str(parent_name),
            SolrField.PARENT_IDENTIFIER_Q.value: Solr.prep_query_str(parent_identifier),
            SolrField.PARENT_BN_Q.value: Solr.prep_query_str(parent_bn)
        }

        # TODO: validate legal_type + state
        legal_types = None
        states = None
        party_roles = None
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if param := _parse_url_param(SolrField.PARENT_TYPE.value, category):
                        legal_types = param.split(',')
                    elif param := _parse_url_param(SolrField.PARENT_STATE.value, category):
                        states = param.split(',')
                    elif param := _parse_url_param(SolrField.PARTY_ROLE.value, category):
                        party_roles = param.lower().split(',')

        # validate party roles
        if not party_roles:
            return jsonify(
                {'message': f"Expected url param 'categories={SolrField.PARTY_ROLE.value}:...'."}
            ), HTTPStatus.BAD_REQUEST
        if [x for x in party_roles if x.lower() not in ['partner', 'proprietor']]:
            return jsonify({'message': f"Expected '{SolrField.PARTY_ROLE.value}:' with values 'partner' and/or " +
                                       "'proprietor'. Other partyRoles are not implemented."}), HTTPStatus.BAD_REQUEST

        start = None
        rows = None
        try:
            with suppress(TypeError):  # suprress int cast over None
                start = int(request.args.get('start', None))
                rows = int(request.args.get('rows', None))
        except ValueError:  # catch invalid start/row entry
            return {'message': "Expected integer for params: 'start', 'rows'"}, HTTPStatus.BAD_REQUEST

        params = SearchParams(query, start, rows, legal_types, states, party_roles)
        results = parties_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'rows': rows or search_solr.default_rows,
                    'query': {
                        'value': query['value'],
                        SolrField.PARTY_NAME.value: query[SolrField.PARTY_NAME_SINGLE.value] or '',
                        SolrField.PARENT_NAME.value: query[SolrField.PARENT_NAME_SINGLE.value] or '',
                        SolrField.PARENT_IDENTIFIER.value: query[SolrField.PARENT_IDENTIFIER_Q.value] or '',
                        SolrField.PARENT_BN.value: query[SolrField.PARENT_BN_Q.value] or ''
                    },
                    'categories': {
                        SolrField.PARENT_TYPE.value: legal_types or '',
                        SolrField.PARENT_STATE.value: states or '',
                        SolrField.PARTY_ROLE.value: party_roles or ''},
                    'start': results.get('response', {}).get('start')},
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


@bp.get('/suggest')
@cross_origin(origin='*')
def suggest():
    """Return a list of suggestions from solr based from the given query."""
    try:
        query = request.args.get('query', None)
        if not query:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        query = Solr.prep_query_str(query)

        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('rows', None))

        highlight = bool(request.args.get('highlight', False))

        suggestions = business_suggest(query, highlight, rows)
        return jsonify({'queryInfo': {'rows': rows, 'highlight': highlight, 'query': query},
                        'results': suggestions}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
