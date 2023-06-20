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
"""Manages common solr synonym payload build methods."""
import pycountry


def _get_address_synonyms() -> dict[str, list[str]]:
    """Return all address synonyms based on pycountry countries/regions."""
    synonyms = {}
    for country in list(pycountry.countries):
        # synonym list = 2 letter, 3 letter, full desc, and full desc no spaces for query logic
        country_synonym_list = [country.alpha_2.lower(), country.alpha_3.lower(), country.name.lower()]
        # each one needs its own mapping to the others
        for synonym in country_synonym_list:
            synonyms[synonym] = synonyms.setdefault(synonym, []) + country_synonym_list

    for region in list(pycountry.subdivisions):
        region_short = region.code.replace(f'{region.country_code}-', '').lower()
        try:
            int(region_short)
            # skip number short forms
            continue
        except ValueError:
            # add to synonyms
            region_synonym_list = [region_short, region.name.lower()]
            # each one needs its own mapping to the others
            for synonym in region_synonym_list:
                synonyms[synonym] = synonyms.setdefault(synonym, []) + region_synonym_list

    return synonyms


def get_synonyms() -> dict[str, list[str]]:
    """Return all synonyms used for SOLR queries."""
    return {
        **_get_address_synonyms(),
        # FUTURE: add name synonyms here
    }
