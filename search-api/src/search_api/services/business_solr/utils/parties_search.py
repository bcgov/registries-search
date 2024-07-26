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
"""Person search methods."""
from search_api.services.base_solr.utils import QueryParams

from .add_category_filters import add_category_filters
from .. import BusinessSolr
from ..doc_fields import PartyField


def parties_search(params: QueryParams, solr: BusinessSolr):
    """Return the list of parties from Solr that match the query."""
    # initialize payload with base doc query (init query / filter)
    initial_queries = solr.query_builder.build_base_query(
        query=params.query,
        fields=params.query_fields,
        boost_fields=params.query_boost_fields,
        fuzzy_fields=params.query_fuzzy_fields)
    # boosts for term order result ordering
    initial_queries['query'] += f' OR ({PartyField.PARTY_NAME_Q.value}:"{params.query["value"]}"~5^5)'
    initial_queries['query'] += f' OR ({PartyField.PARTY_NAME_STEM_AGRO.value}:"{params.query["value"]}"~10^3)'
    initial_queries['query'] += f' OR ({PartyField.PARTY_NAME_STEM_AGRO.value}:"{params.query["value"].split()[0]}"^2)'

    # add defaults
    solr_payload = {
        **initial_queries,
        'queries': {
            'parents': f'{PartyField.PARTY_NAME_Q.value}:*',
            'parentFilters': ' AND '.join(initial_queries['filter'])
        },
        'facet': {
            **solr.query_builder.build_facet(PartyField.PARENT_TYPE, False),
            **solr.query_builder.build_facet(PartyField.PARENT_STATE, False),
            **solr.query_builder.build_facet(PartyField.PARTY_ROLE, False)
        },
        'fields': params.fields
    }
    # base doc faceted filters
    add_category_filters(solr_payload=solr_payload,
                         categories=params.categories,
                         is_nested=False,
                         solr=solr)
    print(solr_payload)
    return solr.query(solr_payload, params.start, params.rows)
