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

from bor_api.services.bor_solr.fields import AddressField
from bor_api.services.bor_solr.doc_models import Address


@pytest.mark.parametrize(
    "test_name,a_type,a_city,a_country,a_region,street,p_code,converted",
    [
        (
            "test_basic_ca_bc",
            "DELIVERY",
            "North Vancouver",
            "CA",
            "BC",
            "Test Street",
            "V0N1G0",
            {"country": "Canada", "region": "British Columbia"},
        ),
        (
            "test_basic_ca_on",
            "DELIVERY",
            "North Vancouver",
            "CA",
            "ON",
            "Test Street",
            "V0N1G0",
            {"country": "Canada", "region": "Ontario"},
        ),
        (
            "test_basic_us_la",
            "DELIVERY",
            "North Vancouver",
            "US",
            "LA",
            "Test Street",
            "V0N1G0",
            {"country": "United States", "region": "Louisiana"},
        ),
        (
            "test_basic_gb_gre",
            "DELIVERY",
            "North Vancouver",
            "GB",
            "GRE",
            "Test Street",
            "V0N1G0",
            {"country": "United Kingdom", "region": "Greenwich"},
        ),
        (
            "test_full_country_desc",
            "DELIVERY",
            "North Vancouver",
            "canada",
            "BC",
            "Test Street",
            "V0N1G0",
            {"country": "Canada", "region": "British Columbia"},
        ),
        (
            "test_no_country",
            "DELIVERY",
            "North Vancouver",
            None,
            "BC",
            "Test Street",
            "V0N1G0",
            {"country": None, "region": "BC"},
        ),
        (
            "test_no_region",
            "DELIVERY",
            "North Vancouver",
            "CA",
            None,
            "Test Street",
            "V0N1G0",
            {"country": "Canada", "region": None},
        ),
        (
            "test_no_country_region",
            "DELIVERY",
            "North Vancouver",
            None,
            None,
            "Test Street",
            "V0N1G0",
            {"country": None, "region": None},
        ),
        ("test_only_street", "DELIVERY", None, None, None, "Test Street", None, {"country": None, "region": None}),
    ],
)
def test_address_doc(app, test_name, a_type, a_city, a_country, a_region, street, p_code, converted):
    """Assert the Address solr doc class works as expected."""
    address = Address(
        addressType=a_type,
        addressCity=a_city,
        addressCountry=a_country,
        addressRegion=a_region,
        postalCode=p_code,
        streetAddress=street,
    )
    assert address

    assert address.address_q
    assert address.streetAddress in address.address_q
    assert not a_city or address.addressCity in address.address_q
    assert not p_code or address.postalCode in address.address_q
    assert not a_country or address.addressCountry in address.address_q
    assert not a_region or converted["region"] in address.address_q

    json = asdict(address)
    assert json
    assert json.get(AddressField.ADDRESS_CITY.value) == a_city
    assert json.get(AddressField.ADDRESS_COUNTRY.value) == converted["country"]
    assert json.get(AddressField.ADDRESS_REGION.value) == a_region
    assert json.get(AddressField.POSTAL_CODE.value) == p_code
    assert json.get(AddressField.STREET_ADDRESS.value) == street
