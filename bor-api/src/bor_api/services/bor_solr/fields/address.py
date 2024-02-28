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
"""Manages address doc fields for BOR solr."""
from bor_api.enums.base import BaseEnum


class AddressField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the address fields available in the BOR solr search core."""

    # unique key for all docs
    UNIQUE_KEY = 'id'
    # address doc stored fields
    ADDRESS_TYPE = 'addressType'
    ADDRESS_CITY = 'addressCity'
    ADDRESS_COUNTRY = 'addressCountry'
    ADDRESS_REGION = 'addressRegion'
    LOCATION_DESC = 'locationDescription'
    POSTAL_CODE = 'postalCode'
    STREET_ADDRESS = 'streetAddress'
    STREET_ADDITIONAL = 'streetAdditional'
    # address doc query fields
    ADDRESS_Q = 'address_q'
    ADDRESS_SYN_Q = 'address_synonym_q'
    # common built in across docs
    SCORE = 'score'
