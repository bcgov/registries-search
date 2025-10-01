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
"""Test-Suite to ensure that the solr backup endpoint works as expected."""
from http import HTTPStatus

import pytest
import requests_mock

from search_api.services.authz import SYSTEM_ROLE, STAFF_ROLE, PUBLIC_USER

from tests import integration_solr
from tests.unit.services.utils import create_header
    

@pytest.mark.parametrize('test_name,command', [
    ('test_backup', 'backup'),
    ('test_restore', 'restore'),
    ('test_restorestatus', 'restorestatus'),
    ('test_details', 'details')
])
def test_replicate_solr_mocked(app, client, jwt, test_name: str, command: str):
    """Assert that the backup endpoint sends the correct call to solr."""
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + f'/bor/replication?command={command}'

    with requests_mock.mock() as m:
        m.post(solr_url)
        
        api_response = client.post(f'/internal/solr/command',
                                   json={'command': command},
                                   headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.OK
        
        # check call to solr mock
        assert m.called == True
        assert m.call_count == 1


@integration_solr
@pytest.mark.parametrize('test_name,command', [
    ('test_backup', 'backup'),
    ('test_restore', 'restore'),
    ('test_restorestatus', 'restorestatus'),
    ('test_details', 'details')
])
def test_replicate_solr_mocked(app, client, jwt, test_name: str, command: str):
    """Assert that the backup endpoint is successful."""
    api_response = client.post(f'/internal/solr/command',
                                json={'command': command},
                                headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))

    # check success
    assert api_response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('test_name,payload', [
    ('missing_command', {'bla': 2}),
    ('invalid_command', {'command': 'invalid'}),
])
def test_backup_solr_invalid_data(app, session, client, jwt, test_name, payload):
    """Assert that error is returned if payload is invalid."""
    api_response = client.post(f'/internal/solr/command',
                               json=payload,
                               headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


def test_backup_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    for role in [STAFF_ROLE, PUBLIC_USER]:
        api_response = client.post(f'/internal/solr/command',
                                   data={'command': 'command'},
                                   headers=create_header(jwt, [role], **{'content-type': 'application/json'}))
        # check
        assert api_response.status_code == HTTPStatus.UNAUTHORIZED
