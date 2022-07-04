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
from typing import List

from search_api.services import solr
from search_api.services.solr import Solr, SolrField


class SearchParams:  # pylint: disable=too-few-public-methods
    """Class definition of search params."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 query: str,
                 start: int,
                 rows: int,
                 legal_type: str = None,
                 state: str = None,
                 party_roles: List[str] = None):
        """Init instance."""
        self.query = query
        self.start = start
        self.rows = rows
        self.legal_type = legal_type
        self.state = state
        self.party_roles = party_roles


def business_search(params: SearchParams):
    """Return the list of businesses from Solr that match the query."""
    # build base query
    solr_query = Solr.build_split_query(
        params.query,
        [
            SolrField.NAME_Q,
            SolrField.NAME_STEM_AGRO,
            SolrField.IDENTIFIER_Q,
            SolrField.BN_Q
        ],
        [SolrField.NAME_Q]
    )
    # TODO: add nested parties query
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
    solr_query += solr.base_facets
    # filters
    if params.legal_type:
        solr_query += f'&{SolrField.TYPE}:{params.legal_type.upper()}'
    if params.state:
        solr_query += f'&{SolrField.STATE}:{params.state.upper()}'

    # boosts for result ordering
    solr_bq_params = f'&bq={SolrField.NAME_Q}:("{params.query}"~10)^30.0' + \
        f' AND {SolrField.NAME_STEM_AGRO}:("{params.query}"~10)^20.0' + \
        f' AND {SolrField.NAME_Q}:({params.query.split()[0]}*)^10.0' + \
        f' AND {SolrField.NAME_SUGGEST}:({params.query.split()[0]}*)^5.0'
    solr_query += solr.boost_params.format(boost_params=solr_bq_params)

    return solr.query(solr_query, solr.base_fields, params.start, params.rows)


def business_suggest(query: str, highlight: bool, rows: int) -> List:
    """Return the list of business suggestions from Solr from given text."""
    if not rows:
        rows = solr.default_rows

    # 1st solr query (names)
    name_suggestions = solr.suggest(query, rows)

    # 2nd solr query (extra names)
    extra_name_suggestions = []
    if len(name_suggestions) < rows:
        name_select_params = Solr.build_split_query(query, [SolrField.NAME_SINGLE], [])
        name_docs = solr.query(name_select_params, solr.base_fields, 0, rows).get('response', {}).get('docs', [])
        extra_name_suggestions = [x.get(SolrField.NAME, '').upper() for x in name_docs]
    # remove dups
    name_suggestions = name_suggestions + list(set(extra_name_suggestions) - set(name_suggestions))
    # highlight
    if highlight:
        name_suggestions = Solr.highlight_names(query.upper(), name_suggestions)

    # 3rd solr query (bns + identifiers)
    identifier_suggestions = []
    bn_suggestions = []
    if len(name_suggestions) < rows:
        bn_id_params = f'q={SolrField.IDENTIFIER_Q}:{query} OR {SolrField.BN_Q}:{query}'
        bn_id_docs = solr.query(bn_id_params, solr.base_fields, 0, rows).get('response', {}).get('docs', [])
        # return list of identifier strings with highlighted query
        identifier_suggestions = [
            x.get(SolrField.IDENTIFIER).replace(query, f'<b>{query}</b>')
            for x in bn_id_docs if query in x.get(SolrField.IDENTIFIER)]
        # return list of bn strings with highlighted query
        bn_suggestions = [
            x.get(SolrField.BN).replace(query, f'<b>{query}</b>')
            for x in bn_id_docs if query in x.get(SolrField.BN, '')]

    # format/combine response
    suggestions = [{'type': SolrField.NAME, 'value': x} for x in name_suggestions]
    suggestions += [{'type': SolrField.IDENTIFIER, 'value': x} for x in identifier_suggestions]
    suggestions += [{'type': SolrField.BN, 'value': x} for x in bn_suggestions]
    return suggestions[:rows]


def parties_search(params: SearchParams):
    """Return the list of parties from Solr that match the query."""
    # build base query
    solr_query = Solr.build_split_query(params.query,
                                        [SolrField.PARTY_NAME_Q, SolrField.PARTY_NAME_STEM_AGRO],
                                        [SolrField.PARTY_NAME_Q])
    # facets
    solr_query += solr.party_facets
    # filters
    if params.party_roles:
        role_filter = f'&fq={SolrField.PARTY_ROLE}:("{params.party_roles[0]}"'
        for role in params.party_roles[1:]:
            role_filter += f' OR "{role.lower()}"'
        solr_query += role_filter + ')'
    if params.legal_type:
        solr_query += f'&{SolrField.PARENT_TYPE}:{params.legal_type.upper()}'
    if params.state:
        solr_query += f'&{SolrField.PARENT_STATE}:{params.state.upper()}'

    # boosts for result ordering
    solr_bq_params = f'&bq={SolrField.PARTY_NAME_Q}:("{params.query}"~10)^30.0' + \
        f' AND {SolrField.PARTY_NAME_STEM_AGRO}:("{params.query}"~10)^20.0' + \
        f' AND {SolrField.PARTY_NAME_Q}:({params.query.split()[0]}*)^10.0' + \
        f' AND {SolrField.PARTY_NAME_SUGGEST}:({params.query.split()[0]}*)^5.0'
    solr_query += solr.boost_params.format(boost_params=solr_bq_params)

    return solr.query(solr_query, solr.party_fields, params.start, params.rows)
