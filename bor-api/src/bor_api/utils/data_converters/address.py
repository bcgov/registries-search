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
"""Data conversion methods for address."""
from bor_api.services.bor_solr.doc_models import Address


def get_lear_address(address_info: dict, address_type: str) -> Address:
    """Return the address from LEAR format as an Address doc."""
    return Address(addressType=address_info.get('addressType') or address_type,
                   addressCity=address_info.get('addressCity', '') or '',
                   addressCountry=address_info.get('addressCountry', '') or '',
                   addressRegion=address_info.get('addressRegion', '') or '',
                   postalCode=address_info.get('postalCode', '') or '',
                   streetAddress=address_info.get('streetAddress', '') or '')


def get_btr_address(address_info: dict, address_type: str) -> Address:
    """Return the address from BTR format as an Address doc."""
    return Address(addressType=address_info.get('type') or address_type,
                   addressCity=address_info.get('city', '') or '',
                   addressCountry='',  # TODO: update this once btr address is fixed
                   addressRegion=address_info.get('region', '') or '',
                   postalCode=address_info.get('postalCode', '') or '',
                   streetAddress=address_info.get('street', '') or '',
                   streetAdditional=address_info.get('streetAdditional', '') or '',
                   locationDescription=address_info.get('locationDescription', '') or '')
