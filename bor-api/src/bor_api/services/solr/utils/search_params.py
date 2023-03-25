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
"""BOR solr search params."""
from dataclasses import dataclass

from bor_api.services.solr.bor_solr_fields import SolrField as Field


@dataclass
class SearchParams:  # pylint: disable=too-few-public-methods
    """Class definition of search params."""

    query: dict[str, str]
    rows: int
    start: int
    categories: dict[Field, list[str]]
    child_query: dict[str, str]
    child_categories: dict[Field, list[str]]
    child_date_ranges: dict[Field, str]
