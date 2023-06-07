# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=invalid-name
"""Manages dataclass for the solr date range doc."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DateRange:
    """Class representation for a solr date range."""

    start: datetime  # query i.e. ['[2022-03-21 TO 2022-10-05]','[2023-01-01 TO *]']
    end: datetime = None
    active: bool = None

    def __post_init__(self):
        """Set solr date range fields dependent on base fields."""
        self.active = not self.end
