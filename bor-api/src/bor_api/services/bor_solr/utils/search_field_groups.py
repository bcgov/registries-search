# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Manages Solr field groupings for a search."""
from bor_api.enums import SearchAccessLevel
from bor_api.services.bor_solr.fields import (
    AddressField,
    DateRangeField,
    EntityField,
    EntityRoleField,
    InterestField,
    InterestPartyField,
)

ENTITY_PUBLIC: list[str] = [
    EntityField.BIRTH_DATE.value,
    EntityField.ENTITY_TYPE.value,
    EntityField.LEGAL_NAME.value,
    EntityField.NATIONALITIES.value,
    EntityField.ROLES.value,
    EntityField.SCORE.value,
    "[child]",
]
ENTITY_LIMITED: list[str] = [EntityField.ENTITY_ADDRESSES.value]
ENTITY_EXTENDED: list[str] = [
    EntityField.ALT_NAME.value,
    EntityField.EMAIL.value,
    EntityField.IS_PR.value,
    EntityField.EXTERNAL_INFLUENCE.value,
    EntityField.PHONE_NUMBER.value,
    EntityField.TAX_NUMBER.value,
    EntityField.TAX_RESIDENCIES.value,
]

ROLE_PUBLIC: list[str] = [
    EntityRoleField.RELATED_BN.value,
    EntityRoleField.RELATED_ENTITY_TYPE.value,
    EntityRoleField.RELATED_IDENTIFIER.value,
    EntityRoleField.RELATED_NAME.value,
    EntityRoleField.RELATED_STATE.value,
    EntityRoleField.ROLE_TYPE.value,
    EntityRoleField.RELATED_LEGAL_TYPE.value,
]
ROLE_LIMITED: list[str] = [EntityRoleField.RELATED_EMAIL.value, EntityRoleField.ROLE_DATES.value]
ROLE_EXTENDED: list[str] = [EntityRoleField.RELATED_ADDRESSES.value, EntityRoleField.RELATED_INTERESTS.value]

ADDRESS: list[str] = [
    AddressField.ADDRESS_CITY.value,
    AddressField.ADDRESS_COUNTRY.value,
    AddressField.ADDRESS_REGION.value,
    AddressField.ADDRESS_TYPE.value,
    AddressField.POSTAL_CODE.value,
    AddressField.STREET_ADDRESS.value,
    AddressField.STREET_ADDITIONAL.value,
    AddressField.LOCATION_DESC.value,
]
DATE_RANGE: list[str] = [DateRangeField.ACTIVE.value, DateRangeField.START.value, DateRangeField.END.value]
INTEREST: list[str] = [
    InterestField.DETAILS.value,
    InterestField.DIRECT_INDIRECT.value,
    InterestField.OTHER_REASON.value,
    InterestField.SHARE_EXACT.value,
    InterestField.SHARE_MAX.value,
    InterestField.SHARE_MIN.value,
    InterestField.TYPE.value,
    InterestField.RELATED_PARTIES.value,
]
INTEREST_PARTY: list[str] = [InterestPartyField.UUID.value, InterestPartyField.NAME.value]


def get_search_field_group(access_level: SearchAccessLevel) -> list[str]:
    """Return the search field grouping for the given access level."""
    if access_level == SearchAccessLevel.PUBLIC:
        return ENTITY_PUBLIC + ROLE_PUBLIC

    if access_level == SearchAccessLevel.LIMITED:
        return ENTITY_PUBLIC + ROLE_PUBLIC + ENTITY_LIMITED + ROLE_LIMITED + ADDRESS + DATE_RANGE

    if access_level == SearchAccessLevel.EXTENDED:
        return (
            ENTITY_PUBLIC
            + ROLE_PUBLIC
            + ENTITY_LIMITED
            + ROLE_LIMITED
            + ADDRESS
            + DATE_RANGE
            + ENTITY_EXTENDED
            + ROLE_EXTENDED
            + INTEREST
            + INTEREST_PARTY
        )

    return []
