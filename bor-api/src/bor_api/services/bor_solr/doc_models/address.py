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

import pycountry
from flask import current_app


@dataclass
class Address:
    """Class representation for a solr address doc."""

    addressType: str
    addressCity: str
    addressCountry: str
    addressRegion: str
    streetAddress: str
    postalCode: str
    location_description: str = None
    address_q: str = None

    def __post_init__(self):
        """Set extra solr address search fields dependent on base fields."""
        region_name = None
        try:
            # attempt to set country with pycountry name
            if self.addressCountry:
                # attempt to get country by 2 digit code
                country = pycountry.countries.get(alpha_2=self.addressCountry)
                if not country:
                    # attempt to get it with fuzzy search. If no matches it will throw a lookup error
                    country = pycountry.countries.search_fuzzy(self.addressCountry)[0]

                # set country name from pycountry
                self.addressCountry = country.name

                # attempt to set region with pycountry name
                if self.addressRegion:
                    region = pycountry.subdivisions.get(code=f'{country.alpha_2}-{self.addressRegion.upper()}')
                    if not region:
                        # attempt to get it with lookup. This will only return a set if there is more than one match
                        region = pycountry.subdivisions.lookup(self.addressRegion)
                        if isinstance(region, set):
                            region = list(region)[0]
                        if not region.get('country_code', None) or region.country_code != country.alpha_2:
                            raise LookupError(f'Region ({region.name}) did not match country ({country.name})')
                    # set region name from pycountry
                    region_name = region.name
        except (LookupError, AttributeError) as err:
            # Conversion to pycountry name failed. Log error for ops and continue.
            current_app.logger.warn('Error converting region and country. Region: %s, Country: %s',
                                    self.addressRegion,
                                    self.addressCountry)
            current_app.logger.warn(err)

        self.address_q = f"{self.streetAddress or ''} {self.addressCity or ''} " + \
            f"{region_name or self.addressRegion or ''} {self.addressCountry or ''} {self.postalCode or ''}" \
            f" {self.location_description or ''}".replace('  ', ' ').strip()
