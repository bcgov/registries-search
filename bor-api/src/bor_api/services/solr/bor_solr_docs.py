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
"""Manages solr dataclasses for search solr docs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Address:
    """Class representation for a solr address doc."""

    addressType: str
    city: str
    country: str
    postalCode: str
    province: str
    street: str
    address_q: str = None

    def __post_init__(self):
        """Set extra solr address search fields dependent on base fields."""
        self.address_q = f'{self.street} {self.city} {self.province} {self.country} {self.postalCode}'


@dataclass
class EntityName:
    """Class representation for a solr entity name doc."""

    name: str
    nameType: str  # legal, operating, etc.
    nameBn: Optional[str] = None  # SP alias's have a bn15 associated with it


@dataclass
class EntityRole:
    """Class representation for a solr entity role doc."""

    active: bool
    activeDates: List[str]  # list of solr DateRangeField i.e. ['[2022-03-21 TO 2022-10-05]','[2023-01-01 TO *]']
    roleEntity: Entity
    roleType: str  # i.e. director, partner, beneficial owner, incorporator, etc.
    roleAddresses: Optional[List[Address]] = None


@dataclass
class Entity:
    """Class representation for a solr entity doc."""

    entityAddresses: List[Address]
    entityType: str  # person or business
    names: List[EntityName]
    bn: Optional[str] = None  # bn9 for people, bn15 for businesses
    identifier: str = None
    legalType: Optional[str] = None
    parties: Optional[List[Entity]] = None
    roles: Optional[List[EntityRole]] = None
    state: Optional[str] = None
