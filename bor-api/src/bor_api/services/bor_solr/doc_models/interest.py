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
"""Manages dataclass for the solr interest doc."""
from dataclasses import dataclass


@dataclass
class Interest:
    """Class representation for a solr interest doc."""

    type: str = None
    details: str = None
    directOrIndirect: str = None
    externalInfluence: str = None  # enum (either influences another or is influenced by another)
    sharesExact: float = None
    sharesMax: float = None
    sharesMin: float = None
    startDate: str = None
    endDate: str = None
