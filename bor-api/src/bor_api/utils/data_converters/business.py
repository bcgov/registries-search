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
"""Data conversion methods for business."""
import re

from bor_api.services.bor_solr.doc_models import Entity

from . import get_lear_addresses


def needs_bc_prefix(identifier: str, legal_type: str) -> bool:
    """Return if the identifier should have the BC prefix or not."""
    numbers_only_rgx = r"^[0-9]+$"
    # TODO: get legal types from shared enum
    return legal_type in ["BEN", "BC", "CC", "ULC"] and re.search(numbers_only_rgx, identifier)


def get_lear_business(business_info: dict) -> Entity:
    """Return the business from LEAR format as an Entity doc."""
    identifier = business_info["identifier"]
    if needs_bc_prefix(identifier, business_info["legalType"]):
        # set prefix to BC
        identifier = f"BC{identifier}"

    business_addresses = None
    if addresses := business_info.get("addresses"):
        business_addresses = get_lear_addresses(addresses, "UNKNOWN")

    return Entity(
        entityAddresses=business_addresses,
        entityType="BUSINESS",
        id=identifier,
        identifier=identifier,
        legalName=business_info["legalName"],
        legalType=business_info["legalType"],
        state=business_info["state"],
        bn=business_info.get("taxId"),
        email=business_info.get("email"),
    )
