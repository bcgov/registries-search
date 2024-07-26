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
"""Test-Suite to ensure that the solr doc import enpoint works as expected."""
import time
from dataclasses import asdict
from http import HTTPStatus

import pytest
import requests_mock

from search_api.services import business_solr
from search_api.services.authz import SYSTEM_ROLE

from tests import integration_solr
from tests.unit.services.utils import create_header
from tests.unit.utils import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,docs', [
    ('single', [SOLR_TEST_DOCS[0]]),
    ('multiple', SOLR_TEST_DOCS),
])
def test_import_solr_mocked(app, session, client, jwt, test_name, docs):
    """Assert that update operation sends correct payload to solr."""
    solr_url = app.config.get('SOLR_SVC_BUS_LEADER_URL') + '/business/update?commit=true&overwrite=true&wt=json'
    docs_json = [asdict(x) for x in docs]
    with requests_mock.mock() as m:
        m.post(solr_url)
        api_response = client.put(f'/api/v1/internal/solr/import',
                                  json={'businesses': docs_json},
                                  headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                               'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.CREATED

        # check call to solr was correct
        assert m.called == True
        assert m.call_count == 1  # batch updated all docs
        assert solr_url in m.request_history[0].url
        
        expected = []
        for doc in docs_json:
            update_doc = {**doc}
            if parties := update_doc.get('parties'):
                update_doc['parties'] = {'set': parties}
            expected.append(update_doc)

        assert m.request_history[0].json() == expected


@integration_solr
def test_update_solr(session, client, jwt):
    """Assert that the import operation is successful."""
    # setup -- start with no docs
    business_solr.delete_all_docs()
    # import
    docs_json = [asdict(x) for x in SOLR_TEST_DOCS]
    api_response = client.put(f'/api/v1/internal/solr/import',
                              json={'businesses': docs_json},
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.CREATED

    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    for entity in SOLR_TEST_DOCS:
        search_response = business_solr.query(payload={'query': f'id:{entity.id}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1
    
    # do partial import
    identifier = SOLR_TEST_DOCS[3].identifier
    party_1_name = 'Test person si 1'
    party_2_name = 'Test person si 2'
    docs_json = [{
        'id': identifier,
        'parties': {
            'add': [
                {
                    'id': f'{identifier}_12457',
                    'partyName': party_1_name,
                    'partyRoles': ['significant individual'],
                    'partyType': 'person'
                },
                {
                    'id': f'{identifier}_124590',
                    'partyName': party_2_name,
                    'partyRoles': ['significant individual'],
                    'partyType': 'person'
                }
            ]
        }
    }]
    api_response = client.put(f'/api/v1/internal/solr/import',
                              json={'type': 'partial', 'businesses': docs_json},
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    time.sleep(2)  # wait for solr to register update
    search_response = business_solr.query(payload={'query': f'id:{identifier}', 'fields': '*, [child]'})
    assert search_response['response']
    assert search_response['response']['docs']
    assert len(search_response['response']['docs']) == 1
    assert len(search_response['response']['docs'][0]['parties']) == 2
    assert search_response['response']['docs'][0]['parties'][0]['partyName'] == party_1_name
    assert search_response['response']['docs'][0]['parties'][1]['partyName'] == party_2_name
        


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    docs_json = [asdict(x) for x in SOLR_TEST_DOCS]
    api_response = client.put(f'/api/v1/internal/solr/import',
                              json={'entities': docs_json},
                              headers=create_header(jwt, [], **{'Accept-Version': 'v1',
                                                                'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED
