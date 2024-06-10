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
"""Tests to ensure that the search field groups return as expected."""
import pytest

from bor_api.enums import SearchAccessLevel
from bor_api.services.bor_solr.fields import EntityField, EntityRoleField
from bor_api.services.bor_solr.utils import get_search_field_group


@pytest.mark.parametrize('test_name,access,expected', [
    ('test_public', SearchAccessLevel.PUBLIC, ['birthDate', 'entityType', 'legalName', 'nationalities', 'roles', 'score', '[child]', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleType', 'relatedLegalType']),
    ('test_limited', SearchAccessLevel.LIMITED, ['birthDate', 'entityType', 'legalName', 'nationalities', 'roles', 'score', '[child]', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleType', 'relatedLegalType', 'entityAddresses', 'relatedEmail', 'roleDates', 'addressCity', 'addressCountry', 'addressRegion', 'addressType', 'postalCode', 'streetAddress', 'streetAdditional', 'locationDescription', 'active', 'start', 'end']),
    ('test_extended', SearchAccessLevel.EXTENDED, ['birthDate', 'entityType', 'legalName', 'nationalities', 'roles', 'score', '[child]', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleType', 'relatedLegalType', 'entityAddresses', 'relatedEmail', 'roleDates', 'addressCity', 'addressCountry', 'addressRegion', 'addressType', 'postalCode', 'streetAddress', 'streetAdditional', 'locationDescription', 'active', 'start', 'end', 'alternateName', 'email', 'isPermanentResident', 'externalInfluence', 'phoneNumber', 'taxNumber', 'taxResidencies', 'relatedAddresses', 'relatedInterests', 'details', 'directOrIndirect', 'otherReason', 'sharesExact', 'sharesMax', 'sharesMin', 'interestType', 'relatedParties', 'interestPartyID', 'interestPartyName'])
])
def test_get_search_field_group(test_name, access, expected):
    """Assert the get_search_field_group method works as expected."""
    fields = get_search_field_group(access)
    assert fields == expected


@pytest.mark.parametrize('test_name,excluded_field', [
    ('test_public_no_tax_number', EntityField.TAX_NUMBER.value),
    ('test_public_no_tax_residencies', EntityField.TAX_RESIDENCIES.value),
    ('test_public_no_addresses', EntityField.ENTITY_ADDRESSES.value),
    ('test_public_no_email', EntityField.EMAIL.value),
    ('test_public_no_alternate_name', EntityField.ALT_NAME.value),
    ('test_public_no_business_email', EntityRoleField.RELATED_EMAIL.value),
    ('test_public_no_business_address', EntityRoleField.RELATED_ADDRESSES.value),
    ('test_public_no_interests', EntityRoleField.RELATED_INTERESTS.value),
    ('test_public_no_dates', EntityRoleField.ROLE_DATES.value)
])
def test_field_exclusion_public(test_name, excluded_field):
    """Assert the get_search_field_group does not return specific important fields for public access."""
    fields = get_search_field_group(SearchAccessLevel.PUBLIC)
    assert excluded_field not in fields


@pytest.mark.parametrize('test_name,excluded_field', [
    ('test_limited_no_tax_number', EntityField.TAX_NUMBER.value),
    ('test_limited_no_tax_residencies', EntityField.TAX_RESIDENCIES.value),
    ('test_limited_no_email', EntityField.EMAIL.value),
    ('test_limited_no_alternate_name', EntityField.ALT_NAME.value),
    ('test_limited_no_business_address', EntityRoleField.RELATED_ADDRESSES.value),
    ('test_limited_no_interests', EntityRoleField.RELATED_INTERESTS.value)
])
def test_field_exclusion_limited(test_name, excluded_field):
    """Assert the get_search_field_group does not return specific important fields for limited access."""
    fields = get_search_field_group(SearchAccessLevel.LIMITED)
    assert excluded_field not in fields
