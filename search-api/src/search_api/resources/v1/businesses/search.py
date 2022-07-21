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
from contextlib import suppress
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
from search_api.request_handlers import business_search, business_suggest, parties_search
from search_api.request_handlers.search import SearchParams
from search_api.services import solr
from search_api.services.solr import Solr, SolrField
import search_api.resources.utils as resource_utils


bp = Blueprint('SEARCH', __name__, url_prefix='/search')  # pylint: disable=invalid-name


@bp.get('/facets')
@cross_origin(origin='*')
def facets():
    """Return a list of business results from solr based from the given query."""
    try:
        query = request.args.get('query', None)
        if not query:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        query = Solr.prep_query_str(query)
        # TODO: validate legal_type + state
        legal_types = None
        states = None
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if SolrField.TYPE in category:
                        legal_types = category.replace(f'{SolrField.TYPE}:', '').split(',')
                    elif SolrField.STATE in category:
                        states = category.replace(f'{SolrField.STATE}:', '').split(',')
        # TODO: add parties filter

        start = None
        with suppress(TypeError):
            start = int(request.args.get('start', None))
        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('rows', None))

        params = SearchParams(query, start, rows, legal_types, states)
        results = business_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'rows': rows or solr.default_rows,
                    'query': query,
                    'categories': {
                        SolrField.TYPE: legal_types or '',
                        SolrField.STATE: states or ''},
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
def parties():
    """Return a list of business/parties results from solr based from the given query."""
    try:
        query = request.args.get('query', None)
        if not query:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        query = Solr.prep_query_str(query)

        party_roles = None
        with suppress(AttributeError):
            party_roles = (request.args.get(SolrField.PARTY_ROLE, None)).split(',')

        # TODO: validate legal_type + state
        legal_types = None
        states = None
        party_roles = None
        if categories := request.args.get('categories', '').split('::'):
            for category in categories:
                with suppress(AttributeError):
                    if SolrField.PARENT_TYPE in category:
                        legal_types = category.replace(f'{SolrField.PARENT_TYPE}:', '').split(',')
                    elif SolrField.PARENT_STATE in category:
                        states = category.replace(f'{SolrField.PARENT_STATE}:', '').split(',')
                    elif SolrField.PARTY_ROLE in category:
                        party_roles = category.replace(f'{SolrField.PARTY_ROLE}:', '').split(',')

        # validate party roles
        if not party_roles:
            return jsonify(
                {'message': f"Expected url param 'categories={SolrField.PARTY_ROLE}:...'."}), HTTPStatus.BAD_REQUEST
        if [x for x in party_roles if x not in ['partner', 'proprietor']]:
            return jsonify({'message': f"Expected '{SolrField.PARTY_ROLE}:' with values 'partner' and/or " +
                                       "'proprietor'. Other partyRoles are not implemented."}), HTTPStatus.BAD_REQUEST

        start = None
        with suppress(TypeError):
            start = int(request.args.get('start', None))
        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('rows', None))

        params = SearchParams(query, start, rows, legal_types, states, party_roles)
        results = parties_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'rows': rows or solr.default_rows,
                    'query': query,
                    'categories': {
                        SolrField.PARENT_TYPE: legal_types or '',
                        SolrField.PARENT_STATE: states or '',
                        SolrField.PARTY_ROLE: party_roles or ''},
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
