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
"""Helper methods for country/region data."""
import pycountry
from flask import current_app


def get_country(country_code: str):
    """Return the country from the 2 digit country code."""
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if not country:
            # attempt to get it with fuzzy search. If no matches it will throw a lookup error
            country = pycountry.countries.search_fuzzy(country_code)[0]
        return country

    except (LookupError, AttributeError) as err:
        # Conversion to pycountry name failed. Log error for ops and continue.
        current_app.logger.warn("Error converting country %s", country_code)
        current_app.logger.warn(err)
        return None


def get_region(region_code: str, country_code: str):
    """Return the region from the 2 digit region and country codes."""
    try:
        region = pycountry.subdivisions.get(code=f"{country_code}-{region_code.upper()}")
        if not region:
            # attempt to get it with lookup. This will only return a set if there is more than one match
            region = pycountry.subdivisions.lookup(region_code)
            if isinstance(region, set):
                region = next(iter(region))
            if not region.get("country_code", None) or region.country_code != country_code:
                raise LookupError(f"Region ({region.name}) did not match country ({country_code})")
        return region

    except (LookupError, AttributeError) as err:
        # Conversion to pycountry name failed. Log error for ops and continue.
        current_app.logger.warn(
            "Error converting region and country. Region: %s, Country: %s", region_code, country_code
        )
        current_app.logger.warn(err)
        return None
