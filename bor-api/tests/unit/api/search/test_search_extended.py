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
"""Test-Suite to ensure that the search endpoints/functions work as expected."""
import json
import time
from http import HTTPStatus

import pytest
import requests_mock

from bor_api.enums import SolrSynonymType
from bor_api.models import SolrSynonymList
from bor_api.services import solr
from bor_api.services.authz import BASIC_USER, auth_cache
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField, InterestField

from tests import integration_solr
from tests.unit.test_utils import SOLR_TEST_DOCS, create_header


@pytest.mark.parametrize(
    "test_name,query,categories",
    [
        ("test_basic", {"value": "123"}, {}),
        (
            "test_filters",
            {
                "value": "test filters",
                "name": "name",
                EntityField.IDENTIFIER.value: "BC23",
                EntityField.BN.value: "023",
            },
            {},
        ),
        (
            "test_categories",
            {"value": "test categories"},
            {
                EntityField.ENTITY_TYPE.value: ["BUSINESS"],
                EntityField.STATE.value: ["ACTIVE"],
                EntityField.LEGAL_TYPE.value: ["BC", "CP", "SP"],
                EntityField.NATIONALITIES.value: ["CA", "FR"],
            },
        ),
        (
            "test_child_filters",
            {
                "value": "test child filters",
                EntityField.ENTITY_ADDRESSES.value: "vancouver bc",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_BN.value: "0424",
                    EntityRoleField.RELATED_EMAIL.value: "1234",
                    EntityRoleField.RELATED_IDENTIFIER.value: "CP4332",
                    EntityRoleField.RELATED_NAME.value: "related name",
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2022-05-10",
                        DateRangeField.START.value: "2020-01-28",
                    },
                    "value": "CP4332 0424 related name",
                },
            },
            {},
        ),
        (
            "test_child_categories",
            {"value": "test child categories"},
            {
                EntityField.ENTITY_ADDRESSES.value: {
                    AddressField.ADDRESS_CITY.value: ["VANCOUVER", "VICTORIA"],
                    AddressField.ADDRESS_COUNTRY.value: ["Canada"],
                    AddressField.ADDRESS_REGION.value: ["British Columbia", "Alberta"],
                },
                EntityField.ROLES.value: {
                    InterestField.DETAILS.value: ["other"],
                    EntityRoleField.RELATED_STATE.value: ["ACTIVE"],
                    EntityRoleField.RELATED_ENTITY_TYPE.value: ["PERSON", "BUSINESS"],
                    EntityRoleField.ROLE_TYPE.value: ["DIRECTOR", "INCORPORATOR"],
                },
            },
        ),
        (
            "test_all_combined",
            {
                "value": "test all combined",
                "name": "name",
                EntityField.IDENTIFIER.value: "BC23",
                EntityField.BN.value: "023",
                EntityField.ENTITY_ADDRESSES.value: "vancouver bc",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_BN.value: "0424",
                    EntityRoleField.RELATED_EMAIL.value: "1234",
                    EntityRoleField.RELATED_IDENTIFIER.value: "CP4332",
                    EntityRoleField.RELATED_NAME.value: "related name",
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2022-05-10",
                        DateRangeField.START.value: "2020-01-28",
                    },
                    "value": "CP4332 0424 related name",
                },
            },
            {
                EntityField.ENTITY_TYPE.value: ["BUSINESS"],
                EntityField.STATE.value: ["ACTIVE"],
                EntityField.LEGAL_TYPE.value: ["BC", "CP", "SP"],
                EntityField.NATIONALITIES.value: ["CA", "FR"],
                EntityField.ENTITY_ADDRESSES.value: {
                    AddressField.ADDRESS_CITY.value: ["VANCOUVER", "VICTORIA"],
                    AddressField.ADDRESS_COUNTRY.value: ["Canada"],
                    AddressField.ADDRESS_REGION.value: ["British Columbia", "Alberta"],
                },
                EntityField.ROLES.value: {
                    InterestField.DETAILS.value: ["other"],
                    EntityRoleField.RELATED_STATE.value: ["ACTIVE"],
                    EntityRoleField.RELATED_ENTITY_TYPE.value: ["PERSON", "BUSINESS"],
                    EntityRoleField.ROLE_TYPE.value: ["DIRECTOR", "INCORPORATOR"],
                },
            },
        ),
    ],
)
def test_search_solr_mock(app, session, client, jwt, requests_mock, test_name, query, categories):
    """Assert that the entities search call works returns successfully."""
    auth_cache.clear()
    # setup mocks
    account_id = 1
    requests_mock.get(
        f"{app.config.get('AUTH_SVC_URL')}/orgs/{account_id}/products?include_hidden=true",
        json=[{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    requests_mock.post(
        f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query", json={"response": {"docs": [], "numFound": 0, "start": 0}}
    )
    # format payload
    payload = {"query": query}
    if categories:
        payload["categories"] = categories
    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps(payload),
        headers=create_header(
            jwt, [BASIC_USER], **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": account_id}
        ),
    )
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json["facets"] == {"fields": {}}
    assert resp_json["searchResults"]["queryInfo"]["categories"] == {
        "entityAddresses": {
            "addressCity": categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(
                AddressField.ADDRESS_CITY.value, None
            ),
            "addressCountry": categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(
                AddressField.ADDRESS_COUNTRY.value, None
            ),
            "addressRegion": categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(
                AddressField.ADDRESS_REGION.value, None
            ),
        },
        "entityType": categories.get(EntityField.ENTITY_TYPE.value, None),
        "legalType": categories.get(EntityField.LEGAL_TYPE.value, None),
        "nationalities": categories.get(EntityField.NATIONALITIES.value, None),
        "roles": {
            "details": categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_INTERESTS.value, None),
            "relatedEntityType": categories.get(EntityField.ROLES.value, {}).get(
                EntityRoleField.RELATED_ENTITY_TYPE.value, None
            ),
            "relatedState": categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_STATE.value, None),
            "roleType": categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.ROLE_TYPE.value, None),
        },
        "state": categories.get(EntityField.STATE.value, None),
    }
    assert resp_json["searchResults"]["queryInfo"]["query"] == {
        "bn": query.get(EntityField.BN.value, ""),
        "info": query.get(EntityField.INFO_Q.value, ""),
        "identifier": query.get(EntityField.IDENTIFIER.value, "").lower(),
        "name": query.get("name", ""),
        "roles": {
            "relatedBN": query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_BN.value, ""),
            "relatedEmail": query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_EMAIL.value, ""),
            "relatedIdentifier": query.get(EntityField.ROLES.value, {})
            .get(EntityRoleField.RELATED_IDENTIFIER.value, "")
            .lower(),
            "relatedName": query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_NAME.value, ""),
            "roleDates": query.get(EntityField.ROLES.value, {}).get(EntityRoleField.ROLE_DATES.value, {}),
            "value": query.get(EntityField.ROLES.value, {}).get("value", "").lower(),
        },
        "value": query["value"],
    }
    assert resp_json["searchResults"]["queryInfo"]["rows"] == 10
    assert resp_json["searchResults"]["queryInfo"]["start"] == 0
    assert resp_json["searchResults"]["results"] == []
    assert resp_json["searchResults"]["totalResults"] == 0


@integration_solr
@pytest.mark.parametrize(
    "test_name,query,categories,expected",
    [
        (
            "test_basic",  # NOTE: test setup checks for 'test_basic' on the first run
            {"value": "123"},
            {},
            [{"email": "abcd@email.com", "entityType": "BUSINESS", "legalName": "test 1234"}],
        ),
        (
            "test_basic_name_match_exact",
            {"value": "person one"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_partial_1",
            {"value": "per one"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_partial_2",
            {"value": "erson tw"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3R 43R",
                            "score": 0.0,
                            "streetAddress": "charles place 4W2",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "persons two",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_partial_3",
            {"value": "er tw"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3R 43R",
                            "score": 0.0,
                            "streetAddress": "charles place 4W2",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "persons two",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_spellcheck",
            {"value": "pirson ttree"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Seattle",
                            "addressCountry": "United States",
                            "addressRegion": "WA",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 4E4",
                            "score": 0.0,
                            "streetAddress": "jerry lane 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "personing three shoot",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2018-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                # NOTE: 'ttree' matching on 'street'
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Penticton",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "F4K 3S7",
                            "score": 0.0,
                            "streetAddress": "404 Fake Street",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person 13 partner",
                    "roles": [
                        {
                            "relatedBN": "987654322BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234568",
                            "relatedLegalType": "GP",
                            "relatedName": "Firm GP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2024-10-01T00:03:54Z"}],
                            "roleType": "PARTNER",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_stem_1",
            {"value": "persons one"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_stem_2",
            {"value": "personing one"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_stem_3",
            {"value": "personed one"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_mix",
            {"value": "one person"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_mix_partial",
            {"value": "tw pers"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3R 43R",
                            "score": 0.0,
                            "streetAddress": "charles place 4W2",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "persons two",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_mix_stem",
            {"value": "one persons"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_adv_chars",
            {"value": 'p*n o?e "one"'},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_name_match_spec_char",
            {"value": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./"},
            {},
            [
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                }
            ],
        ),
        (
            "test_basic_name_match_and_and",
            {"value": "person and"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person and 5",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person&six",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person+seven",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                # NOTE: matches on 'and' in island
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_and_&",
            {"value": "person &"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person and 5",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person&six",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person+seven",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                # NOTE: matches on 'and' in island
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_and_+",
            {"value": "person +"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person and 5",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person&six",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person+seven",
                    "roles": [
                        {
                            "relatedBN": "09876K",
                            "relatedEmail": "xyz@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0234567",
                            "relatedLegalType": "CP",
                            "relatedName": "tester 1111",
                            "relatedState": "HISTORICAL",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                # NOTE: matches on 'and' in island
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Bowen Island",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V8T 4R8",
                            "score": 0.0,
                            "streetAddress": "Cherry Lane",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person twelve proprietor",
                    "roles": [
                        {
                            "relatedBN": "987654321BC0001",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "FM1234567",
                            "relatedLegalType": "SP",
                            "relatedName": "Firm SP",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2023-04-09T00:03:54Z"}],
                            "roleType": "PROPRIETOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_basic_name_match_._1",
            {"value": "person ten y.z."},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_name_match_._2",
            {"value": "person ten yz"},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_name_match_._3",
            {"value": "person ten x.k."},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_name_match_._4",
            {"value": "person ten xk"},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_exact",
            {"value": "significant individual alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_partial_1",
            {"value": "sign individ alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_partial_2",
            {"value": "ignific vidua"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_spellcheck",
            {"value": "sagnificent endividuol alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_stem_1",
            {"value": "significanted individuals alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_stem_2",
            {"value": "significanting individualed alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_mix",
            {"value": "individual alt significant"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_mix_partial",
            {"value": "individ ifica"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_mix_stem",
            {"value": "individualing significants alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_adv_chars",
            {"value": 'sp*r ch?r "special"'},
            {},
            [
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_spec_char",
            {"value": '#special"char`'},
            {},
            [
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_._1",
            {"value": "person ten si"},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_._2",
            {"value": "person ten s.i."},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_alt_name_match_._3",
            {"value": "person ten r.m."},
            {},
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_basic_tax_number_match",
            {"value": "705 362 853"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_tax_number_match_partial",
            {"value": "705 3"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_tax_number_match_no_space",
            {"value": "705362853"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_tax_number_match_no_space_partial",
            {"value": "7053"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        ("test_basic_tax_number_no_match", {"value": "705 362 852"}, {}, []),
        ("test_basic_tax_number_no_match_partial", {"value": "705 37"}, {}, []),
        (
            "test_basic_email_match_exact",
            {"value": "nine@si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_match_partial_1",
            {"value": "nine@si9"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_match_partial_2",
            {"value": "@si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                },
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                },
            ],
        ),
        ("test_basic_email_no_match", {"value": "nine@email.com"}, {}, []),
        (
            "test_basic_email_and_name_1",
            {"value": "person nine@si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_and_name_2",
            {"value": "nine@si9.com person"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_and_name_3",
            {"value": "person nine@si9.com significant"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_domain_and_name",
            {"value": "nine person @si9. com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                },
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                },
            ],
        ),
        (
            "test_basic_email_and_name_partial",
            {"value": "per nin sign @si9"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_and_name_fuzzy_1",
            {"value": "person nine@so9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_basic_email_and_name_fuzzy_2",
            {"value": "persan nine@so9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        ("test_basic_email_fuzzy_no_match", {"value": "nane@so.com"}, {}, []),
        (
            "test_basic_address_match",
            {"value": "walaby way"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_address_match_partial",
            {"value": "waleby way"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_address_match_mix",
            {"value": "way walaby"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_basic_address_match_mix_partial",
            {"value": "way wilaby"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                },
            ],
        ),
        (
            "test_basic_name_and_address_match_partial",
            {"value": "pirson way wilaby"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        ("test_basic_rel_email_no_match", {"value": "person xyz@email.com"}, {}, []),
        ("test_basic_no_match", {"value": "zzz no match here qljrb"}, {}, []),
        ("test_basic_empty_space", {"value": " "}, {}, []),
        (
            "test_filters_business",
            {
                "value": "test",
                EntityField.LEGAL_NAME.value: "test 1234",
                EntityField.IDENTIFIER.value: "CP123",
                EntityField.BN.value: "BN00",
            },
            {},
            [{"email": "abcd@email.com", "entityType": "BUSINESS", "legalName": "test 1234"}],
        ),
        (
            "test_filters_legal_name",
            {"value": "person nine", "name": "nine"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_filters_alt_name",
            {"value": "person nine", "name": "alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_filters_name",
            {"value": "person nine", "name": "nine alt"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        ("test_filters_alt_name_no_match", {"value": "person nine", "name": "alternate"}, {}, []),
        (
            "test_filters_info_tax_number",
            {"value": "person nine", "info": "705"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_filters_info_email",
            {"value": "person nine", "info": "nine@si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        ("test_filters_info_email_no_match", {"value": "person nine", "info": "nine@com"}, {}, []),
        (
            "test_filters_info_address",
            {"value": "person nine", "info": "V6V 1P2"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_filters_info_combined",
            {"value": "person nine", "info": "853 Vancouver si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_filters_all_combined",
            {"value": "person nine", "name": "nine", "info": "853 Vancouver si9.com"},
            {},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        ("test_filters_no_match", {"value": "person", "name": "ten", "info": "nine@si9.com"}, {}, []),
        (
            "test_categories_1",
            {"value": "person"},
            {EntityField.NATIONALITIES.value: ["FR"]},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_categories_2",
            {"value": "person"},
            {EntityField.NATIONALITIES.value: ["FR", "CA"]},
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                },
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                },
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                },
            ],
        ),
        ("test_categories_no_match", {"value": "person"}, {EntityField.NATIONALITIES.value: ["UK"]}, []),
        (
            "test_child_filters",
            {
                "value": "person one",
                EntityField.ENTITY_ADDRESSES.value: "victoria canada",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_BN.value: "123",
                    EntityRoleField.RELATED_IDENTIFIER.value: "CP123",
                    EntityRoleField.RELATED_NAME.value: "test",
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2023-05-10",
                        DateRangeField.START.value: "2020-01-28",
                    },
                    "value": "CP123 test",
                },
            },
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_value",
            {
                "value": "person one",
                EntityField.ENTITY_ADDRESSES.value: "victoria brit col",
                EntityField.ROLES.value: {"value": "CP123 test"},
            },
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_role_dates_1",
            {
                "value": "person",
                EntityField.ROLES.value: {
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2017-05-10",
                        DateRangeField.START.value: "2014-01-28",
                    },
                },
            },
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_role_dates_2",
            {
                "value": "person",
                EntityField.ROLES.value: {
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2015-08-04",
                        DateRangeField.START.value: "2014-01-28",
                    },
                },
            },
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_role_dates_3",
            {
                "value": "person",
                EntityField.ROLES.value: {
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2017-08-04",
                        DateRangeField.START.value: "2015-09-05",
                    },
                },
            },
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_role_dates_4",
            {
                "value": "person",
                EntityField.ROLES.value: {
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2015-08-03",
                        DateRangeField.START.value: "2014-09-05",
                    },
                },
            },
            {},
            [],
        ),
        (
            "test_child_filters_related_email_1",
            {"value": "person", EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value: "5555"}},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_email_2",
            {"value": "person", EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value: "5555@email.com"}},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_email_3",
            {"value": "person", EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value: "5@email.com"}},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_child_filters_related_email_4",
            {
                "value": "person",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_EMAIL.value: "+em-ail: \\ ~ ^ / ! || AND NOT && OR [] {} ()"
                },
            },
            {},
            [],
        ),
        (
            "test_child_filters_no_match",
            {
                "value": "person",
                EntityField.ENTITY_ADDRESSES.value: "vancouver british colum",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_BN.value: "0424",
                    EntityRoleField.RELATED_IDENTIFIER.value: "CP4332",
                    EntityRoleField.RELATED_NAME.value: "related name",
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2022-05-10",
                        DateRangeField.START.value: "2020-01-28",
                    },
                },
            },
            {},
            [],
        ),
        (
            "test_child_categories_1",
            {"value": "person"},
            {
                EntityField.ENTITY_ADDRESSES.value: {
                    AddressField.ADDRESS_COUNTRY.value: ["Canada", "United States"],
                    AddressField.ADDRESS_REGION.value: ["BC", "AB", "WA"],
                },
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_STATE.value: ["ACTIVE"],
                    EntityRoleField.RELATED_ENTITY_TYPE.value: ["BUSINESS"],
                    EntityRoleField.ROLE_TYPE.value: ["DIRECTOR", "INCORPORATOR"],
                },
            },
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3S 1E4",
                            "score": 0.0,
                            "streetAddress": "walaby way 1112",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person one",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 1A4",
                            "score": 0.0,
                            "streetAddress": "hello world 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person eight",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Calgary",
                                    "addressCountry": "Canada",
                                    "addressRegion": "AB",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V2R 3A7",
                                    "score": 0.0,
                                    "streetAddress": "8888 related address",
                                }
                            ],
                            "relatedBN": "BN00012334",
                            "relatedEmail": "5555@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP0034567",
                            "relatedLegalType": "CP",
                            "relatedName": "tests 2222",
                            "relatedState": "ACTIVE",
                            "roleDates": [
                                {
                                    "active": False,
                                    "end": "2016-08-04T00:03:54Z",
                                    "score": 0.0,
                                    "start": "2015-08-04T00:03:54Z",
                                }
                            ],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3R 43R",
                            "score": 0.0,
                            "streetAddress": "charles place 4W2",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "persons two",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Seattle",
                            "addressCountry": "United States",
                            "addressRegion": "WA",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 4E4",
                            "score": 0.0,
                            "streetAddress": "jerry lane 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "personing three shoot",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2018-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                },
            ],
        ),
        (
            "test_child_categories_2",
            {"value": "person"},
            {
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_INTERESTS.value: ["controlType.shares.registeredOwner"],
                }
            },
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                }
            ],
        ),
        (
            "test_child_categories_3",
            {"value": "person"},
            {
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_INTERESTS.value: ["other"],
                }
            },
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_child_categories_4",
            {"value": "person"},
            {
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_INTERESTS.value: [
                        "controlType.shares.registeredOwner",
                        "controlType.votes.beneficialOwner",
                    ],
                }
            },
            [
                {
                    "alternateName": "significant individual alt",
                    "birthDate": "1999-02-26",
                    "email": "nine@si9.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "V6V 1P2",
                            "score": 0.0,
                            "streetAddress": "hello world 500",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person nine",
                    "nationalities": ["CA", "US", "FR"],
                    "phoneNumber": "+1 (778) 445 7843",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Fake",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V3C 3X9",
                                    "score": 0.0,
                                    "streetAddress": "9999 related address",
                                }
                            ],
                            "relatedBN": "124221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0000007",
                            "relatedInterests": [
                                {
                                    "details": "controlType.shares.registeredOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.actingJointly",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "1111", "interestPartyName": "PartyName 1", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.shares.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "shareholding",
                                    "relatedParties": [
                                        {"interestPartyID": "2222", "interestPartyName": "PartyName 2", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "lots of words in here",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-03-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "705 362 853",
                },
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                },
                {
                    "alternateName": '#special"char`',
                    "birthDate": "1988-10-03",
                    "email": "eleven@si11.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Vancouver",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc 11",
                            "postalCode": "V3V 4T6",
                            "score": 0.0,
                            "streetAddress": "Willaby Way",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:'\",<>./",
                    "nationalities": ["CA"],
                    "phoneNumber": "+1 (250) 245 9804",
                    "roles": [
                        {
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                                {
                                    "details": "controlType.directors.inConcertControl",
                                    "directOrIndirect": "direct",
                                    "interestType": "appointmentOfBoard",
                                    "relatedParties": [
                                        {"interestPartyID": "3333", "interestPartyName": "PartyName 3", "score": 0.0}
                                    ],
                                    "score": 0.0,
                                    "sharesMax": 50.0,
                                    "sharesMin": 25.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2021-01-19T00:05:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "111 442 356",
                },
            ],
        ),
        (
            "test_child_categories_no_match",
            {"value": "person"},
            {
                EntityField.ROLES.value: {
                    EntityRoleField.ROLE_TYPE.value: ["DIRECTOR"],
                    EntityRoleField.RELATED_INTERESTS.value: ["other"],
                }
            },
            [],
        ),
        (
            "test_synonym_country",
            {"value": "person three US"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Seattle",
                            "addressCountry": "United States",
                            "addressRegion": "WA",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 4E4",
                            "score": 0.0,
                            "streetAddress": "jerry lane 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "personing three shoot",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2018-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_synonym_region",
            {"value": "persons two bc"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "postalCode": "T3R 43R",
                            "score": 0.0,
                            "streetAddress": "charles place 4W2",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "persons two",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_synonym_name",
            {"value": "person three chute"},
            {},
            [
                {
                    "entityAddresses": [
                        {
                            "addressCity": "Seattle",
                            "addressCountry": "United States",
                            "addressRegion": "WA",
                            "addressType": "DELIVERY",
                            "postalCode": "V3R 4E4",
                            "score": 0.0,
                            "streetAddress": "jerry lane 9002",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "personing three shoot",
                    "roles": [
                        {
                            "relatedBN": "BN00012334",
                            "relatedEmail": "abcd@email.com",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "CP1234567",
                            "relatedLegalType": "CP",
                            "relatedName": "test 1234",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2018-08-04T00:03:54Z"}],
                            "roleType": "DIRECTOR",
                            "score": 0.0,
                        }
                    ],
                }
            ],
        ),
        (
            "test_all_combined_person",
            {
                "value": "parson yz rm @si 104342 universe 4r1 locatian",
                EntityField.LEGAL_NAME.value: "t",
                "name": "rm",
                EntityField.ENTITY_ADDRESSES.value: "hi universe 1000 location desc V3L 4R1 victoria",
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_BN.value: "125",
                    EntityRoleField.RELATED_IDENTIFIER.value: "BC20047",
                    EntityRoleField.RELATED_NAME.value: "sensitive",
                    EntityRoleField.ROLE_DATES.value: {
                        DateRangeField.END.value: "2022-05-10",
                        DateRangeField.START.value: "2018-01-28",
                    },
                    "value": "not case 002004 532",
                },
            },
            {
                EntityField.ENTITY_TYPE.value: ["PERSON"],
                EntityField.NATIONALITIES.value: ["CA"],
                EntityField.ENTITY_ADDRESSES.value: {
                    AddressField.ADDRESS_COUNTRY.value: ["Canada"],
                    AddressField.ADDRESS_REGION.value: ["BC", "AB"],
                },
                EntityField.ROLES.value: {
                    EntityRoleField.RELATED_STATE.value: ["ACTIVE"],
                    EntityRoleField.RELATED_ENTITY_TYPE.value: ["BUSINESS"],
                    EntityRoleField.RELATED_INTERESTS.value: [
                        "controlType.shares.registeredOwner",
                        "controlType.votes.beneficialOwner",
                    ],
                    EntityRoleField.ROLE_TYPE.value: ["SIGNIFICANT INDIVIDUAL"],
                },
            },
            [
                {
                    "alternateName": "s.i. rm",
                    "birthDate": "1954-12-14",
                    "email": "ten@si.com",
                    "entityAddresses": [
                        {
                            "addressCity": "Victoria",
                            "addressCountry": "Canada",
                            "addressRegion": "BC",
                            "addressType": "DELIVERY",
                            "locationDescription": "location desc",
                            "postalCode": "V3L 4R1",
                            "score": 0.0,
                            "streetAddress": "hi universe 1000",
                        }
                    ],
                    "entityType": "PERSON",
                    "legalName": "person ten y.z. xk",
                    "nationalities": ["CA"],
                    "phoneNumber": "+44 020 4750 3344",
                    "roles": [
                        {
                            "relatedAddresses": [
                                {
                                    "addressCity": "Sidney",
                                    "addressCountry": "Canada",
                                    "addressRegion": "BC",
                                    "addressType": "DELIVERY",
                                    "postalCode": "V1L 0W1",
                                    "score": 0.0,
                                    "streetAddress": "1010 related address",
                                }
                            ],
                            "relatedBN": "1255323221",
                            "relatedEntityType": "BUSINESS",
                            "relatedIdentifier": "BC0020047",
                            "relatedInterests": [
                                {
                                    "details": "controlType.votes.beneficialOwner",
                                    "directOrIndirect": "direct",
                                    "interestType": "votingRights",
                                    "score": 0.0,
                                    "sharesMax": 75.0,
                                    "sharesMin": 50.0,
                                },
                                {
                                    "details": "other",
                                    "directOrIndirect": "unknown",
                                    "interestType": "otherInfluenceOrControl",
                                    "otherReason": "bla bla other reason",
                                    "score": 0.0,
                                },
                            ],
                            "relatedLegalType": "BEN",
                            "relatedName": "NOt Case SENSitive",
                            "relatedState": "ACTIVE",
                            "roleDates": [{"active": True, "score": 0.0, "start": "2020-11-09T00:03:54Z"}],
                            "roleType": "SIGNIFICANT INDIVIDUAL",
                            "score": 0.0,
                        }
                    ],
                    "taxNumber": "104 342 350",
                }
            ],
        ),
        (
            "test_all_combined_business",
            {
                "value": "test",
                EntityField.LEGAL_NAME.value: "12",
                EntityField.IDENTIFIER.value: "CP12",
                EntityField.BN.value: "123",
            },
            {
                EntityField.ENTITY_TYPE.value: ["BUSINESS"],
                EntityField.STATE.value: ["ACTIVE"],
                EntityField.LEGAL_TYPE.value: ["BC", "CP", "SP"],
            },
            [{"email": "abcd@email.com", "entityType": "BUSINESS", "legalName": "test 1234"}],
        ),
    ],
)
def test_search(app, session, client, jwt, monkeypatch, test_name, query, categories, expected):
    """Assert that the entities search call works returns successfully."""
    # test setup
    if test_name == "test_basic":
        # setup solr data for test (only needed the first time)
        solr.delete_all_docs()
        time.sleep(1)
        solr.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)
    # add test dependent synonyms to db
    SolrSynonymList(synonym="bc", synonym_list=["british columbia", "bc"], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(
        synonym="british columbia", synonym_list=["british columbia", "bc"], synonym_type=SolrSynonymType.ADDRESS
    ).save()
    SolrSynonymList(
        synonym="united states", synonym_list=["us", "united states"], synonym_type=SolrSynonymType.ADDRESS
    ).save()
    SolrSynonymList(synonym="us", synonym_list=["us", "united states"], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym="chute", synonym_list=["chute", "shoot"], synonym_type=SolrSynonymType.NAME).save()
    # setup products mock in validator
    monkeypatch.setattr(
        "bor_api.utils.request_validators.account_products",
        lambda *args, **kwargs: [{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    # format payload
    payload = {"query": query}
    if categories:
        payload["categories"] = categories

    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps(payload),
        headers=create_header(
            jwt, [BASIC_USER], **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": 1}
        ),
    )
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json["facets"]
    assert resp_json["searchResults"]
    results = resp_json["searchResults"]["results"]
    assert resp_json["searchResults"]["totalResults"] == len(expected)
    for result in results:
        del result["score"]
        assert result.get(EntityField.LEGAL_NAME.value)

    assert results == expected


def test_search_xlsx(app, session, client, jwt, requests_mock):
    """Assert that the entities search call works returns successfully."""
    # setup mocks
    account_id = 1
    requests_mock.get(
        f"{app.config.get('AUTH_SVC_URL')}/orgs/{account_id}/products?include_hidden=true",
        json=[{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    doc = {
        "entityAddresses": [
            {
                "addressCity": "Victoria",
                "addressCountry": "Canada",
                "addressRegion": "BC",
                "addressType": "DELIVERY",
                "postalCode": "T3R 43R",
                "score": 0.0,
                "streetAddress": "charles place 4W2",
            }
        ],
        "entityType": "PERSON",
        "legalName": "persons two",
        "roles": [
            {
                "relatedBN": "BN00012334",
                "relatedEmail": "abcd@email.com",
                "relatedEntityType": "BUSINESS",
                "relatedIdentifier": "CP1234567",
                "relatedLegalType": "CP",
                "relatedName": "test 1234",
                "relatedState": "ACTIVE",
                "roleDates": [{"active": True, "score": 0.0, "start": "2019-08-04T00:03:54Z"}],
                "roleType": "DIRECTOR",
                "score": 0.0,
            }
        ],
    }

    requests_mock.post(
        f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query",
        json={"response": {"docs": [doc], "numFound": 1, "start": 0}},
    )
    # format payload
    payload = {"query": {"value": "persons two"}}
    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps(payload),
        headers=create_header(
            jwt,
            [BASIC_USER],
            **{
                "Accept-Version": "v1",
                "content-type": "application/json",
                "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Account-Id": account_id,
            },
        ),
    )
    # test
    assert resp.status_code == HTTPStatus.OK
    assert resp.data


def test_search_error(app, session, client, jwt, monkeypatch, requests_mock):
    """Assert that the entities search call error handling works as expected."""
    # setup products mock in validator
    monkeypatch.setattr(
        "bor_api.utils.request_validators.account_products",
        lambda *args, **kwargs: [{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    # setup solr mock
    mocked_error_msg = "mocked error"
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(
        f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query",
        json={"error": {"msg": mocked_error_msg}},
        status_code=mocked_status_code,
    )
    # create payload
    payload = {"query": {"value": "123"}}
    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps(payload),
        headers=create_header(
            jwt, [BASIC_USER], **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": 1}
        ),
    )
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get("detail") == f"{mocked_error_msg}, {mocked_status_code}"
    assert resp_json.get("message") == "Solr service error while processing request."


@pytest.mark.parametrize(
    "test_name,query,categories,headers,errors",
    [
        ("test_no_value", {}, {}, {}, [{"Invalid payload": "Expected a string for 'value'."}]),
        (
            "test_invalid_accept_headers",
            {"value": "a"},
            {},
            {"Accept": "application/pdf"},
            [
                {
                    "Invalid header": "Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf"
                }
            ],
        ),
        (
            "test_invalid_query_and_headers",
            {},
            {},
            {"Accept": "application/pdf"},
            [
                {"Invalid payload": "Expected a string for 'value'."},
                {
                    "Invalid header": "Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf"
                },
            ],
        ),
    ],
)
def test_search_bad_request(app, session, client, jwt, monkeypatch, test_name, query, categories, headers, errors):
    """Assert that the entities search call validates the payload."""
    # setup products mock in validator
    monkeypatch.setattr(
        "bor_api.utils.request_validators.account_products",
        lambda *args, **kwargs: [{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    # create payload
    payload = {"query": query}
    if categories:
        payload["categories"] = categories
    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps(payload),
        headers=create_header(
            jwt,
            [BASIC_USER],
            **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": 1, **headers},
        ),
    )
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get("message") == "Errors processing request."
    assert resp_json.get("details") == errors


@pytest.mark.parametrize(
    "test_name,subscription,expected",
    [
        ("test_authorized", {"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}, HTTPStatus.OK),
        ("test_wrong_product_NDS", {"code": "NDS", "subscriptionStatus": "ACTIVE"}, HTTPStatus.UNAUTHORIZED),
        ("test_wrong_product_BUSINESS", {"code": "BUSINESS", "subscriptionStatus": "ACTIVE"}, HTTPStatus.UNAUTHORIZED),
        (
            "test_subscription_inactive",
            {"code": "CA_SEARCH", "subscriptionStatus": "INACTIVE"},
            HTTPStatus.UNAUTHORIZED,
        ),
    ],
)
def test_search_product_access(
    app, client, session, jwt, monkeypatch, requests_mock, test_name, subscription, expected
):
    """Assert access is granted/denied based on having the right product subscription."""
    # setup mocks
    monkeypatch.setattr("bor_api.utils.request_validators.account_products", lambda *args, **kwargs: [subscription])
    monkeypatch.setattr("bor_api.utils.request_validators.flags.value", lambda *args, **kwargs: False)
    requests_mock.post(
        f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query", json={"response": {"docs": [], "numFound": 0, "start": 0}}
    )
    # call search
    resp = client.post(
        f"/api/v1/search/extended",
        data=json.dumps({"query": {"value": "a"}}),
        headers=create_header(
            jwt, [BASIC_USER], **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": 1}
        ),
    )
    # test
    assert resp.status_code == expected


def test_search_fields(app, session, client, jwt, monkeypatch):
    """Assert the fields for data requested are set correctly for the endpoint."""
    monkeypatch.setattr(
        "bor_api.utils.request_validators.account_products",
        lambda *args, **kwargs: [{"code": "CA_SEARCH", "subscriptionStatus": "ACTIVE"}],
    )
    solr_url = f"{app.config.get('SOLR_SVC_FOLLOWER_URL')}/{app.config.get('SOLR_SVC_FOLLOWER_CORE')}/query"

    with requests_mock.mock() as m:
        m.post(solr_url, json={"response": {"docs": []}})

        # call search
        resp = client.post(
            f"/api/v1/search/extended",
            data=json.dumps({"query": {"value": "a"}}),
            headers=create_header(
                jwt, [BASIC_USER], **{"Accept-Version": "v1", "content-type": "application/json", "Account-Id": 1}
            ),
        )
        # test
        assert resp.status_code == HTTPStatus.OK
        assert m.called == True
        fields_requested = m.request_history[0].json()["fields"]
        assert fields_requested == [
            "birthDate",
            "entityType",
            "legalName",
            "nationalities",
            "roles",
            "score",
            "[child]",
            "relatedBN",
            "relatedEntityType",
            "relatedIdentifier",
            "relatedName",
            "relatedState",
            "roleType",
            "relatedLegalType",
            "entityAddresses",
            "relatedEmail",
            "roleDates",
            "addressCity",
            "addressCountry",
            "addressRegion",
            "addressType",
            "postalCode",
            "streetAddress",
            "streetAdditional",
            "locationDescription",
            "active",
            "start",
            "end",
            "alternateName",
            "email",
            "isPermanentResident",
            "externalInfluence",
            "phoneNumber",
            "taxNumber",
            "taxResidencies",
            "relatedAddresses",
            "relatedInterests",
            "details",
            "directOrIndirect",
            "otherReason",
            "sharesExact",
            "sharesMax",
            "sharesMin",
            "interestType",
            "relatedParties",
            "interestPartyID",
            "interestPartyName",
        ]
