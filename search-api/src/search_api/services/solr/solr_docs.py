# Copyright © 2022 Province of British Columbia
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

    parentLegalType: str
    parentName: str
    parentStatus: str
    partyName: str
    partyRoles: List[str]
    partyType: str
    parentBN: Optional[str] = None


@dataclass
class BusinessDoc:
    """Class representation for a solr business doc."""

    identifier: str
    legalType: str
    name: str
    status: str
    bn: Optional[str] = None
    identifier_q: str = None
    parties: Optional[List[PartyDoc]] = None

    def __post_init__(self):
        """Set identifier_q to the business level identifier.

        It isn't a copy field in solr to avoid including generated party identifiers
        so it must be set explicitly during an update.
        """
        self.identifier_q = self.identifier
