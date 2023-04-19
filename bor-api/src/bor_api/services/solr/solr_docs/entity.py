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
"""Manages dataclass for the solr entity doc."""
from dataclasses import dataclass

from .address import Address
from .entity_role import EntityRole


@dataclass
class Entity:
    """Class representation for a solr entity doc."""

    entityAddresses: list[Address]
    entityType: str  # person or business
    identifier: str  # business identifier or person identifier (COLIN<party id> / LEAR<party id>)
    legalName: str
    # aliases: EntityName = None
    bn: str = None  # bn9 for people, bn15 for businesses
    bnSP: str = None  # interim for SPs, future: will be in aliases
    identifier_q: str = None
    legalType: str = None
    operatingName: str = None  # interim for SPs, future: will be in aliases
    roles: list[EntityRole] = None
    state: str = None

    def __post_init__(self):
        """Set identifier query field for business entities.

        Needed here because identifier is the unique key in all docs (addresses,roles,etc.),
        so it can't be copied over via the index copyfields without adding in unwanted data.
        """
        if self.entityType.lower() == 'business':
            self.identifier_q = self.identifier
