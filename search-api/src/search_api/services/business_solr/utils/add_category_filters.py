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
"""Category filter methods."""
from .. import BusinessSolr
from ..doc_fields import BusinessField


def add_category_filters(solr_payload: dict,
                         categories: dict[BusinessField, list[str]],
                         is_nested: bool,
                         solr: BusinessSolr):
    """Attach filter queries for categories to the params."""
    for category in categories:
        if category_filters := categories[category]:
            filter_str = solr.query_builder.build_facet_query(category, category_filters, is_nested)
            solr_payload['filter'].append(filter_str)
