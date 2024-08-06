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
"""Test-Suite to ensure that the parties search endpoints/functions work as expected."""
import time
from http import HTTPStatus

import pytest

from search_api.services import business_solr
from search_api.services.business_solr.doc_fields import PartyField

from tests import integration_solr
from tests.unit.utils import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,query,categories', [
    ('test_basic', {'value': '123'}, {PartyField.PARTY_ROLE.value: ['partner','proprietor']}),
    ('test_filters',
     {'value': 'test filters', PartyField.PARENT_NAME.value: 'name', PartyField.PARENT_IDENTIFIER.value: 'BC23', PartyField.PARENT_BN.value: '023'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']}
    ),
    ('test_categories',
     {'value': 'test categories'},
     {PartyField.PARENT_STATE.value:['ACTIVE'], PartyField.PARENT_TYPE.value: ['BC', 'CP', 'SP'], PartyField.PARTY_ROLE.value: ['partner','proprietor']}
    ),
    ('test_all_combined',
     {
        'value': 'test all combined',
        PartyField.PARENT_NAME.value: 'name',
        PartyField.PARENT_IDENTIFIER.value: 'BC23',
        PartyField.PARENT_BN.value: '023'
     },
     {
        PartyField.PARENT_STATE.value: ['ACTIVE'],
        PartyField.PARENT_TYPE.value: ['BC', 'CP', 'SP'],
        PartyField.PARTY_ROLE.value: ['partner','proprietor']
     })
])
def test_parties_solr_mock(app, session, client, requests_mock, test_name, query, categories):
    """Assert that the parties search call works returns successfully."""
    # setup mocks
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # call search
    resp = client.post('/api/v2/search/parties',
                       headers={'content-type': 'application/json'},
                       json={'query': query, 'categories': categories})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets'] == {'fields': {}}
    assert resp_json['searchResults']['queryInfo']['rows'] == 10
    assert resp_json['searchResults']['queryInfo']['start'] == 0
    assert resp_json['searchResults']['results'] == []
    assert resp_json['searchResults']['totalResults'] == 0


@integration_solr
@pytest.mark.parametrize('test_name,query,categories,expected', [
    ('test_basic_name',  # NOTE: test setup checks for 'test_basic' on the first run
     {'value': 'person one'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_case',  # NOTE: test setup checks for 'test_basic' on the first run
     {'value': 'pErson ONE'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_partial_1',
     {'value': 'pers one'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_partial_2',
     {'value': 'erson one'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_partial_3',
     {'value': 'erso ne'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_spellcheck',
     {'value': 'parson one'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_mix',
     {'value': 'one person'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_mix_partial',
     {'value': 'ne erson'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_adv_chars',
     {'value': 'p*n o?e "one"'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_basic_name_._1',
     {'value': 'organization two y.z.'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentIdentifier': 'FM0004018', 'parentLegalType': 'GP', 'parentName': 'firm eleven 11 periods y.z. xk', 'parentStatus': 'ACTIVE', 'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization'}]
    ),
    ('test_basic_name_._2',
     {'value': 'organization two yz'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentIdentifier': 'FM0004018', 'parentLegalType': 'GP', 'parentName': 'firm eleven 11 periods y.z. xk', 'parentStatus': 'ACTIVE', 'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization'}]
    ),
    ('test_basic_name_._3',
     {'value': 'organization two x.k.'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentIdentifier': 'FM0004018', 'parentLegalType': 'GP', 'parentName': 'firm eleven 11 periods y.z. xk', 'parentStatus': 'ACTIVE', 'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization'}]
    ),
    ('test_basic_name_._4',
     {'value': 'organization two xk'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentIdentifier': 'FM0004018', 'parentLegalType': 'GP', 'parentName': 'firm eleven 11 periods y.z. xk', 'parentStatus': 'ACTIVE', 'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization'}]
    ),
    ('test_basic_no_match', {'value': 'zzz no match here qljrb'}, {PartyField.PARTY_ROLE.value: ['partner','proprietor']},[]),
    ('test_filters_name',
     {'value': 'person', PartyField.PARENT_NAME.value: 'nine'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_filters_no_match',
     {'value': 'person', PartyField.PARENT_NAME.value: 'three'},
     {PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     []
    ),
    ('test_categories_state',
     {'value': 'person'},
     {PartyField.PARENT_TYPE.value: ['SP'], PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    ),
    ('test_categories_no_match',
     {'value': 'person'},
     {PartyField.PARENT_TYPE.value: ['BEN'], PartyField.PARTY_ROLE.value: ['partner','proprietor']},
     []
    ),
    ('test_all_combined',
     {
        'value': 'person',
        PartyField.PARENT_NAME.value: 'nine',
        PartyField.PARENT_IDENTIFIER.value: 'FM1000028',
        PartyField.PARENT_BN.value: '123',
     },
     {
        PartyField.PARENT_STATE.value: ['ACTIVE'],
        PartyField.PARENT_TYPE.value: ['SP'],
        PartyField.PARTY_ROLE.value: ['partner','proprietor']
     },
     [{'parentBN': '123', 'parentIdentifier': 'FM1000028', 'parentLegalType': 'SP', 'parentName': 'firm nine 9 special + match', 'parentStatus': 'ACTIVE', 'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person'}]
    )
])
def test_parties(app, session, client, test_name, query, categories, expected):
    """Assert that the parties search call works returns successfully."""
    # test setup
    if test_name == 'test_basic_name':
        # setup solr data for test (only needed the first time)
        business_solr.delete_all_docs()
        time.sleep(1)
        business_solr.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)

    # call search
    resp = client.post('/api/v2/search/parties',
                       headers={'content-type': 'application/json'},
                       json={'query': query, 'categories': categories})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets']
    assert resp_json['searchResults']
    results = resp_json['searchResults']['results']
    assert resp_json['searchResults']['totalResults'] == len(expected)
    assert results == expected


def test_search_error(app, session, client, requests_mock):
    """Assert that the parties search call error handling works as expected."""
    # setup solr error mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # call search
    resp = client.post('/api/v2/search/parties',
                       headers={'content-type': 'application/json'},
                       json={'query': {'value':'test'}, 'categories': {'partyRoles': ['partner','proprietor']}})
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get('detail') == f'{mocked_error_msg}, {mocked_status_code}'
    assert resp_json.get('message') == 'Solr service error while processing request.'


@pytest.mark.parametrize('test_name,payload,errors', [
    ('test_no_query', {}, [{'Invalid payload': "Expected an object for 'query'."}]),
    ('test_invalid_query', {'query': 'wrong'}, [{'Invalid payload': "Expected an object for 'query'."}]),
    ('test_no_value', {'query': {'notValue': 'bla'}}, [{'Invalid payload': "Expected a string for 'query/value'."}]),
    ('test_invalid_value', {'query': {'value': 1}}, [{'Invalid payload': "Expected a string for 'query/value'."}]),
    ('test_no_partyRoles',
     {'query': {'value': 'test'}, 'categories': {'noPartyRoles': ['partner']}},
     [{'Invalid payload': "Expected 'categories/partyRoles:[...]'."}]),
    ('test_invalid_partyRoles',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['director']}},
     [{'Invalid payload': "Expected 'categories/partyRoles:' with values 'partner' and/or 'proprietor'. Other party roles are not available."}]),
    ('test_invalid_category',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': 'partner'}},
     [{'Invalid payload': "Expected a list for 'categories/partyRoles'."}]),
    ('test_invalid_start_1',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['partner']}, 'start': -10},
     [{'Invalid payload': "Expected 'start' to be >= 0."}]),
    ('test_invalid_start_2',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['partner']}, 'start': 'lala'},
     [{'Invalid payload': "Expected integer for params: 'start', 'rows'"}]),
    ('test_invalid_rows_1',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['partner']}, 'rows': -22},
     [{'Invalid payload': "Expected 'rows' to be between 0 and 10000."}]),
    ('test_invalid_rows_2',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['partner']}, 'rows': 200000},
     [{'Invalid payload': "Expected 'rows' to be between 0 and 10000."}]),
    ('test_invalid_rows_2',
     {'query': {'value': 'test'}, 'categories': {'partyRoles': ['partner']}, 'rows': '&899'},
     [{'Invalid payload': "Expected integer for params: 'start', 'rows'"}]),
])
def test_search_bad_request(app, session, client, test_name, payload, errors):
    """Assert that the business search call validates the payload."""
    # call search
    resp = client.post('/api/v2/search/parties',
                       headers={'content-type': 'application/json'},
                       json=payload)
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get('message') == 'Errors processing request.'
    assert resp_json.get('details') == errors
