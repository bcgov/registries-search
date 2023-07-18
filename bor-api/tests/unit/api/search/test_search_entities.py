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

import xlsxwriter

from bor_api.enums import SolrSynonymType
from bor_api.models import SolrSynonymList
from bor_api.services import bor_solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field

from tests import integration_solr
from tests.unit.utils import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,query,categories', [
    ('test_basic', {'value': '123'}, {}),
    ('test_filters',
     {'value': 'test filters', Field.LEGAL_NAME.value: 'name', Field.IDENTIFIER.value: 'BC23', Field.BN.value: '023'},
     {}
    ),
    ('test_categories',
     {'value': 'test categories'},
     {Field.ENTITY_TYPE.value: ['BUSINESS'], Field.STATE.value:['ACTIVE'], Field.LEGAL_TYPE.value: ['BC', 'CP', 'SP']}
    ),
    ('test_child_filters', {
        'value': 'test child filters',
        Field.ENTITY_ADDRESSES.value: 'vancouver bc',
        Field.ROLES.value: {
            Field.RELATED_BN.value: '0424',
            Field.RELATED_EMAIL.value: '1234',
            Field.RELATED_IDENTIFIER.value: 'CP4332',
            Field.RELATED_NAME.value: 'related name',
            Field.ROLE_DATES.value:{Field.END.value: '2022-05-10', Field.START.value: '2020-01-28'},
            'value': 'CP4332 0424 related name'
        }
     },{}
    ),
    ('test_child_categories',
     {'value': 'test child categories'},
     {
        Field.ENTITY_ADDRESSES.value: {
            Field.ADDRESS_CITY.value: ['VANCOUVER', 'VICTORIA'],
            Field.ADDRESS_COUNTRY.value:['Canada'],
            Field.ADDRESS_REGION.value: ['British Columbia', 'Alberta']
        },
        Field.ROLES.value: {
            Field.RELATED_STATE.value: ['ACTIVE'],
            Field.RELATED_ENTITY_TYPE.value: ['PERSON', 'BUSINESS'],
            Field.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     }
    ),
    ('test_all_combined',
     {
        'value': 'test all combined',
        Field.LEGAL_NAME.value: 'name',
        Field.IDENTIFIER.value: 'BC23',
        Field.BN.value: '023',
        Field.ENTITY_ADDRESSES.value: 'vancouver bc',
        Field.ROLES.value: {
            Field.RELATED_BN.value: '0424',
            Field.RELATED_EMAIL.value: '1234',
            Field.RELATED_IDENTIFIER.value: 'CP4332',
            Field.RELATED_NAME.value: 'related name',
            Field.ROLE_DATES.value:{Field.END.value: '2022-05-10', Field.START.value: '2020-01-28'},
            'value': 'CP4332 0424 related name'
        }
     },
     {
        Field.ENTITY_TYPE.value: ['BUSINESS'],
        Field.STATE.value:['ACTIVE'],
        Field.LEGAL_TYPE.value: ['BC', 'CP', 'SP'],
        Field.ENTITY_ADDRESSES.value: {
            Field.ADDRESS_CITY.value: ['VANCOUVER', 'VICTORIA'],
            Field.ADDRESS_COUNTRY.value:['Canada'],
            Field.ADDRESS_REGION.value: ['British Columbia', 'Alberta']
        },
        Field.ROLES.value: {
            Field.RELATED_STATE.value: ['ACTIVE'],
            Field.RELATED_ENTITY_TYPE.value: ['PERSON', 'BUSINESS'],
            Field.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     })
])
def test_search_entities_solr_mock(app, session, client, requests_mock, test_name, query, categories):
    """Assert that the entities search call works returns successfully."""
    # setup solr mock
    requests_mock.post(f"{app.config.get('SOLR_SVC_URL')}/bor/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/entities', data=json.dumps(payload), headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets'] == {'fields': {}}
    assert resp_json['searchResults']['queryInfo']['categories'] == {
        'entityAddresses': {
            'addressCity': categories.get(Field.ENTITY_ADDRESSES.value, {}).get(Field.ADDRESS_CITY.value, None),
            'addressCountry': categories.get(Field.ENTITY_ADDRESSES.value, {}).get(Field.ADDRESS_COUNTRY.value, None),
            'addressRegion': categories.get(Field.ENTITY_ADDRESSES.value, {}).get(Field.ADDRESS_REGION.value, None)},
        'entityType': categories.get(Field.ENTITY_TYPE.value, None),
        'legalType': categories.get(Field.LEGAL_TYPE.value, None),
        'roles': {
            'relatedEntityType': categories.get(Field.ROLES.value, {}).get(Field.RELATED_ENTITY_TYPE.value, None),
            'relatedState': categories.get(Field.ROLES.value, {}).get(Field.RELATED_STATE.value, None),
            'roleType': categories.get(Field.ROLES.value, {}).get(Field.ROLE_TYPE.value, None)
        },
        'state': categories.get(Field.STATE.value, None)
    }
    assert resp_json['searchResults']['queryInfo']['query'] == {
        'bn': query.get(Field.BN.value, ''),
        'entityAddresses': query.get(Field.ENTITY_ADDRESSES.value, ''),
        'identifier': query.get(Field.IDENTIFIER.value, '').lower(),
        'legalName': query.get(Field.LEGAL_NAME.value, ''),
        'roles': {
            'relatedBN': query.get(Field.ROLES.value, {}).get(Field.RELATED_BN.value, ''),
            'relatedEmail': query.get(Field.ROLES.value, {}).get(Field.RELATED_EMAIL.value, ''),
            'relatedIdentifier': query.get(Field.ROLES.value, {}).get(Field.RELATED_IDENTIFIER.value, '').lower(),
            'relatedName': query.get(Field.ROLES.value, {}).get(Field.RELATED_NAME.value, ''),
            'roleDates': query.get(Field.ROLES.value, {}).get(Field.ROLE_DATES.value, {}),
            'value': query.get(Field.ROLES.value, {}).get('value', '').lower()},
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
     [{'bn': 'BN00012334', 'email': '1234@email.com', 'entityType': 'BUSINESS', 'identifier': 'CP1234567', 'legalName': 'test 1234', 'legalType': 'CP', 'state': 'ACTIVE'}, {'bn': 'BN00012334', 'email': '2222@email.com', 'entityType': 'BUSINESS', 'identifier': 'CP0034567', 'legalName': 'tests 2222', 'legalType': 'CP', 'state': 'ACTIVE'}],
    ),
    ('test_basic_name_match_exact',
     {'value': 'person one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_1',
     {'value': 'per one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_2',
     {'value': 'erson tw'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_3',
     {'value': 'er tw'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spellcheck',
     {'value': 'pirson ttree'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_1',
     {'value': 'persons one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_2',
     {'value': 'personing one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_3',
     {'value': 'personed one'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix',
     {'value': 'one person'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_partial',
     {'value': 'tw pers'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_stem',
     {'value': 'one persons'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spec_char',
     {'value': '*person! [one]'},
     {},[{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]),
    ('test_basic_name_match_and_and',
     {'value': 'person and'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_&',
     {'value': 'person &'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_+',
     {'value': 'person +'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}, {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEmail': '1111@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2021-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_address_match',
     {'value': 'walaby way'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_partial',
     {'value': 'waleby way'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_mix',
     {'value': 'way walaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_address_match_mix_partial',
     {'value': 'way wilaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_name_and_address_match_partial',
     {'value': 'pirson way wilaby'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_basic_no_match', {'value': 'zzz no match here qljrb'}, {},[]),
    ('test_filters',
     {'value': 'test', Field.LEGAL_NAME.value: 'test 1234', Field.IDENTIFIER.value: 'CP123', Field.BN.value: 'BN00'},
     {},
     [{'bn': 'BN00012334', 'email': '1234@email.com', 'entityType': 'BUSINESS', 'identifier': 'CP1234567', 'legalName': 'test 1234', 'legalType': 'CP', 'state': 'ACTIVE'}]
    ),
    ('test_filters_no_match',
     {'value': 'test filters', Field.LEGAL_NAME.value: 'name', Field.IDENTIFIER.value: 'BC23', Field.BN.value: '023'},
     {},
     []
    ),
    ('test_categories',
     {'value': 'tests 2222'},
     {Field.ENTITY_TYPE.value: ['BUSINESS'], Field.STATE.value:['ACTIVE'], Field.LEGAL_TYPE.value: ['BC', 'CP', 'SP']},
     [{'bn': 'BN00012334', 'email': '2222@email.com', 'entityType': 'BUSINESS', 'identifier': 'CP0034567', 'legalName': 'tests 2222', 'legalType': 'CP', 'state': 'ACTIVE'}]
    ),
    ('test_categories_no_match',
     {'value': 'test 1234'},
     {Field.ENTITY_TYPE.value: ['BUSINESS'], Field.STATE.value:['ACTIVE'], Field.LEGAL_TYPE.value: ['BC', 'GP', 'SP']},
     []
    ),
    ('test_child_filters',
     {
        'value': 'person one',
        Field.ENTITY_ADDRESSES.value: 'victoria canada',
        Field.ROLES.value: {
            Field.RELATED_BN.value: '123',
            Field.RELATED_IDENTIFIER.value: 'CP123',
            Field.RELATED_NAME.value: 'test',
            Field.ROLE_DATES.value:{Field.END.value: '2023-05-10', Field.START.value: '2020-01-28'},
            'value': 'CP123 test'
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_value',
     {
        'value': 'person one',
        Field.ENTITY_ADDRESSES.value: 'victoria brit col',
        Field.ROLES.value: {'value': 'CP123 test'}
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_1',
     {
        'value': 'person',
        Field.ROLES.value: {
            Field.ROLE_DATES.value:{Field.END.value: '2017-05-10', Field.START.value: '2014-01-28'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_2',
     {
        'value': 'person',
        Field.ROLES.value: {
            Field.ROLE_DATES.value:{Field.END.value: '2015-08-04', Field.START.value: '2014-01-28'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_3',
     {
        'value': 'person',
        Field.ROLES.value: {
            Field.ROLE_DATES.value:{Field.END.value: '2017-08-04', Field.START.value: '2015-09-05'},
        }
     },
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_role_dates_4',
     {
        'value': 'person',
        Field.ROLES.value: {
            Field.ROLE_DATES.value:{Field.END.value: '2015-08-03', Field.START.value: '2014-09-05'},
        }
     },
     {},
     []
    ),
    ('test_child_filters_related_email_1',
     {'value': 'person', Field.ROLES.value: {Field.RELATED_EMAIL.value:"2222"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_2',
     {'value': 'person', Field.ROLES.value: {Field.RELATED_EMAIL.value:"2222@email.com"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_3',
     {'value': 'person', Field.ROLES.value: {Field.RELATED_EMAIL.value:"2@email.com"}},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_4',
     {'value': 'person', Field.ROLES.value: {Field.RELATED_EMAIL.value:"+em-ail: \\ ~ ^ / ! || AND NOT && OR [] {} ()"}},
     {},
     []
    ),
    ('test_child_filters_no_match',
     {
        'value': 'person',
        Field.ENTITY_ADDRESSES.value: 'vancouver british colum',
        Field.ROLES.value: {
            Field.RELATED_BN.value: '0424',
            Field.RELATED_IDENTIFIER.value: 'CP4332',
            Field.RELATED_NAME.value: 'related name',
            Field.ROLE_DATES.value:{Field.END.value: '2022-05-10', Field.START.value: '2020-01-28'}
        }
     },
     {},
     []
    ),
    ('test_child_categories',
     {'value': 'person'},
     {
        Field.ENTITY_ADDRESSES.value: {
            Field.ADDRESS_COUNTRY.value:['Canada', 'United States'],
            Field.ADDRESS_REGION.value: ['BC', 'AB', 'WA']
        },
        Field.ROLES.value: {
            Field.RELATED_STATE.value: ['ACTIVE'],
            Field.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            Field.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     [
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3S 1E4', 'score': 0.0, 'streetAddress': 'walaby way 1112'}], 'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2020-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'V3R 1A4', 'score': 0.0, 'streetAddress': 'hello world 9002'}], 'entityType': 'PERSON', 'legalName': 'person eight', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '2222@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0034567', 'relatedLegalType': 'CP', 'relatedName': 'tests 2222', 'relatedState': 'ACTIVE', 'roleDates': [{'active': False, 'end': '2016-08-04T00:03:54Z', 'score': 0.0, 'start': '2015-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_categories_no_match',
     {'value': 'person'},
     {
        Field.ENTITY_ADDRESSES.value: {
            Field.ADDRESS_COUNTRY.value:['Canada'],
            Field.ADDRESS_REGION.value: ['ON', 'AB']
        },
        Field.ROLES.value: {
            Field.RELATED_STATE.value: ['ACTIVE'],
            Field.RELATED_ENTITY_TYPE.value: ['PERSON'],
            Field.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     []
    ),
    ('test_synonym_country',
     {'value': 'person three US'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_synonym_region',
     {'value': 'persons two bc'},
     {},
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_synonym_name',
     {'value': 'person three chute'},
     {},
     [{'entityAddresses': [{'addressCity': 'Seattle', 'addressCountry': 'United States', 'addressRegion': 'WA', 'addressType': 'DELIVERY', 'postalCode': 'V3R 4E4', 'score': 0.0, 'streetAddress': 'jerry lane 9002'}], 'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2018-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_all_combined_person',
     {
        'value': 'person CA bc',
        Field.LEGAL_NAME.value: 't',
        Field.ENTITY_ADDRESSES.value: 'charles place victoria british colu',
        Field.ROLES.value: {
            Field.RELATED_BN.value: '123',
            Field.RELATED_IDENTIFIER.value: 'CP123',
            Field.RELATED_NAME.value: 'test',
            Field.ROLE_DATES.value:{Field.END.value: '2022-05-10', Field.START.value: '2018-01-28'},
            'value': 'CP123 test'
        }
     },
     {
        Field.ENTITY_TYPE.value: ['PERSON'],
        Field.ENTITY_ADDRESSES.value: {
            Field.ADDRESS_COUNTRY.value:['Canada'],
            Field.ADDRESS_REGION.value: ['BC', 'AB']
        },
        Field.ROLES.value: {
            Field.RELATED_STATE.value: ['ACTIVE'],
            Field.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            Field.ROLE_TYPE.value: ['DIRECTOR']
        }
     },
     [{'entityAddresses': [{'addressCity': 'Victoria', 'addressCountry': 'Canada', 'addressRegion': 'BC', 'addressType': 'DELIVERY', 'postalCode': 'T3R 43R', 'score': 0.0, 'streetAddress': 'charles place 4W2'}], 'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEmail': '1234@email.com', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}], 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_all_combined_business',
     {
        'value': 'test',
        Field.LEGAL_NAME.value: '12',
        Field.IDENTIFIER.value: 'CP12',
        Field.BN.value: '123'
     },
     {
        Field.ENTITY_TYPE.value: ['BUSINESS'],
        Field.STATE.value:['ACTIVE'],
        Field.LEGAL_TYPE.value: ['BC', 'CP', 'SP']
     },
     [{'bn': 'BN00012334', 'email': '1234@email.com', 'entityType': 'BUSINESS', 'identifier': 'CP1234567', 'legalName': 'test 1234', 'legalType': 'CP', 'state': 'ACTIVE'}]
    )
])
def test_search_entities(session, client, test_name, query, categories, expected):
    """Assert that the entities search call works returns successfully."""
    # setup solr data for test
    bor_solr.delete_all_docs()
    time.sleep(1)
    bor_solr.create_or_replace_docs(SOLR_TEST_DOCS)
    time.sleep(2)
    # add test dependent synonyms to db
    SolrSynonymList(synonym='bc', synonym_list=['british columbia', 'bc'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='british columbia', synonym_list=['british columbia', 'bc'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='united states', synonym_list=['us', 'united states'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='us', synonym_list=['us', 'united states'], synonym_type=SolrSynonymType.ADDRESS).save()
    SolrSynonymList(synonym='chute', synonym_list=['chute', 'shoot'], synonym_type=SolrSynonymType.NAME).save()
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/entities', data=json.dumps(payload), headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
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


def test_search_entities_xlsx(app, session, client, requests_mock):
    """Assert that the entities search call works returns successfully."""
    # setup solr mock
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
                      'relatedEmail': '1234@email.com',
                      'relatedEntityType': 'BUSINESS',
                      'relatedIdentifier': 'CP1234567',
                      'relatedLegalType': 'CP',
                      'relatedName': 'test 1234',
                      'relatedState': 'ACTIVE',
                      'roleDates': [{'active': True, 'score': 0.0, 'start': '2019-08-04T00:03:54Z'}],
                      'roleType': 'DIRECTOR',
                      'score': 0.0}]}

    requests_mock.post(f"{app.config.get('SOLR_SVC_URL')}/bor/query",json={'response': {'docs': [doc], 'numFound': 1, 'start': 0}})
    # format payload
    payload = {'query': {'value': 'persons two'}}
    # call search
    resp = client.post(f'/api/v1/search/entities',
                       data=json.dumps(payload),
                       headers={'Accept-Version': 'v1',
                                'content-type': 'application/json',
                                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})
    # test
    assert resp.status_code == HTTPStatus.OK
    assert resp.data


def test_search_entities_error(app, session, client, requests_mock):
    """Assert that the entities search call error handling works as expected."""
    # setup solr mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('SOLR_SVC_URL')}/bor/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # create payload
    payload = {'query': {'value': '123'}}
    # call search
    resp = client.post(f'/api/v1/search/entities', data=json.dumps(payload), headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get('detail') == f'{mocked_error_msg}, {mocked_status_code}'
    assert resp_json.get('message') == 'Solr service error while processing request.'


@pytest.mark.parametrize('test_name,query,categories,headers,errors', [
    ('test_no_value', {}, {}, {}, [{'Invalid payload': "Expected a string for 'value'."}]),
    ('test_invalid_accept_headers', {'value': 'a'}, {}, {'Accept': 'application/pdf'}, [{'Invalid headers': 'Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf'}]),
    ('test_invalid_query_and_headers', {}, {}, {'Accept': 'application/pdf'}, [{'Invalid payload': "Expected a string for 'value'."}, {'Invalid headers': 'Invalid Accept header. Expected application/json or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet but received application/pdf'}]),
])
def test_search_entities_bad_request(client, test_name, query, categories, headers, errors):
    """Assert that the entities search call validates the payload."""
    # create payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/entities',
                       data=json.dumps(payload),
                       headers={'Accept-Version': 'v1', 'content-type': 'application/json', **headers})
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get('message') == 'Errors processing request.'
    assert resp_json.get('details') == errors
