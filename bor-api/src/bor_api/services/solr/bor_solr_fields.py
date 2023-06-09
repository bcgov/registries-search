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
"""Manages solr fields for search solr."""
from bor_api.enums.base import BaseEnum


class SolrField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the fields available in the solr search core."""

    # unique key for all docs
    UNIQUE_KEY = 'id'

    # base entity doc stored fields
    BN = 'bn'
    BN_SP = 'bnSP'
    ENTITY_ADDRESSES = 'entityAddresses'
    ENTITY_TYPE = 'entityType'
    IDENTIFIER = 'identifier'
    LEGAL_NAME = 'legalName'
    LEGAL_TYPE = 'legalType'
    OPERATING_NAME = 'operatingName'
    ROLES = 'roles'
    STATE = 'state'
    # entity doc query fields
    BN_Q = 'bn_q'
    BN_SP_Q = 'bnSP_q'
    IDENTIFIER_Q = 'identifier_q'
    LEGAL_NAME_Q = 'legalName_q'
    LEGAL_NAME_AGRO_Q = 'legalName_agro_q'
    LEGAL_NAME_SINGLE_Q = 'legalName_single_term'
    OPERATING_NAME_Q = 'operatingName'
    OPERATING_NAME_AGRO_Q = 'operatingName_agro_q'
    OPERATING_NAME_SINGLE_Q = 'operatingName_single_term'

    # entity role doc stored fields
    ACTIVE = 'active'
    RELATED_BN = 'relatedBN'
    RELATED_ENTITY_TYPE = 'relatedEntityType'
    RELATED_IDENTIFIER = 'relatedIdentifier'
    RELATED_LEGAL_TYPE = 'relatedLegalType'
    RELATED_NAME = 'relatedName'
    RELATED_STATE = 'relatedState'
    ROLE_DATES = 'roleDates'
    ROLE_TYPE = 'roleType'
    # entity role doc query fields
    RELATED_BN_Q = 'relatedBN_q'
    RELATED_IDENTIFIER_Q = 'relatedIdentifier_q'
    RELATED_NAME_Q = 'relatedName_q'
    RELATED_NAME_AGRO_Q = 'relatedName_agro_q'
    RELATED_NAME_SINGLE_Q = 'relatedName_single_term'
    RELATED_Q = 'related_q'

    # address doc stored/query fields
    ADDRESS_TYPE = 'addressType'
    ADDRESS_CITY = 'addressCity'
    ADDRESS_COUNTRY = 'addressCountry'
    ADDRESS_REGION = 'addressRegion'
    POSTAL_CODE = 'postalCode'
    STREET_ADDRESS = 'streetAddress'
    # address doc query fields
    ADDRESS_Q = 'address_q'
    POSTAL_CODE_Q = 'postalCode_q'

    # date range fields
    START = 'start'
    END = 'end'

    # shared built in fields
    SCORE = 'score'
