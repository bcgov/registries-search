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
import csv
import os

import pycountry

from bor_api.enums import SolrSynonymType


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
                synonyms[synonym] = list(set(synonyms.setdefault(synonym, []) + region_synonym_list))

    return synonyms


def _get_name_synonyms() -> dict[str, list[str]]:
    """Return all name synonyms provided in the nickname.csv."""
    synonyms_by_id = {}
    path = os.path.dirname(__file__)
    abs_file_path = os.path.join(path, 'data/nicknames.csv')
    with open(file=abs_file_path, encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for item in reader:
            name = item['name'].lower().strip()
            synonym_id = item['name_id']
            synonyms_by_id[synonym_id] = list(set(synonyms_by_id.setdefault(synonym_id, []) + [name]))

    synonyms = {}
    for syn_id, syn_list in synonyms_by_id.items():  # pylint: disable=unused-variable
        # add all name synonym mappings to each other
        for synonym in syn_list:
            synonyms[synonym] = list(set(synonyms.setdefault(synonym, []) + syn_list))
    return synonyms


def get_synonyms() -> dict[SolrSynonymType, dict[str, list[str]]]:
    """Return all synonyms used for SOLR queries."""
    address_synonyms = _get_address_synonyms()
    name_synonyms = _get_name_synonyms()
    # NB: will want this for business names only
    # add address synonyms to name_synonyms (combine lists where necessary)
    # for addr_syn, addr_syn_list in address_synonyms.items():
    #     if addr_syn in name_synonyms:
    #         # combine synonym list
    #         name_synonyms[addr_syn] = list(set(name_synonyms[addr_syn] + addr_syn_list))
    #     else:
    #         name_synonyms[addr_syn] = addr_syn_list

    return {
        SolrSynonymType.ADDRESS: address_synonyms,
        SolrSynonymType.NAME: name_synonyms
    }
