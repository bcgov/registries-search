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
"""Test-Suite to ensure that the business search endpoints/functions work as expected."""
import time
from http import HTTPStatus

import pytest

from search_api.services import business_solr
from search_api.services.business_solr.doc_fields import BusinessField

from tests import integration_solr
from tests.unit.utils import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,names,identifiers,rows', [
    ('test_name', ['name'], [], 10),
    ('test_name_multiple', ['name1', 'name2'], [], 10),
    ('test_identifier', [], ['identifier'], 10),
    ('test_identifier_multiple', [], ['identifier1', 'identifier2'], 10),
    ('test_mix', ['name'], ['identifier'], 10),
    ('test_mix_multiple', ['name1', 'name2'], ['identifier1', 'identifier2'], 10),
])
def test_businesses_bulk_solr_mock(app, session, client, requests_mock, test_name, names, identifiers, rows):
    """Assert that the entities search call works returns successfully."""
    # setup mocks
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # call search
    resp = client.post('/api/v2/search/businesses/bulk',
                       headers={'content-type': 'application/json'},
                       json={'names': names, 'identifiers': identifiers, 'rows': rows})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['results'] == []
    assert resp_json['totalResults'] == 0


@integration_solr
@pytest.mark.parametrize('test_name,names,identifiers,expected', [
    ('test_name',  # NOTE: test setup checks for 'test_name' on the first run
     ['business one 1'],
     [],
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_name_multiple',
     ['business one 1', 'business two 2', 'business four 4'],
     [],
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'},
      {'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'},
      {'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_name_spec_char',
     ['b!u(si)ness fou}l{rt-een ~`@#$%^-_=[]|\\;:\'",<>./'],
     [],
     [{'bn': '123456776BC0001', 'identifier': 'BC0030014', 'legalType': 'BEN', 'name': 'b!u(si)ness fou}l{rt-een ~`@#$%^-_=[]|\\;:\'",<>./', 'status': 'ACTIVE'}]
    ),
    ('test_name_partial_no_match',
     ['usiness one'],
     ['34567'],
     []
    ),
    ('test_name_spellcheck_no_match',
     ['basiness two 2'],
     [],
     []
    ),
    ('test_name_stem_no_match',
     ['businesses two 2'],
     [],
     []
    ),
    ('test_name_swap_no_match',
     ['one business 1'],
     [],
     []
    ),
    ('test_identifier',
     [],
     ['CP1234567'],
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_identifier_multiple',
     [],
     ['CP1234567', 'CP0234567', 'BC0004567'],
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'},
      {'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'},
      {'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_mix',
     ['business two 2'],
     ['CP1234567'],
     [{'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'},
      {'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_mix_multiple',
     ['business two 2', 'business four 4'],
     ['CP1234567', 'CP0034567'],
     [{'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'},
      {'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'},
      {'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'},
      {'goodStanding': True, 'identifier': 'CP0034567', 'legalType': 'CP', 'name': 'business three 3', 'status': 'ACTIVE'}]
    ),
])
def test_businesses_bulk(app, session, client, test_name, names, identifiers, expected):
    """Assert that the business search call works returns successfully."""
    # test setup
    if test_name == 'test_name':
        # setup solr data for test (only needed the first time)
        business_solr.delete_all_docs()
        time.sleep(1)
        business_solr.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)

    # call search
    resp = client.post('/api/v2/search/businesses/bulk',
                       headers={'content-type': 'application/json'},
                       json={'names': names, 'identifiers': identifiers})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    results = resp_json['results']
    for result in results:
        del result['score']
    assert resp_json['totalResults'] == len(expected)
    assert results == expected


def test_search_bulk_error(app, session, client, requests_mock):
    """Assert that the business search call error handling works as expected."""
    # setup solr error mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # call search
    resp = client.post('/api/v2/search/businesses/bulk',
                       headers={'content-type': 'application/json'},
                       json={'names': ['name']})
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get('detail') == f'{mocked_error_msg}, {mocked_status_code}'
    assert resp_json.get('message') == 'Solr service error while processing request.'


@pytest.mark.parametrize('test_name,payload,errors', [
    ('test_no_payload', {}, [{'Invalid payload': "Expected at least 1 value in 'names' or 'identifiers'."}]),
    ('test_no_names_identifier', {'rows': 10}, [{'Invalid payload': "Expected at least 1 value in 'names' or 'identifiers'."}]),
    ('test_invalid_names', {'names': 'wrong'}, [{'Invalid payload': "Expected 'names' and 'identifiers' to be a list of strings."}]),
    ('test_invalid_identifiers', {'identifiers': 1}, [{'Invalid payload': "Expected 'names' and 'identifiers' to be a list of strings."}]),
    ('test_invalid_rows_1', {'identifiers': ['BC1234567'], 'rows': '10'}, [{'Invalid payload': "Expected 'rows' to be an integer."}]),
    ('test_invalid_rows_2', {'identifiers': ['BC1234567'], 'rows': 10001}, [{'Invalid payload': "Expected 'rows' to be <= 10000."}]),
])
def test_search_bulk_bad_request(app, session, client, test_name, payload, errors):
    """Assert that the business search call validates the payload."""
    # call search
    resp = client.post('/api/v2/search/businesses/bulk',
                       headers={'content-type': 'application/json'},
                       json=payload)
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get('message') == 'Errors processing request.'
    assert resp_json.get('details') == errors

