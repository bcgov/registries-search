# Copyright © 2024 Province of British Columbia
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
"""Manages solr dataclasses for search solr docs."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PartyDoc:
    """Class representation for a solr business doc."""

    id: str
    parentLegalType: str
    parentIdentifier: str
    parentName: str
    parentStatus: str
    partyName: str
    partyRoles: List[str]
    partyType: str
    parentBN: Optional[str] = None
