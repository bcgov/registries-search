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
"""API request handlers for Search."""
from typing import Dict, List

from search_api.services import search_solr
from search_api.services.solr import Solr
from search_api.services.solr.solr_fields import SolrField


class SearchParams:  # pylint: disable=too-few-public-methods
    """Class definition of search params."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 query: Dict[str, str],
                 start: int,
                 rows: int,
                 legal_types: List[str] = None,
                 states: List[str] = None,
                 party_roles: List[str] = None):
        """Init instance."""
        self.query = query
        self.start = start
        self.rows = rows
        self.legal_types = legal_types
        self.states = states
        self.party_roles = party_roles


def business_search(params: SearchParams):
    """Return the list of businesses from Solr that match the query."""
    # build base query
    solr_query_params = Solr.build_split_query(
        params.query,
        [
            SolrField.NAME_Q.value,
            SolrField.NAME_STEM_AGRO.value,
            SolrField.IDENTIFIER_Q.value,
            SolrField.BN_Q.value
        ],
        [SolrField.NAME_Q.value]
    )
    # TODO: add nested parties query
    # NB: keeping for future: build a query based on child values and return parent doc
    # child_query = Solr.build_child_query(query,
    #                                     SolrField.PARTIES,
    #                                     [SolrField.PARTY_NAME_Q,SolrField.PARTY_NAME_STEM_AGRO],
    #                                     SolrField.PARTY_NAME_SINGLE)
    # terms = query.split()
    # child_filter = f'"{SolrField.PARTY_NAME_SINGLE}:{terms[0]}'
    # for term in terms[1:]:
    #     child_filter += f' AND {SolrField.PARTY_NAME_SINGLE}:{term}'
    # child_filter += '"'
    # child_query += solr.nest_fields_party.format(filter=child_filter)

    # facets
    solr_query_params['facet'] = 'on'
    solr_query_params['json.facet'] = search_solr.base_facets
    # filter queries
    filter_q = ''
    if params.legal_types:
        filter_q = '(' + Solr.build_filter_query(SolrField.TYPE.value, [x.upper() for x in params.legal_types])
    if params.states:
        filter_str = Solr.build_filter_query(SolrField.STATE.value, [x.upper() for x in params.states])
        filter_q = filter_q + ' AND ' + filter_str if filter_q else '(' + filter_str

    filter_q = filter_q + ')' if filter_q else ''
    if filter_q:
        if solr_query_params.get('fq'):
            solr_query_params['fq'] += ' AND ' + filter_q
        else:
            solr_query_params['fq'] = filter_q
    # boosts for result ordering
    solr_query_params['defType'] = 'edismax'
    solr_query_params['bq'] = f'{SolrField.NAME_Q.value}:("{params.query["value"]}"~10)^30.0' + \
        f' AND {SolrField.NAME_STEM_AGRO.value}:("{params.query["value"]}"~10)^20.0' + \
        f' AND {SolrField.NAME_Q.value}:({params.query["value"].split()[0]}*)^10.0' + \
        f' AND {SolrField.NAME_SUGGEST.value}:({params.query["value"].split()[0]}*)^5.0'

    solr_query_params['fl'] = search_solr.base_fields
    return search_solr.query(solr_query_params, params.start, params.rows)


def business_suggest(query: str, highlight: bool, rows: int) -> List:
    """Return the list of business suggestions from Solr from given text."""
    if not rows:
        rows = search_solr.default_rows

    # 1st solr query (names)
    name_suggestions = search_solr.suggest(query, rows)

    # 2nd solr query (extra names)
    extra_name_suggestions = []
    if len(name_suggestions) < rows:
        name_select_params = Solr.build_split_query({'value': query}, [SolrField.NAME_SINGLE.value], [])
        name_select_params['fl'] = search_solr.base_fields
        name_docs = search_solr.query(name_select_params, rows).get('response', {}).get('docs', [])
        extra_name_suggestions = [x.get(SolrField.NAME.value).upper() for x in name_docs if x.get(SolrField.NAME.value)]
    # remove dups
    name_suggestions = name_suggestions + list(set(extra_name_suggestions) - set(name_suggestions))
    query = query.upper()  # NOTE: needed for bn/identifier processing too
    # highlight
    if highlight:
        name_suggestions = Solr.highlight_names(query, name_suggestions)

    # 3rd solr query (bns + identifiers)
    identifier_suggestions = []
    bn_suggestions = []
    if len(name_suggestions) < rows:
        bn_id_params = {
            'q': f'{SolrField.IDENTIFIER_Q.value}:{query} OR {SolrField.BN_Q.value}:{query}',
            'fl': search_solr.base_fields}
        bn_id_docs = search_solr.query(bn_id_params, 0, rows).get('response', {}).get('docs', [])
        if highlight:
            # return list of identifier strings with highlighted query
            identifier_suggestions = [
                x.get(SolrField.IDENTIFIER.value).replace(query, f'<b>{query}</b>')
                for x in bn_id_docs if query in x.get(SolrField.IDENTIFIER.value)]
            # return list of bn strings with highlighted query
            bn_suggestions = [
                x.get(SolrField.BN.value).replace(query, f'<b>{query}</b>')
                for x in bn_id_docs if x.get(SolrField.BN.value) and query in x.get(SolrField.BN.value, '')]
        else:
            identifier_suggestions = [
                x.get(SolrField.IDENTIFIER.value) for x in bn_id_docs if query in x.get(SolrField.IDENTIFIER.value)]
            bn_suggestions = [
                x.get(SolrField.BN.value) for x in bn_id_docs
                if x.get(SolrField.BN.value) and query in x.get(SolrField.BN.value, '')]

    # format/combine response
    suggestions = [{'type': SolrField.NAME.value, 'value': x} for x in name_suggestions]
    suggestions += [{'type': SolrField.IDENTIFIER.value, 'value': x} for x in identifier_suggestions]
    suggestions += [{'type': SolrField.BN.value, 'value': x} for x in bn_suggestions]
    return suggestions[:rows]


def parties_search(params: SearchParams):
    """Return the list of parties from Solr that match the query."""
    # build base query
    solr_query_params = Solr.build_split_query(params.query,
                                               [SolrField.PARTY_NAME_Q.value, SolrField.PARTY_NAME_STEM_AGRO.value],
                                               [SolrField.PARTY_NAME_Q.value, SolrField.PARENT_NAME_Q.value])
    # facets
    solr_query_params['facet'] = 'on'
    solr_query_params['json.facet'] = search_solr.party_facets
    # filters
    filter_q = ''
    if params.party_roles:
        filter_q = '(' + Solr.build_filter_query(SolrField.PARTY_ROLE.value, [x.lower() for x in params.party_roles])
    if params.legal_types:
        filter_str = Solr.build_filter_query(SolrField.PARENT_TYPE.value, [x.upper() for x in params.legal_types])
        filter_q = filter_q + ' AND ' + filter_str if filter_q else '(' + filter_str
    if params.states:
        filter_str = Solr.build_filter_query(SolrField.PARENT_STATE.value, [x.upper() for x in params.states])
        filter_q = filter_q + ' AND ' + filter_str if filter_q else '(' + filter_str

    filter_q = filter_q + ')' if filter_q else ''
    if filter_q:
        if solr_query_params.get('fq'):
            solr_query_params['fq'] += ' AND ' + filter_q
        else:
            solr_query_params['fq'] = filter_q

    # boosts for result ordering
    solr_query_params['defType'] = 'edismax'
    solr_query_params['bq'] = f'{SolrField.PARTY_NAME_Q.value}:("{params.query["value"]}"~10)^30.0' + \
        f' AND {SolrField.PARTY_NAME_STEM_AGRO.value}:("{params.query["value"]}"~10)^20.0' + \
        f' AND {SolrField.PARTY_NAME_Q.value}:({params.query["value"].split()[0]}*)^10.0' + \
        f' AND {SolrField.PARTY_NAME_SUGGEST.value}:({params.query["value"].split()[0]}*)^5.0'

    solr_query_params['fl'] = search_solr.party_fields

    return search_solr.query(solr_query_params, params.start, params.rows)
