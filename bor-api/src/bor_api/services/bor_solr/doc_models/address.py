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
"""Manages dataclass for the solr address doc."""
from dataclasses import dataclass

from bor_api.utils.pycountry_helpers import get_country, get_region


@dataclass
class Address:
    """Class representation for a solr address doc."""

    addressType: str
    addressCity: str = None
    addressCountry: str = None
    addressRegion: str = None
    locationDescription: str = None
    postalCode: str = None
    streetAddress: str = None
    streetAdditional: str = None
    address_q: str = None
    parentDoc: str = None  # i.e. entity, entityRole

    def __post_init__(self):
        """Set extra solr address search fields dependent on base fields."""
        region_name = None
        if (self.addressCountry and (country := get_country(self.addressCountry))):
            # attempt to set country by 2 digit code
            self.addressCountry = country.name
            # attempt to set region_name with pycountry name
            if self.addressRegion and (region := get_region(self.addressRegion, country.alpha_2)):
                region_name = region.name

        self.address_q = (
            (
                f"{self.streetAddress or ''} {self.streetAdditional or ''} {self.addressCity or ''} "
                + f"{region_name or self.addressRegion or ''} {self.addressCountry or ''} "
                + f"{self.postalCode or ''} {self.locationDescription or ''}"
            )
            .replace("  ", " ")
            .strip()
        )
