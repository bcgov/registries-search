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
from typing import List

from flask import current_app, jsonify, request, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
from search_api.services import solr
from search_api.services.solr import Solr, SolrField
import search_api.resources.utils as resource_utils

bp = Blueprint('SEARCH', __name__, url_prefix='/search')  # pylint: disable=invalid-name


@bp.get('/facets')
@cross_origin(origin='*')
def facets():
    """Return a list of results from solr based from the given query."""
    try:
        query = request.args.get('query', None)
        if not query:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST
        
        # TODO: validate legal_type + state
        legal_type = request.args.get('legal_type', None)
        state = request.args.get('state', None)

        start = None
        with suppress(Exception):
            start = int(request.args.get('start_row', None))
        rows = None
        with suppress(Exception):
            rows = int(request.args.get('num_of_rows', None))

        results = _business_search(query, legal_type, state, start, rows)
        response = {
            'facets': Solr.parse_facets(results),
            'searchResults': {'queryInfo':{
                'num_of_rows': rows or solr.default_rows,
                'query': query,
                'start_row': results.get('response', {}).get('start'),
                'total_rows': results.get('response', {}).get('numFound')}
            },
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
        with suppress(Exception):
            rows = int(request.args.get('max_results', None))

        suggestions = _business_suggest(query, rows)
        return jsonify({'results': suggestions}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


def _business_search(query: str, legal_type: str, state: str, start: int, rows: int):
    """Return the list of businesses from Solr that match the query."""
    if not start:
        start = solr.default_start
    if not rows:
        rows = solr.default_rows
    
    # base query
    solr_query = Solr.build_split_query(
        query,
        [
            SolrField.NAME_SELECT,
            SolrField.NAME_STEM_AGRO,
            SolrField.NAME_SYNONYM,
            SolrField.IDENTIFIER_SELECT,
            SolrField.BN_SELECT
        ],
        [SolrField.NAME_SELECT]
    )
    
    # facets
    solr_query += solr.facets
    if legal_type:
        solr_query += f'&{SolrField.TYPE}:{legal_type.upper()}'
    if state:
        solr_query += f'&{SolrField.STATE}:{state.upper()}'
    
    # boosts for result ordering
    solr_bq_params = f'&bq={SolrField.NAME_SELECT}:("{query}"~10)^30.0' + \
        f'&bq={SolrField.NAME_STEM_AGRO}:("{query}"~10)^20.0' + \
        f'&bq={SolrField.NAME_SELECT}:({query.split()[0]}*)^10.0'
    solr_query += solr.bq.format(boost_params=solr_bq_params)
    
    try:
        results = solr.select(solr_query, start, rows)
    except SolrException as err:
        current_app.logger.debug(f'1st solr call attempt failed with {err.with_traceback(None)}')
        terms = query.split()
        for term in terms:
            solr_query.replace(f' OR {SolrField.NAME_SYNONYM}:{term}', '')
        current_app.logger.debug('Trying again without synonym clause...')
        results = solr.select(solr_query, start, rows)
    
    return results
    


def _business_suggest(query: str, rows: int = None) -> List:
    """Return the list of business suggestions from Solr from given text."""
    if not rows:
        rows = solr.default_rows
    # 1st solr query (names)
    name_suggestions = solr.suggest(query, rows)

    # 2nd solr query (extra names)
    extra_name_suggestions = []
    if len(name_suggestions) < rows:
        name_select_params = Solr.build_split_query(query, SolrField.NAME_SINGLE)
        name_docs = solr.select(name_select_params, 0, rows).get('response', {}).get('docs')
        extra_name_suggestions = [x.get(SolrField.NAME, '').upper() for x in name_docs]
    # remove dups
    name_suggestions = name_suggestions + list(set(extra_name_suggestions) - set(name_suggestions))
    # highlight
    name_suggestions = Solr.highlight_names(query.upper(), name_suggestions)

    # 3rd solr query (bns + identifiers)
    identifier_suggestions = []
    bn_suggestions = []
    if len(name_suggestions) < rows:
        bn_id_params = f'q={SolrField.IDENTIFIER_SELECT}:{query} OR {SolrField.BN_SELECT}:{query}'
        bn_id_docs = solr.select(bn_id_params, 0, rows).get('response', {}).get('docs')
        # return list of identifier strings with highlighted query
        identifier_suggestions = [
            x.get(SolrField.IDENTIFIER).replace(query, f'<b>{query}</b>')
            for x in bn_id_docs if query in x.get(SolrField.IDENTIFIER)]
        # return list of bn strings with highlighted query
        bn_suggestions = [
            x.get(SolrField.BN).replace(query, f'<b>{query}</b>')
            for x in bn_id_docs if query in x.get(SolrField.BN, '')]

    # format/combine response
    suggestions = [{'type': 'name', 'value': x} for x in name_suggestions]
    suggestions += [{'type': 'identifier', 'value': x} for x in identifier_suggestions]
    suggestions += [{'type': 'bn', 'value': x} for x in bn_suggestions]
    return suggestions[:rows]
