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
"""Business search methods."""
from search_api.services.base_solr.utils import QueryParams

from .add_category_filters import add_category_filters
from .. import BusinessSolr
from ..doc_fields import BusinessField


def business_search(params: QueryParams, solr: BusinessSolr):
    """Return the list of businesses from Solr that match the query."""
    # initialize payload with base doc query (init query / filter)
    initial_queries = solr.query_builder.build_base_query(
        query=params.query,
        fields=params.query_fields,
        boost_fields=params.query_boost_fields,
        fuzzy_fields=params.query_fuzzy_fields)
    # boosts for term order result ordering
    initial_queries['query'] += f' OR ({BusinessField.NAME_Q.value}:"{params.query["value"]}"~5^5)'
    initial_queries['query'] += f' OR ({BusinessField.NAME_STEM_AGRO.value}:"{params.query["value"]}"~10^3)'
    initial_queries['query'] += f' OR ({BusinessField.NAME_STEM_AGRO.value}:"{params.query["value"].split()[0]}"^2)'

    # add defaults
    solr_payload = {
        **initial_queries,
        'queries': {
            'parents': f'{BusinessField.IDENTIFIER.value}:*',
            'parentFilters': ' AND '.join(initial_queries['filter'])},
        'facet': {
            **solr.query_builder.build_facet(BusinessField.STATE, False),
            **solr.query_builder.build_facet(BusinessField.TYPE, False)
        },
        'fields': params.fields
    }
    # base doc faceted filters
    add_category_filters(solr_payload=solr_payload,
                         categories=params.categories,
                         is_nested=False,
                         solr=solr)
    # child filter queries
    if child_query := solr.query_builder.build_child_query(params.child_query):
        solr_payload['filter'].append(child_query)
    # child doc faceted filter queries
    add_category_filters(solr_payload=solr_payload,
                         categories=params.child_categories,
                         is_nested=True,
                         solr=solr)
    print(solr_payload)
    return solr.query(solr_payload, params.start, params.rows)
