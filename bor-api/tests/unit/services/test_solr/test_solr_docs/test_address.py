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
"""Tests to ensure that the Address Solr Doc works as expected."""
from dataclasses import asdict

import pytest

from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.solr_docs import Address


@pytest.mark.parametrize('test_name,a_type,a_city,a_country,a_region,street,p_code', [
    ('test_1', 'DELIVERY', 'North Vancouver', 'CA', 'BC', 'Test Street', 'V0N1G0'),
])
def test_address_doc(test_name, a_type, a_city, a_country, a_region, street, p_code):
    """Assert the Address solr doc class works as expected."""
    address = Address(
        addressType=a_type,
        addressCity=a_city,
        addressCountry=a_country,
        addressRegion=a_region,
        postalCode=p_code,
        streetAddress=street
    )
    assert address

    assert address.address_q
    assert address.addressCity in address.address_q
    assert address.addressCountry in address.address_q
    assert address.addressRegion in address.address_q
    assert address.postalCode in address.address_q
    assert address.streetAddress in address.address_q

    json = asdict(address)
    assert json
    assert json.get(Field.ADDRESS_CITY.value) == a_city
    assert json.get(Field.ADDRESS_COUNTRY.value) == a_country
    assert json.get(Field.ADDRESS_REGION.value) == a_region
    assert json.get(Field.POSTAL_CODE.value) == p_code
    assert json.get(Field.STREET_ADDRESS.value) == street


@pytest.mark.parametrize('test_name,a_type,a_city,a_country,a_region,street,p_code', [
    ('test_1', 'DELIVERY', 'North Vancouver', 'CA', 'BC', 'Test Street', 'V0N1G0'),
])
def test_address_doc_invalid(test_name, a_type, a_city, a_country, a_region, street, p_code):
    """Assert the Address solr doc class does not initialize when required fields are missing."""
    # type
    with pytest.raises(TypeError):
        Address(
            addressCity=a_city,
            addressCountry=a_country,
            addressRegion=a_region,
            postalCode=p_code,
            streetAddress=street
        )
    # city
    with pytest.raises(TypeError):
        Address(
            addressType=a_type,
            addressCountry=a_country,
            addressRegion=a_region,
            postalCode=p_code,
            streetAddress=street
        )
    # country
    with pytest.raises(TypeError):
        Address(
            addressType=a_type,
            addressCity=a_city,
            addressRegion=a_region,
            postalCode=p_code,
            streetAddress=street
        )
    # address region
    with pytest.raises(TypeError):
        Address(
            addressType=a_type,
            addressCity=a_city,
            addressCountry=a_country,
            postalCode=p_code,
            streetAddress=street
        )
    # postal code
    with pytest.raises(TypeError):
        Address(
            addressType=a_type,
            addressCity=a_city,
            addressCountry=a_country,
            addressRegion=a_region,
            streetAddress=street
        )
    # street
    with pytest.raises(TypeError):
        Address(
            addressType=a_type,
            addressCity=a_city,
            addressCountry=a_country,
            addressRegion=a_region,
            postalCode=p_code
        )
