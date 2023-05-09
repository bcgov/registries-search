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
            # build_method = build_child_facet_query if child else build_facet_query
            filter_str = build_facet_query(category, [x.upper() for x in category_filters], is_nested)
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
            Field.IDENTIFIER_Q: 2,
            Field.BN_Q: 2
        },
        fuzzy_fields={
            Field.LEGAL_NAME_Q: 2,
            Field.LEGAL_NAME_AGRO_Q: 2,
            Field.LEGAL_NAME_SINGLE_Q: 2,
            Field.IDENTIFIER_Q: 1,
            Field.BN_Q: 1,
            Field.ADDRESS_Q: 1
        })

    # boosts for term order result ordering
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_Q.value}:"{params.query["value"]}"~5^5)'
    initial_queries['query'] += f' OR ({Field.LEGAL_NAME_AGRO_Q.value}:"{params.query["value"]}"~10^3)'
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
        start_clause = f'{Field.START.value}:[{start_date} TO {end_date}]'
        end_clause = f'{Field.END.value}:[{start_date} TO {end_date}]'
        # put it together
        date_filter = f'{PRE_CHILD_FILTER_CLAUSE}{start_clause} OR {end_clause}'
        if end_date == '*':
            # current dirs with no end date need the active filter
            date_filter += f' OR {Field.ACTIVE.value}: true'
        solr_payload['filter'].append(date_filter)

    return solr.query(solr_payload, params.start, params.rows)
