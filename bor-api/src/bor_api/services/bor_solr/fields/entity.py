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
"""Manages entity doc fields for BOR solr."""
from bor_api.enums.base import BaseEnum


class EntityField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the entity fields available in the BOR solr search core."""

    # unique key for all docs
    UNIQUE_KEY = 'id'
    # entity doc stored fields (base doc)
    ALT_NAME = 'alternateName'
    BIRTH_DATE = 'birthDate'
    BN = 'bn'
    DEATH_DATE = 'deathDate'
    EMAIL = 'email'
    ENTITY_ADDRESSES = 'entityAddresses'
    ENTITY_TYPE = 'entityType'
    EXTERNAL_INFLUENCE = 'externalInfluence'
    IDENTIFIER = 'identifier'
    IS_PR = 'isPermanentResident'
    LEGAL_NAME = 'legalName'
    LEGAL_TYPE = 'legalType'
    NATIONALITIES = 'nationalities'
    ROLES = 'roles'
    STATE = 'state'
    TAX_NUMBER = 'taxNumber'
    TAX_RESIDENCIES = 'taxResidencies'
    # entity doc query fields
    ALT_NAME_Q = 'alternateName_q'
    ALT_NAME_AGRO_Q = 'alternateName_stem_agro_q'
    ALT_NAME_SINGLE_Q = 'alternateName_single_term_q'
    ALT_NAME_SYN_Q = 'alternateName_synonym_q'
    BN_Q = 'bn_q'
    IDENTIFIER_Q = 'identifier_q'
    TAX_NUMBER_Q = 'taxNumber_q'
    LEGAL_NAME_Q = 'legalName_q'
    LEGAL_NAME_AGRO_Q = 'legalName_stem_agro_q'
    LEGAL_NAME_SINGLE_Q = 'legalName_single_term_q'
    LEGAL_NAME_SYN_Q = 'legalName_synonym_q'
    # common built in across docs
    SCORE = 'score'
