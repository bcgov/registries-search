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

from bor_api.enums import SolrSynonymType
from bor_api.models import SolrSynonymList
from bor_api.services import solr_temp
from bor_api.services.authz import BASIC_USER
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField

from tests import integration_solr
from tests.unit.test_utils import SOLR_TEST_DOCS, create_header


@pytest.mark.parametrize('test_name,query,categories', [
    ('test_basic', {'value': '123'}, {}),
    ('test_filters',
     {'value': 'test filters', 'name': 'name', EntityField.IDENTIFIER.value: 'BC23', EntityField.BN.value: '023'},
     {}
    ),
    ('test_categories',
     {'value': 'test categories'},
     {EntityField.ENTITY_TYPE.value: ['BUSINESS'], EntityField.STATE.value:['ACTIVE'], EntityField.LEGAL_TYPE.value: ['BC', 'CP', 'SP']}
    ),
    ('test_child_filters', {
        'value': 'test child filters',
        EntityField.ENTITY_ADDRESSES.value: 'vancouver bc',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_EMAIL.value: '1234',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name',
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2022-05-10', DateRangeField.START.value: '2020-01-28'},
            'value': 'CP4332 0424 related name'
        }
     },{}
    ),
    ('test_child_categories',
     {'value': 'test child categories'},
     {
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_CITY.value: ['VANCOUVER', 'VICTORIA'],
            AddressField.ADDRESS_COUNTRY.value:['Canada'],
            AddressField.ADDRESS_REGION.value: ['British Columbia', 'Alberta']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['PERSON', 'BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     }
    ),
    ('test_all_combined',
     {
        'value': 'test all combined',
        'name': 'name',
        EntityField.IDENTIFIER.value: 'BC23',
        EntityField.BN.value: '023',
        EntityField.ENTITY_ADDRESSES.value: 'vancouver bc',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_EMAIL.value: '1234',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name',
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2022-05-10', DateRangeField.START.value: '2020-01-28'},
            'value': 'CP4332 0424 related name'
        }
     },
     {
        EntityField.ENTITY_TYPE.value: ['BUSINESS'],
        EntityField.STATE.value:['ACTIVE'],
        EntityField.LEGAL_TYPE.value: ['BC', 'CP', 'SP'],
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_CITY.value: ['VANCOUVER', 'VICTORIA'],
            AddressField.ADDRESS_COUNTRY.value:['Canada'],
            AddressField.ADDRESS_REGION.value: ['British Columbia', 'Alberta']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['PERSON', 'BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     })
])
def test_search_solr_mock(app, session, client, jwt, requests_mock, test_name, query, categories):
    """Assert that the entities search call works returns successfully."""
    # setup mocks
    account_id = 1
    requests_mock.get(f"{app.config.get('AUTH_SVC_URL')}/orgs/{account_id}/products?include_hidden=true",
                      json=[{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    requests_mock.post(f"{app.config.get('TEMP_SOLR_SVC_URL')}/bo/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/extended',
                       data=json.dumps(payload),
                       headers=create_header(jwt,[BASIC_USER], **{'Accept-Version': 'v1',
                                                                  'content-type': 'application/json',
                                                                  'Account-Id': account_id}))
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets'] == {'fields': {}}
    assert resp_json['searchResults']['queryInfo']['categories'] == {
        'entityAddresses': {
            'addressCity': categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(AddressField.ADDRESS_CITY.value, None),
            'addressCountry': categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(AddressField.ADDRESS_COUNTRY.value, None),
            'addressRegion': categories.get(EntityField.ENTITY_ADDRESSES.value, {}).get(AddressField.ADDRESS_REGION.value, None)},
        'entityType': categories.get(EntityField.ENTITY_TYPE.value, None),
        'legalType': categories.get(EntityField.LEGAL_TYPE.value, None),
        'roles': {
            'relatedEntityType': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_ENTITY_TYPE.value, None),
            'relatedState': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_STATE.value, None),
            'roleType': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.ROLE_TYPE.value, None)
        },
        'state': categories.get(EntityField.STATE.value, None)
    }
    assert resp_json['searchResults']['queryInfo']['query'] == {
        'bn': query.get(EntityField.BN.value, ''),
        'entityAddresses': query.get(EntityField.ENTITY_ADDRESSES.value, ''),
        'identifier': query.get(EntityField.IDENTIFIER.value, '').lower(),
        'name': query.get('name', ''),
        'roles': {
            'relatedBN': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_BN.value, ''),
            'relatedEmail': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_EMAIL.value, ''),
            'relatedIdentifier': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_IDENTIFIER.value, '').lower(),
            'relatedName': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_NAME.value, ''),
            'roleDates': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.ROLE_DATES.value, {}),
            'value': query.get(EntityField.ROLES.value, {}).get('value', '').lower()},
        'value': query['value']
    }
    assert resp_json['searchResults']['queryInfo']['rows'] == 10
    assert resp_json['searchResults']['queryInfo']['start'] == 0
    assert resp_json['searchResults']['results'] == []
    assert resp_json['searchResults']['totalResults'] == 0


@integration_solr
@pytest.mark.parametrize('test_name,query,categories,expected', [
    ('test_basic',
     {'value': '123'},
     {},
     [{'email': 'abcd@email.com', 'entityType': 'BUSINESS', 'legalName': 'test 1234'}],
    ),
    ('test_basic_name_match_exact',
     {'value': 'person one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_1',
     {'value': 'per one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_2',
     {'value': 'erson tw'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_3',
     {'value': 'er tw'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spellcheck',
     {'value': 'pirson ttree'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_1',
     {'value': 'persons one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_2',
     {'value': 'personing one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_3',
     {'value': 'personed one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix',
     {'value': 'one person'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_partial',
     {'value': 'tw pers'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_stem',
     {'value': 'one persons'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spec_char',
     {'value': '*person! [one]'},
     {},[{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]),
    ('test_basic_name_match_and_and',
     {'value': 'person and'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_&',
     {'value': 'person &'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_+',
     {'value': 'person +'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_._1',
     {'value': 'person ten y.z.'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_name_match_._2',
     {'value': 'person ten yz'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_name_match_._3',
     {'value': 'person ten x.k.'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_name_match_._4',
     {'value': 'person ten xk'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_alt_name_match_exact',
     {'value': 'significant individual alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_partial_1',
     {'value': 'sign individ alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_partial_2',
     {'value': 'ignific vidua'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_spellcheck',
     {'value': 'sagnificent endividuol alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_stem_1',
     {'value': 'significanted individuals alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_stem_2',
     {'value': 'significanting individualed alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_mix',
     {'value': 'individual alt significant'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_mix_partial',
     {'value': 'individ ifica'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_mix_stem',
     {'value': 'individualing significants alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_spec_char',
     {'value': '*significant! [individual$] alt^'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_alt_name_match_._1',
     {'value': 'person ten si'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_alt_name_match_._2',
     {'value': 'person ten s.i.'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_alt_name_match_._3',
     {'value': 'person ten r.m.'},
     {},
     [{'alternateName': 's.i. rm', 'email': 'ten@si.com', 'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3L 4R1', 'score': 0.0, 'streetAddress': 'hi universe 1000'}], 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'voting', 'score': 0.0, 'sharesMax': 75.0, 'sharesMin': 50.0}], 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-11-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '104 342 350'}]
    ),
    ('test_basic_tax_number_match',
     {'value': '705 362 853'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_tax_number_match_partial',
     {'value': '705 3'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_tax_number_match_no_space',
     {'value': '705362853'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_tax_number_match_no_space_partial',
     {'value': '7053'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_basic_tax_number_no_match',
     {'value': '705 362 852'},
     {},
     []
    ),
    ('test_basic_tax_number_no_match_partial',
     {'value': '705 37'},
     {},
     []
    ),
    ('test_basic_address_match',
     {'value': 'walaby way'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_partial',
     {'value': 'waleby way'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_mix',
     {'value': 'way walaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_mix_partial',
     {'value': 'way wilaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_name_and_address_match_partial',
     {'value': 'pirson way wilaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_no_match', {'value': 'zzz no match here qljrb'}, {},[]),
    ('test_filters',
     {'value': 'test', EntityField.LEGAL_NAME.value: 'test 1234', EntityField.IDENTIFIER.value: 'CP123', EntityField.BN.value: 'BN00'},
     {},
     [{'email': 'abcd@email.com', 'entityType': 'BUSINESS', 'legalName': 'test 1234'}]
    ),
    ('test_filters_no_match',
     {'value': 'test filters', EntityField.LEGAL_NAME.value: 'name', EntityField.IDENTIFIER.value: 'BC23', EntityField.BN.value: '023'},
     {},
     []
    ),
    ('test_legal_name_filter',
     {'value': 'person nine', 'name': 'nine'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_preferred_name_filter',
     {'value': 'person nine', 'name': 'alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_name_filter_combined',
     {'value': 'person nine', 'name': 'nine alt'},
     {},
     [{'alternateName': 'significant individual alt', 'email': 'nine@si.com', 'entityAddresses': [{'addressCity': 'Vancouver', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V6V 1P2', 'score': 0.0, 'streetAddress': 'hello world 500'}], 'entityType': 'PERSON', 'legalName': 'person nine', 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedInterests': [{'details': 'controlType.sharesOrVotes.registeredOwner', 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'score': 0.0, 'sharesMax': 50.0, 'sharesMin': 25.0}], 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-03-09T00:03:54Z'}], 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}], 'taxNumber': '705 362 853'}]
    ),
    ('test_preferred_name_filter_no_match',
     {'value': 'person nine', 'name': 'alternate'},
     {},
     []
    ),
    ('test_categories',
     {'value': 'tests 2222'},
     {EntityField.ENTITY_TYPE.value: ['BUSINESS'], EntityField.STATE.value:['ACTIVE'], EntityField.LEGAL_TYPE.value: ['BC', 'CP', 'SP']},
     [{'email': '5555@email.com', 'entityType': 'BUSINESS', 'legalName': 'tests 2222'}]
    ),
    ('test_categories_no_match',
     {'value': 'test 1234'},
     {EntityField.ENTITY_TYPE.value: ['BUSINESS'], EntityField.STATE.value:['ACTIVE'], EntityField.LEGAL_TYPE.value: ['BC', 'GP', 'SP']},
     []
    ),
    ('test_child_filters',
     {
        'value': 'person one',
        EntityField.ENTITY_ADDRESSES.value: 'victoria canada',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '123',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP123',
            EntityRoleField.RELATED_NAME.value: 'test',
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2023-05-10', DateRangeField.START.value: '2020-01-28'},
            'value': 'CP123 test'
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_value',
     {
        'value': 'person one',
        EntityField.ENTITY_ADDRESSES.value: 'victoria brit col',
        EntityField.ROLES.value: {'value': 'CP123 test'}
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_1',
     {
        'value': 'person',
        EntityField.ROLES.value: {
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2017-05-10', DateRangeField.START.value: '2014-01-28'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_2',
     {
        'value': 'person',
        EntityField.ROLES.value: {
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2015-08-04', DateRangeField.START.value: '2014-01-28'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_3',
     {
        'value': 'person',
        EntityField.ROLES.value: {
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2017-08-04', DateRangeField.START.value: '2015-09-05'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_4',
     {
        'value': 'person',
        EntityField.ROLES.value: {
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2015-08-03', DateRangeField.START.value: '2014-09-05'},
        }
     },
     {},
     []
    ),
    ('test_child_filters_related_email_1',
     {'value': 'person', EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value:"5555"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_2',
     {'value': 'person', EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value:"5555@email.com"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_3',
     {'value': 'person', EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value:"5@email.com"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_4',
     {'value': 'person', EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value:"+em-ail: \\ ~ ^ / ! || AND NOT && OR [] {} ()"}},
     {},
     []
    ),
    ('test_child_filters_no_match',
     {
        'value': 'person',
        EntityField.ENTITY_ADDRESSES.value: 'vancouver british colum',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name',
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2022-05-10', DateRangeField.START.value: '2020-01-28'}
        }
     },
     {},
     []
    ),
    ('test_child_categories',
     {'value': 'person'},
     {
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_COUNTRY.value:['Canada', 'United States'],
            AddressField.ADDRESS_REGION.value: ['BC', 'AB', 'WA']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     [
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '5555@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_categories_no_match',
     {'value': 'person'},
     {
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_COUNTRY.value:['Canada'],
            AddressField.ADDRESS_REGION.value: ['ON', 'AB']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['PERSON'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     []
    ),
    ('test_synonym_country',
     {'value': 'person three US'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_synonym_region',
     {'value': 'persons two bc'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_synonym_name',
     {'value': 'person three chute'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_all_combined_person',
     {
        'value': 'person CA bc',
        EntityField.LEGAL_NAME.value: 't',
        EntityField.ENTITY_ADDRESSES.value: 'charles place victoria british colu',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '123',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP123',
            EntityRoleField.RELATED_NAME.value: 'test',
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2022-05-10', DateRangeField.START.value: '2018-01-28'},
            'value': 'CP123 test'
        }
     },
     {
        EntityField.ENTITY_TYPE.value: ['PERSON'],
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_COUNTRY.value:['Canada'],
            AddressField.ADDRESS_REGION.value: ['BC', 'AB']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR']
        }
     },
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_all_combined_business',
     {
        'value': 'test',
        EntityField.LEGAL_NAME.value: '12',
        EntityField.IDENTIFIER.value: 'CP12',
        EntityField.BN.value: '123'
     },
     {
        EntityField.ENTITY_TYPE.value: ['BUSINESS'],
        EntityField.STATE.value:['ACTIVE'],
        EntityField.LEGAL_TYPE.value: ['BC', 'CP', 'SP']
     },
     [{'email': 'abcd@email.com', 'entityType': 'BUSINESS', 'legalName': 'test 1234'}]
    ),
    ('test_basic_email_match_exact',
     {'value': 'xyz@email.com'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'lala lane 9002'}], 'entityType': 'PERSON', 'legalName': 'person-four', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS','relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_email_match_partia_l',
     {'value': 'xyz'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'lala lane 9002'}], 'entityType': 'PERSON', 'legalName': 'person-four', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS','relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_email_match_partial_2',
     {'value': 'xyz@'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'lala lane 9002'}], 'entityType': 'PERSON', 'legalName': 'person-four', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS','relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': 'xyz@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_email_no_match', {'value': 'xy.xyz@email.com'}, {}, []),
    ('test_email_and_name_1',
     {'value': 'person abcd@email.com'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_and_name_2',
     {'value': 'abcd@email.com person'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_and_name_3',
     {'value': 'person abcd@email.com one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_domain_and_name',
     {'value': 'abc person @email. com'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_and_name_partial',
     {'value': 'person ab'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_and_name_fuzzy_1',
     {'value': 'person abcm@email.com'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_and_name_fuzzy_2',
     {'value': 'persan abcd@emoil.com'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': 'abcd@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_email_fuzzy_no_match',
     {'value': 'abcm@emoil.com'},
     {},
     []
    )
])
def test_search(app, session, client, jwt, monkeypatch, test_name, query, categories, expected):
    """Assert that the entities search call works returns successfully."""
    # test setup
    if test_name == 'test_basic':
        # setup solr data for test (only needed the first time)
        solr_temp.delete_all_docs()
        time.sleep(1)
        solr_temp.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)
    # add test dependent synonyms to db
    SolrSynonymList(synonym='bc', synonym_list=['british columbia', 'bc'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='british columbia', synonym_list=['british columbia', 'bc'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='united states', synonym_list=['us', 'united states'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='us', synonym_list=['us', 'united states'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='chute', synonym_list=['chute', 'shoot'], synonym_type=SolrSynonymType.NAME).save()
    # setup products mock in validator
    monkeypatch.setattr('bor_api.utils.request_validators.account_products', lambda *args, **kwargs: [{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories

    # call search
    resp = client.post(f'/api/v1/search/extended',
                        data=json.dumps(payload),
                        headers=create_header(jwt,[BASIC_USER], **{'Accept-Version': 'v1',
                                                                    'content-type': 'application/json',
                                                                    'Account-Id': 1}))
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets']
    assert resp_json['searchResults']
    results = resp_json['searchResults']['results']
    assert resp_json['searchResults']['totalResults'] == len(expected)
    for result in results:
        del result['score']
    assert results == expected


def test_search_xlsx(app, session, client, jwt, requests_mock):
    """Assert that the entities search call works returns successfully."""
    # setup mocks
    account_id = 1
    requests_mock.get(f"{app.config.get('AUTH_SVC_URL')}/orgs/{account_id}/products?include_hidden=true",
                      json=[{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    doc = {'entityAddresses': [{'addressCity': 'Victoria',
                                'addressCountry': 'Canada',
                                'addressRegion': 'BC',
                                'addressType': 'DELIVERY',
                                'postalCode': 'T3R 43R',
                                'score': 0.0,
                                'streetAddress': 'charles place 4W2'}],
           'entityType': 'PERSON',
           'legalName': 'persons two',
           'roles': [{'relatedBN': 'BN00012334',
                      'relatedEmail': 'abcd@email.com',
                      'relatedEntityType': 'BUSINESS',
                      'relatedIdentifier': 'CP1234567',
                      'relatedLegalType': 'CP',
                      'relatedName': 'test 1234',
                      'relatedState': 'ACTIVE',
                      'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}],
                      'roleType': 'DIRECTOR',
                      'score': 0.0}]}

    requests_mock.post(f"{app.config.get('TEMP_SOLR_SVC_URL')}/bo/query",json={'response': {'docs': [doc], 'numFound': 1, 'start': 0}})
    # format payload
    payload = {'query': {'value': 'persons two'}}
    # call search
    resp = client.post(f'/api/v1/search/extended',
                       data=json.dumps(payload),
                       headers=create_header(jwt,[BASIC_USER], **{'Accept-Version': 'v1',
                                                                  'content-type': 'application/json',
                                                                  'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                                  'Account-Id': account_id}))
    # test
    assert resp.status_code == HTTPStatus.OK
    assert resp.data


def test_search_error(app, session, client, jwt, monkeypatch, requests_mock):
    """Assert that the entities search call error handling works as expected."""
    # setup products mock in validator
    monkeypatch.setattr('bor_api.utils.request_validators.account_products', lambda *args, **kwargs: [{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    # setup solr mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('TEMP_SOLR_SVC_URL')}/bo/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # create payload
    payload = {'query': {'value': '123'}}
    # call search
    resp = client.post(f'/api/v1/search/extended',
                       data=json.dumps(payload),
                       headers=create_header(jwt,[BASIC_USER], **{'Accept-Version': 'v1',
                                                                  'content-type': 'application/json',
                                                                  'Account-Id': 1}))
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get('detail') == f'{mocked_error_msg}, {mocked_status_code}'
    assert resp_json.get('message') == 'Solr service error while processing request.'


@pytest.mark.parametrize('test_name,query,categories,headers,errors', [
    ('test_no_value', {}, {}, {}, [{'Invalid payload': "Expected a string for 'value'."}]),
    ('test_invalid_accept_headers', {'value': 'a'}, {}, {'Accept': 'application/pdf'}, [{'Invalid header': 'Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf'}]),
    ('test_invalid_query_and_headers', {}, {}, {'Accept': 'application/pdf'}, [{'Invalid payload': "Expected a string for 'value'."}, {'Invalid header': 'Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf'}]),
])
def test_search_bad_request(app, session, client, jwt, monkeypatch, test_name, query, categories, headers, errors):
    """Assert that the entities search call validates the payload."""
    # setup products mock in validator
    monkeypatch.setattr('bor_api.utils.request_validators.account_products', lambda *args, **kwargs: [{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    # create payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/extended',
                       data=json.dumps(payload),
                       headers=create_header(jwt,[BASIC_USER], **{'Accept-Version': 'v1',
                                                                  'content-type': 'application/json',
                                                                  'Account-Id': 1,
                                                                  **headers}))
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get('message') == 'Errors processing request.'
    assert resp_json.get('details') == errors
