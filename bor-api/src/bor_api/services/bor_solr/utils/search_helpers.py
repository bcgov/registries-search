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
from bor_api.services.bor_solr import BorSolr
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField, InterestField

from .query_builders import (PRE_CHILD_FILTER_CLAUSE, build_child_query,
                             build_facet, build_facet_query, build_base_query)
from .search_params import SearchParams


def _add_category_filters(solr_payload: dict,
                          categories: dict[AddressField | EntityField | EntityRoleField | InterestField, list[str]],
                          is_nested: bool):
    """Attach filter queries for categories to the params."""
    for category in categories:
        if category_filters := categories[category]:
            filter_str = build_facet_query(category, category_filters, is_nested)
            solr_payload['filter'].append(filter_str)


def entities_search(params: SearchParams, solr: BorSolr):
    """Return the list of businesses from Solr that match the query."""
    # initialize payload with base doc query (init query / filter)
    initial_queries = build_base_query(
        query=params.query,
        fields=params.query_fields,
        boost_fields=params.query_boost_fields,
        fuzzy_fields=params.query_fuzzy_fields,
        synonym_fields=params.query_synonym_fields)

    # boosts for term order result ordering
    initial_queries['query'] += f' OR ({EntityField.LEGAL_NAME_Q.value}:"{params.query["value"]}"~5^5)'
    initial_queries['query'] += f' OR ({EntityField.LEGAL_NAME_AGRO_Q.value}:"{params.query["value"]}"~10^3)'
    initial_queries['query'] += f' OR ({EntityField.LEGAL_NAME_SYN_Q.value}:"{params.query["value"]}"~10^3)'
    if params.query['value']:
        initial_queries['query'] += \
            f' OR ({EntityField.LEGAL_NAME_AGRO_Q.value}:"{params.query["value"].split()[0]}"^2)'
    # Only add alternate name boost if it is specified in the query
    if EntityField.ALT_NAME_Q.value in params.query_fields:
        initial_queries['query'] += f' OR ({EntityField.ALT_NAME_Q.value}:"{params.query["value"]}"~5^5)'
        initial_queries['query'] += f' OR ({EntityField.ALT_NAME_AGRO_Q.value}:"{params.query["value"]}"~10^3)'
        initial_queries['query'] += f' OR ({EntityField.ALT_NAME_SYN_Q.value}:"{params.query["value"]}"~10^3)'
        if params.query['value']:
            initial_queries['query'] += \
                f' OR ({EntityField.ALT_NAME_AGRO_Q.value}:"{params.query["value"].split()[0]}"^2)'

    # add defaults
    solr_payload = {
        **initial_queries,
        'queries': {
            'parents': f'{EntityField.ENTITY_TYPE.value}:*',
            'parentFilters': ' AND '.join(initial_queries['filter'])},
        'facet': {
            # facets for roles
            **build_facet(EntityRoleField.RELATED_ENTITY_TYPE, True),
            **build_facet(EntityRoleField.RELATED_LEGAL_TYPE, True),
            **build_facet(EntityRoleField.RELATED_STATE, True),
            **build_facet(EntityRoleField.ROLE_TYPE, True)
        },
        'fields': params.fields
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
        start_date = params.child_date_ranges[DateRangeField.START]
        end_date = params.child_date_ranges[DateRangeField.END]
        # set filters for start / end overlapp
        # start is before end date OR None AND end is after start date OR active (end date is None)
        start_qry = f'({DateRangeField.START.value}:[* TO {end_date}] OR ({DateRangeField.ACTIVE.value}:*' \
            f' AND NOT {DateRangeField.START.value}:*))'
        end_qry = f'({DateRangeField.END.value}:[{start_date} TO *] OR ({DateRangeField.ACTIVE.value}:* AND NOT end:*))'
        # put it together
        date_filter = f'{PRE_CHILD_FILTER_CLAUSE}{start_qry} AND {end_qry}'
        solr_payload['filter'].append(date_filter)

    return solr.query(solr_payload, params.start, params.rows)
