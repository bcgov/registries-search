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

    # base entity doc stored fields
    BN = 'bn'
    ENTITY_ADDRESSES = 'entityAddresses'
    ENTITY_TYPE = 'entityType'
    IDENTIFIER = 'identifier'
    LEGAL_TYPE = 'legalType'
    NAMES = 'names'
    PARTIES = 'parties'
    ROLES = 'roles'
    STATE = 'state'
    # entity doc query fields
    BN_Q = 'bn_q'
    IDENTIFIER_Q = 'identifier_q'

    # name doc stored fields
    NAME = 'name'
    NAME_BN = 'nameBn'
    NAME_TYPE = 'nameType'
    # name doc query fields
    NAME_Q = 'name_q'
    NAME_AGRO_Q = 'name_agro_q'
    NAME_SINGLE_Q = 'name_single_q'

    # entity role doc stored fields
    ACTIVE = 'active'
    ACTIVE_DATES = 'activeDates'
    ROLE_ADDRESSES = 'roleAddresses'
    ROLE_ENTITY = 'roleEntity'
    ROLE_TYPE = 'roleType'

    # address doc stored/query fields
    ADDRESS_TYPE = 'addressType'
    CITY = 'city'
    COUNTRY = 'country'
    POSTAL_CODE = 'postalCode'
    PROVINCE = 'province'
    STREET = 'street'
    # address doc query fields
    ADDRESS_Q = 'address_q'

    # shared built in fields
    SCORE = 'score'
