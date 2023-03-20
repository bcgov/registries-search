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
import re
from typing import Dict

from bor_api.services import bor_solr as solr
from bor_api.services.solr import Solr
from bor_api.services.solr.bor_solr_search_params import SearchParams
from bor_api.services.solr.bor_solr_fields import SolrField as Field


def entities_search(params: SearchParams):
    """Return the list of businesses from Solr that match the query."""
    # facets
    query_params = {
        'facet': 'on',
        'json.facet': solr.base_facets,
        'fl': solr.entity_fields
    }

    # add names query
    query_params['q'] = Solr.build_child_query(params.query[Field.NAME.value],
                                               Field.NAMES,
                                               [Field.NAME_Q, Field.NAME_AGRO_Q],
                                               Field.NAME_SINGLE_Q)
    # add names fields / filter
    terms = query_params['q'].split()
    name_filter = f'"{Field.NAME_SINGLE.value}:{terms[0]}'
    for term in terms[1:]:
        name_filter += f' AND {Field.NAME_SINGLE.value}:{term}'
    name_filter += '"'
    query_params['fl'] += ',' + solr.entity_nest_fields.format(filter=name_filter)

    # filter queries -- uncomment and add to this when using entity filters
    # filter_q = ''
    # if params.legal_types:
    #     filter_q = '(' + Solr.build_filter_query(Field.TYPE.value, [x.upper() for x in params.legal_types])
    # if params.states:
    #     filter_str = Solr.build_filter_query(Field.STATE.value, [x.upper() for x in params.states])
    #     filter_q = filter_q + ' AND ' + filter_str if filter_q else '(' + filter_str

    # filter_q = filter_q + ')' if filter_q else ''
    # if filter_q:
    #     if query_params.get('fq'):
    #         query_params['fq'] += ' AND ' + filter_q
    #     else:
    #         query_params['fq'] = filter_q
    # boosts for result ordering -- need to test and see if this works with child queries
    query_params['defType'] = 'edismax'
    query_params['bq'] = f'{Field.NAME_Q.value}:("{params.query[Field.NAME.value]}"~10)^30.0' + \
        f' AND {Field.NAME_AGRO_Q.value}:("{params.query[Field.NAME.value]}"~10)^20.0' + \
        f' AND {Field.NAME_Q.value}:({params.query[Field.NAME.value].split()[0]}*)^5.0'

    return solr.query(query_params, params.start, params.rows)


def parse_facets(facet_data: Dict) -> Dict:
    """Return formatted solr facet response data."""
    facet_info = facet_data.get('facets', {})
    facets = {}
    for category in facet_info:
        if category == 'count':
            continue
        facets[category] = []
        for item in facet_info[category]['buckets']:
            facets[category].append({'value': item['val'], 'count': item['count']})

    return {'fields': facets}


def prep_query_str(query: str) -> str:
    """Return query string prepped for solr call."""
    # replace solr specific special chars
    rmv_spec_chars_rgx = r'([\[\]!()\"~*?:/\\={}^%`#|<>,.@$;_\-])'
    handled_spec_chars_rgx = r'([&+]+)'
    query = re.sub(rmv_spec_chars_rgx, ' ', query.lower())
    return re.sub(handled_spec_chars_rgx, r' \\\1 ', query) if not query.isspace() else r'\*'
