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
from bor_api.services.authz import BASIC_USER
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField

from tests import integration_solr
from tests.unit.test_utils import SOLR_TEST_DOCS, create_header


@pytest.mark.parametrize('test_name,query,categories', [
    ('test_basic', {'value': '123'}, {}),
    ('test_filters',
     {'value': 'test filters', EntityField.LEGAL_NAME.value: 'name', EntityField.IDENTIFIER.value: 'BC23', EntityField.BN.value: '023'},
     {}
    ),
    ('test_categories',
     {'value': 'test categories'},
     {EntityField.ENTITY_TYPE.value: ['BUSINESS'], EntityField.STATE.value:['ACTIVE'], EntityField.LEGAL_TYPE.value: ['BC', 'CP', 'SP']}
    ),
    ('test_child_filters', {
        'value': 'test child filters',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name',
            'value': 'CP4332 0424 related name'
        }
     },{}
    ),
    ('test_child_categories',
     {'value': 'test child categories'},
     {
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
        EntityField.LEGAL_NAME.value: 'name',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name',
            'value': 'CP4332 0424 related name'
        }
     },
     {
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
    requests_mock.post(f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories
    # call search
    resp = client.post(f'/api/v1/search/public',
                       data=json.dumps(payload),
                       headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets'] == {'fields': {}}
    assert resp_json['searchResults']['queryInfo']['categories'] == {
        'roles': {
            'active': [True],
            'relatedEntityType': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_ENTITY_TYPE.value, None),
            'relatedState': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_STATE.value, None),
            'roleType': categories.get(EntityField.ROLES.value, {}).get(EntityRoleField.ROLE_TYPE.value, None)
        }
    }
    assert resp_json['searchResults']['queryInfo']['query'] == {
        'legalName': query.get(EntityField.LEGAL_NAME.value, ''),
        'roles': {
            'relatedBN': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_BN.value, ''),
            'relatedIdentifier': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_IDENTIFIER.value, '').lower(),
            'relatedName': query.get(EntityField.ROLES.value, {}).get(EntityRoleField.RELATED_NAME.value, ''),
            'value': query.get(EntityField.ROLES.value, {}).get('value', '').lower()},
        'value': query['value']
    }
    assert resp_json['searchResults']['queryInfo']['rows'] == 10
    assert resp_json['searchResults']['queryInfo']['start'] == 0
    assert resp_json['searchResults']['results'] == []
    assert resp_json['searchResults']['totalResults'] == 0


@integration_solr
@pytest.mark.parametrize('test_name,query,categories,expected', [
    ('test_basic',  # NOTE: test setup checks for 'test_basic' on the first run
     {'value': 'person ten'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_1',
     {'value': 'per ten'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_2',
     {'value': 'erson te'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_partial_3',
     {'value': 'er ine'},
     {},
     [{'birthDate': '1999', 'entityType': 'PERSON', 'legalName': 'person nine', 'nationalities': ['CA'], 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spellcheck',
     {'value': 'pirson nane'},
     {},
     [{'birthDate': '1999', 'entityType': 'PERSON', 'legalName': 'person nine', 'nationalities': ['CA'], 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_1',
     {'value': 'persons ten'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_2',
     {'value': 'personing ten'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_stem_3',
     {'value': 'personed ten'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix',
     {'value': 'ten person'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_partial',
     {'value': 'te pers'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_mix_stem',
     {'value': 'ten persons'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_adv_chars',
     {'value': 'p*n t?n "ten"'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_spec_char',
     {'value': 'p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:\'",<>./'},
     {},
     [{'birthDate': '1988', 'entityType': 'PERSON', 'legalName': 'p!e(rs)on e}l{ev-en ~`@#$%^-_=[]|\\;:\'",<>./', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_and',
     {'value': 'person and'},
     {},
     [{'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]}, 
      {'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_&',
     {'value': 'person &'},
     {},
     [{'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_and_+',
     {'value': 'person +'},
     {},
     [{'entityType': 'PERSON', 'legalName': 'person and 5', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityType': 'PERSON', 'legalName': 'person&six', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]},
      {'entityType': 'PERSON', 'legalName': 'person+seven', 'roles': [{'relatedBN': '09876K', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP0234567', 'relatedLegalType': 'CP', 'relatedName': 'tester 1111', 'relatedState': 'HISTORICAL', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_._1',
     {'value': 'person ten y.z.'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_._2',
     {'value': 'person ten yz'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_._3',
     {'value': 'person ten x.k.'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_name_match_._4',
     {'value': 'person ten xk'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_basic_historic_no_match', {'value': 'person eight'}, {}, []),
    ('test_basic_address_no_match', {'value': 'way walaby'}, {}, []),
    ('test_basic_rel_email_no_match', {'value': 'person xyz@email.com'}, {}, []),
    ('test_basic_email_no_match', {'value': 'nine@si9.com'}, {}, []),
    ('test_basic_tax_number_no_match', {'value': '705 362 853'}, {}, []),
    ('test_basic_alt_name_no_match', {'value': 'significant individual alt'}, {}, []),
    ('test_basic_no_match', {'value': 'zzz no match here qljrb'}, {},[]),
    ('test_filters_person',
     {'value': 'person', EntityField.LEGAL_NAME.value: 'nine'},
     {},
     [{'birthDate': '1999', 'entityType': 'PERSON', 'legalName': 'person nine', 'nationalities': ['CA'], 'roles': [{'relatedBN': '124221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0000007', 'relatedLegalType': 'BEN', 'relatedName': 'lots of words in here', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_filters_alt_name_no_effect',
     {'value': 'person ten', 'name': 'alalalala ble blap zzzz ignored'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_filters_info_no_effect',
     {'value': 'person ten', 'info': 'nine@si9.com 705 362 853 zzzzz ignored'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_filters_tax_number_no_effect',
     {'value': 'person ten', EntityField.TAX_NUMBER.value: '705 362 853 zzzzzz ignored'},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_filters_no_match',
     {'value': 'person', EntityField.LEGAL_NAME.value: 'name'},
     {},
     []
    ),
    ('test_child_filters_all_combined',
     {
        'value': 'person one',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '123',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP123',
            EntityRoleField.RELATED_NAME.value: 'test',
            'value': 'CP123 test'
        }
     },
     {},
     [{'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_value',
     {
        'value': 'person one',
        EntityField.ROLES.value: {'value': 'CP123 test'}
     },
     {},
     [{'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_all_combined',
     {
        'value': 'person one',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '123',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP123',
            EntityRoleField.RELATED_NAME.value: 'test',
            'value': 'CP123 test'
        }
     },
     {},
     [{'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_filters_address_no_effect',
     {
        'value': 'person ten',
        EntityField.ENTITY_ADDRESSES.value: 'victoria canada walaby way 1112 T3S 1E4'
     },
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_child_filters_related_email_no_effect',
     {'value': 'person ten', EntityField.ROLES.value: {EntityRoleField.RELATED_EMAIL.value:"5555"}},
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_child_filters_role_dates_no_effect',
     {
        'value': 'person ten',
        EntityField.ROLES.value: {
            EntityRoleField.ROLE_DATES.value:{DateRangeField.END.value: '2017-05-10', DateRangeField.START.value: '2014-01-28'},
        }
     },
     {},
     [{'birthDate': '1954', 'entityType': 'PERSON', 'legalName': 'person ten y.z. xk', 'nationalities': ['CA'], 'roles': [{'relatedBN': '1255323221', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'BC0020047', 'relatedLegalType': 'BEN', 'relatedName': 'NOt Case SENSitive', 'relatedState': 'ACTIVE', 'roleType': 'SIGNIFICANT INDIVIDUAL', 'score': 0.0}]}]
    ),
    ('test_child_filters_no_match',
     {
        'value': 'person',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '0424',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP4332',
            EntityRoleField.RELATED_NAME.value: 'related name'
        }
     },
     {},
     []
    ),
    ('test_child_categories',
     {'value': 'person'},
     {
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     [
        {'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_categories_addresses_no_effect',
     {'value': 'person'},
     {
        EntityField.ENTITY_ADDRESSES.value: {
            AddressField.ADDRESS_COUNTRY.value:['Canada'],
            AddressField.ADDRESS_REGION.value: ['ON', 'AB']
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     [
        {'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_categories_interests_no_effect',
     {'value': 'person'},
     {
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_INTERESTS.value: ['controlType.sharesOrVotes.registeredOwner'],
        },
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR', 'INCORPORATOR']
        }
     },
     [
        {'entityType': 'PERSON', 'legalName': 'person one', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]},
        {'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    ),
    ('test_child_categories_no_match',
     {'value': 'person'},
     {
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['PERSON'],
            EntityRoleField.ROLE_TYPE.value: ['OOPS']
        }
     },
     []
    ),
    ('test_synonym_name',
     {'value': 'person three chute'},
     {},
     [{'entityType': 'PERSON', 'legalName': 'personing three shoot', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}],
    ),
    ('test_all_combined_person',
     {
        'value': 'person',
        EntityField.LEGAL_NAME.value: 'two',
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_BN.value: '123',
            EntityRoleField.RELATED_IDENTIFIER.value: 'CP123',
            EntityRoleField.RELATED_NAME.value: 'test',
            'value': 'CP123 test'
        }
     },
     {
        EntityField.ENTITY_TYPE.value: ['PERSON'],
        EntityField.ROLES.value: {
            EntityRoleField.RELATED_STATE.value: ['ACTIVE'],
            EntityRoleField.RELATED_ENTITY_TYPE.value: ['BUSINESS'],
            EntityRoleField.ROLE_TYPE.value: ['DIRECTOR']
        }
     },
     [{'entityType': 'PERSON', 'legalName': 'persons two', 'roles': [{'relatedBN': 'BN00012334', 'relatedEntityType': 'BUSINESS', 'relatedIdentifier': 'CP1234567', 'relatedLegalType': 'CP', 'relatedName': 'test 1234', 'relatedState': 'ACTIVE', 'roleType': 'DIRECTOR', 'score': 0.0}]}]
    )
])
def test_search(app, session, client, jwt, monkeypatch, test_name, query, categories, expected):
    """Assert that the entities search call works returns successfully."""
    # test setup
    if test_name == 'test_basic':
        # setup solr data for test (only needed the first time)
        solr.delete_all_docs()
        time.sleep(1)
        solr.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)
    # add test dependent name synonyms to db
    SolrSynonymList(synonym='chute', synonym_list=['chute', 'shoot'], synonym_type=SolrSynonymType.NAME).save()
    # setup products mock in validator
    monkeypatch.setattr('bor_api.utils.request_validators.account_products', lambda *args, **kwargs: [{'code': 'NDS', 'subscriptionStatus': 'ACTIVE'}])
    # format payload
    payload = {'query': query}
    if categories:
        payload['categories'] = categories

    # call search
    resp = client.post(f'/api/v1/search/public',
                       data=json.dumps(payload),
                       headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets']
    assert resp_json['searchResults']
    results = resp_json['searchResults']['results']
    assert resp_json['searchResults']['totalResults'] == len(expected)
    for result in results:
        del result['score']
        assert result.get(EntityField.LEGAL_NAME.value)
        # tax info should not be visible from this search
        assert not result.get(EntityField.TAX_NUMBER.value)
        assert not result.get(EntityField.TAX_RESIDENCIES.value)
        # personal email should not be visible from this search
        assert not result.get(EntityField.EMAIL.value)
        # addresses should never be visible from this search
        assert not result.get(EntityField.ENTITY_ADDRESSES.value)
        # birthdate should only show the year
        assert not len(result.get(EntityField.BIRTH_DATE.value, '')) > 4

    assert results == expected


def test_search_error(app, session, client, jwt, monkeypatch, requests_mock):
    """Assert that the entities search call error handling works as expected."""
    # setup solr mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # create payload
    payload = {'query': {'value': '123'}}
    # call search
    resp = client.post(f'/api/v1/search/public',
                       data=json.dumps(payload),
                       headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
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
    resp = client.post(f'/api/v1/search/public',
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


def test_search_nationalities_only_ca_returned(app, session, client, jwt, requests_mock):
    """Assert access is granted/denied based on having the right product subscription."""
    # setup mocks
    requests_mock.post(f"{app.config.get('SOLR_SVC_LEADER_URL')}/bor/query", json={'response': {'docs': [{'nationalities': ['CA', 'US']}], 'numFound': 0, 'start': 0}})
    # call search
    resp = client.post(f'/api/v1/search/public',
                       data=json.dumps({'query': {'value': 'a'}}),
                       headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
    # test
    assert resp.status_code == HTTPStatus.OK
    assert resp.json['searchResults']['results'][0]['nationalities'] == ['CA']


def test_search_fields(app, session, client):
    """Assert the fields for data requested are set correctly for the public endpoint."""
    solr_url = f"{app.config.get('SOLR_SVC_FOLLOWER_URL')}/{app.config.get('SOLR_SVC_FOLLOWER_CORE')}/query"

    with requests_mock.mock() as m:
        m.post(solr_url, json={'response': {'docs': []}})

        # call search
        resp = client.post(f'/api/v1/search/public',
                        data=json.dumps({'query': {'value': 'a'}}),
                        headers={'Accept-Version': 'v1', 'content-type': 'application/json'})
        # test
        assert resp.status_code == HTTPStatus.OK
        assert m.called == True
        fields_requested = m.request_history[0].json()['fields']
        assert EntityField.TAX_NUMBER.value not in fields_requested
        assert EntityField.TAX_RESIDENCIES.value not in fields_requested
        assert EntityField.ENTITY_ADDRESSES.value not in fields_requested
        assert EntityField.EMAIL.value not in fields_requested
        assert fields_requested == ['birthDate', 'entityType', 'legalName', 'nationalities', 'roles', 'score', '[child]', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleType', 'relatedLegalType']
