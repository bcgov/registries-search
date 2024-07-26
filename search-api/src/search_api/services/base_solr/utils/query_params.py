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
"""Solr query params."""
from dataclasses import dataclass

from search_api.utils.base import BaseEnum


@dataclass
class QueryParams:  # pylint: disable=too-few-public-methods
    """Class definition of query params."""

    query: dict[str, str]
    rows: int
    start: int
    categories: dict[BaseEnum, list[str]]
    child_query: dict[str, str]
    child_categories: dict[BaseEnum, list[str]]
    child_date_ranges: dict[BaseEnum, str]
    fields: list[str]
    query_fields: dict[BaseEnum, str]
    query_boost_fields: dict[BaseEnum, int]
    query_fuzzy_fields: dict[BaseEnum, dict[str, int]]
