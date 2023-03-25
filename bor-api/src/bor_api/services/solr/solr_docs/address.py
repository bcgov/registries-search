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
"""Manages dataclass for the solr address doc."""
from dataclasses import dataclass


@dataclass
class Address:
    """Class representation for a solr address doc."""

    addressType: str
    addressCity: str
    addressCountry: str
    addressRegion: str
    streetAddress: str
    postalCode: str
    address_q: str = None

    def __post_init__(self):
        """Set extra solr address search fields dependent on base fields."""
        self.address_q = f'{self.streetAddress} {self.addressCity} ' + \
            f'{self.addressRegion} {self.addressCountry} {self.postalCode}'
