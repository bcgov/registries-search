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

        # TODO: validate legal_type + state
        legal_type = request.args.get(SolrField.TYPE, None)
        state = request.args.get(SolrField.STATE, None)
        # TODO: add parties filter

        start = None
        with suppress(TypeError):
            start = int(request.args.get('start_row', None))
        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('num_of_rows', None))

        params = SearchParams(query, start, rows, legal_type, state)
        results = business_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {'queryInfo': {
                'num_of_rows': rows or solr.default_rows,
                'query': query,
                'start_row': results.get('response', {}).get('start'),
                'total_rows': results.get('response', {}).get('numFound')}},
            'results': results.get('response', {}).get('docs')}

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

        party_roles = None
        with suppress(AttributeError):
            party_roles = (request.args.get('roles', None)).split(',')
        if not party_roles:
            return jsonify({'message': "Expected url param 'roles'."}), HTTPStatus.BAD_REQUEST
        if [x for x in party_roles if x not in ['partner', 'proprietor']]:
            return jsonify(
                {'message': "Expected url param 'roles' to be 'partner' and/or 'proprietor'."}
            ), HTTPStatus.BAD_REQUEST

        # TODO: validate legal_type + state
        legal_type = request.args.get(SolrField.TYPE, None)
        state = request.args.get(SolrField.STATE, None)
        start = None
        with suppress(TypeError):
            start = int(request.args.get('start_row', None))
        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('num_of_rows', None))

        params = SearchParams(query, start, rows, legal_type, state, party_roles)
        results = parties_search(params)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {'queryInfo': {
                'num_of_rows': rows or solr.default_rows,
                'query': query,
                'start_row': results.get('response', {}).get('start'),
                'total_rows': results.get('response', {}).get('numFound')}},
            'results': results.get('response', {}).get('docs')}

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

        rows = None
        with suppress(TypeError):
            rows = int(request.args.get('max_results', None))

        highlight = bool(request.args.get('highlight', False))

        suggestions = business_suggest(query, highlight, rows)
        return jsonify({'results': suggestions}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
