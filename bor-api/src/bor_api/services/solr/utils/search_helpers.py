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
"""BOR solr search functions."""
from bor_api.services import bor_solr as solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field

from .query_builders import (PRE_CHILD_FILTER_CLAUSE, build_child_query,
                             build_facet, build_facet_query, build_base_query)
from .search_params import SearchParams


def _add_category_filters(solr_payload: dict, categories: dict[Field, list[str]], is_nested: bool):
    """Attach filter queries for categories to the params."""
    for category in categories:
        if category_filters := categories[category]:
            filter_str = build_facet_query(category, category_filters, is_nested)
            solr_payload['filter'].append(filter_str)


def entities_search(params: SearchParams):
    """Return the list of businesses from Solr that match the query."""
    # initialize payload with base doc query (init query / filter)
    initial_queries = build_base_query(
        query=params.query,
        fields=[Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q, Field.LEGAL_NAME_SINGLE_Q,
                Field.IDENTIFIER_Q, Field.BN_Q],
        nested_fields=[Field.ADDRESS_Q],
        boost_fields={
            Field.LEGAL_NAME_Q: 2,
            Field.LEGAL_NAME_AGRO_Q: 2,
            Field.LEGAL_NAME_SINGLE_Q: 2,
            Field.BN_Q: 2
        },
        fuzzy_fields={
            Field.LEGAL_NAME_Q: {'short': 1, 'long': 2},
            Field.LEGAL_NAME_AGRO_Q: {'short': 1, 'long': 2},
            Field.LEGAL_NAME_SINGLE_Q: {'short': 1, 'long': 2},
            Field.BN_Q: {'short': 1, 'long': 1},
            Field.ADDRESS_Q: {'short': 1, 'long': 1},
        },
        synonym_fields={
            Field.LEGAL_NAME_SYN_Q: 'parent',
            Field.ADDRESS_SYN_Q: 'child'
        })

    # boosts for term order result ordering
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_Q.value}:"{params.query["value"]}"~5^5)'
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_AGRO_Q.value}:"{params.query["value"]}"~10^3)'
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_SYN_Q.value}:"{params.query["value"]}"~10^3)'
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_AGRO_Q.value}:"{params.query["value"].split()[0]}"^2)'

    # add defaults
    solr_payload = {
        **initial_queries,
        'queries': {
            'parents': f'{Field.ENTITY_TYPE.value}:*',
            'parentFilters': ' AND '.join(initial_queries['filter'])},
        'facet': {
            # facets entity
            **build_facet(Field.ENTITY_TYPE, False),
            **build_facet(Field.LEGAL_TYPE, False),
            **build_facet(Field.STATE, False),
            # facets roles
            **build_facet(Field.RELATED_ENTITY_TYPE, True),
            **build_facet(Field.RELATED_LEGAL_TYPE, True),
            **build_facet(Field.RELATED_STATE, True),
            **build_facet(Field.ROLE_TYPE, True)
        },
        'fields': solr.entity_fields + solr.address_fields + solr.entity_role_fields + solr.date_fields
    }

    # base doc faceted filters
    _add_category_filters(solr_payload=solr_payload, categories=params.categories, is_nested=False)

    # child filter queries
    if child_query := build_child_query(params.child_query):
        solr_payload['filter'].append(child_query)

    # child doc faceted filter queries
    _add_category_filters(solr_payload=solr_payload, categories=params.child_categories, is_nested=True)

    # child doc date range filter queries
    if params.child_date_ranges:
        # get params
        start_date = params.child_date_ranges[Field.START]
        end_date = params.child_date_ranges[Field.END]
        # set filters for start / end overlapp
        # start is before end date OR None AND end is after start date OR active (end date is None)
        start_qry = f'({Field.START.value}:[* TO {end_date}] OR ({Field.ACTIVE.value}:* AND NOT {Field.START.value}:*))'
        end_qry = f'({Field.END.value}:[{start_date} TO *] OR ({Field.ACTIVE.value}:* AND NOT end:*))'
        # put it together
        date_filter = f'{PRE_CHILD_FILTER_CLAUSE}{start_qry} AND {end_qry}'
        solr_payload['filter'].append(date_filter)

    return solr.query(solr_payload, params.start, params.rows)
