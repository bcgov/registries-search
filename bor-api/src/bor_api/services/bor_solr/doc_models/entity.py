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

    id: str  # business identifier or person identifier
    entityAddresses: list[Address]
    entityType: str  # person or business
    legalName: str
    bn: str = None  # bn9 for people, bn15 for businesses
    email: str = None
    identifier: str = None
    legalType: str = None
    roles: list[EntityRole] = None
    state: str = None
    # significant individual stuff
    alternateName: str = None
    birthDate: str = None  # YYYY-MM-DD
    deathDate: str = None  # YYYY-MM-DD
    externalInfluence: str = None  # enum (either influences another or is influenced by another)
    isPermanentResident: bool = None
    nationalities: list[str] = None
    taxNumber: str = None
    taxResidencies: list[str] = None
    name_q: str = None

    def __post_init__(self):
        """Set extra field to support name filtering."""
        self.name_q = f'{self.legalName} {self.alternateName}' if self.alternateName else self.legalName
