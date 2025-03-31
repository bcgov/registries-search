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


def get_lear_addresses(addresses: list[dict[str, str]], address_type_default: str) -> list[Address]:
    """Return the list of addresses from LEAR format as a list of Address docs."""
    address_docs: list[Address] = []
    for address in addresses:
        address_docs.append(
            Address(
                addressType=address.get("addressType", address_type_default).upper(),
                addressCity=address.get("addressCity") or None,
                addressCountry=address.get("addressCountry") or None,
                addressRegion=address.get("addressRegion") or None,
                postalCode=address.get("postalCode") or None,
                streetAddress=address.get("streetAddress") or None,
                streetAdditional=address.get("streetAddressAdditional") or None,
                locationDescription=address.get("deliveryInstructions") or None,
            )
        )
    return address_docs


def get_btr_address(address_info: dict[str, str], address_type_default: str) -> Address:
    """Return the address from BTR format as an Address doc."""
    return Address(
        addressType=address_info.get("type", address_type_default).upper(),
        addressCity=address_info.get("city") or None,
        addressCountry=address_info.get("country") or None,
        addressRegion=address_info.get("region") or None,
        postalCode=address_info.get("postalCode") or None,
        streetAddress=address_info.get("street") or None,
        streetAdditional=address_info.get("streetAdditional") or None,
        locationDescription=address_info.get("locationDescription") or None,
    )
