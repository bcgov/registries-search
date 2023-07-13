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
"""Manages dataclass for the solr entity role doc."""
from dataclasses import dataclass

from .date_range import DateRange


@dataclass
class EntityRole:
    """Class representation for a solr entity role doc."""

    relatedEntityType: str
    relatedIdentifier: str
    relatedLegalType: str
    relatedName: str
    relatedState: str
    roleDates: list[DateRange]
    roleType: str  # i.e. director, partner, beneficial owner, incorporator, etc.
    relatedBN: str = None
    relatedEmail: str = None
    related_q: str = None

    def __post_init__(self):
        """Set extra solr role search fields dependent on base fields."""
        self.related_q = f"{self.relatedName} {self.relatedIdentifier} {self.relatedBN or ''}".strip()
