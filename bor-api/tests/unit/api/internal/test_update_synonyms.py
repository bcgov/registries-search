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
"""Test-Suite to ensure that the solr synonym update enpoint works as expected."""
import json
from copy import deepcopy
from http import HTTPStatus
from random import randint

import pytest
import requests_mock

from bor_api.models import SolrSynonymList
from bor_api.services import bor_solr
from bor_api.services.authz import SYSTEM_ROLE

from tests.unit.utils import create_header
from tests import integration_solr


def check_synonym_recorded(synonym: str, synonym_list: list[str]):
    """Assert the given synonym was recorded in the db."""
    synonym_list_record = SolrSynonymList.find_by_synonym(synonym)
    assert synonym_list_record.synonym == synonym
    assert synonym_list_record.synonym_list == synonym_list


@pytest.mark.parametrize('test_name,request_json', [
    ('reload_all_synonyms', {}),
    ('create/update_new_synonyms', {
        'this should not exist yet': ['walaby', 'bla blah'],
        'another one that should not exist': ['we waa', 'heloworld', 'fun testing'],
        'singlewordnotinlist': ['sjkfv']
      }
    )
])
def test_update_synonyms_mocked(app, session, client, jwt, test_name, request_json):
    """Assert the update operation sends correct payload to solr."""
    solr_syn_url = app.config.get('SOLR_SVC_URL') + '/bor/schema/analysis/synonyms/english'
    solr_reload_url = app.config.get('SOLR_SVC_URL') + '/admin/cores?action=RELOAD&core=bor'

    with requests_mock.mock() as m:
        m.put(solr_syn_url)
        m.get(solr_reload_url)
        
        api_response = client.put(f'/api/v1/internal/solr/update/synonyms',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check synonym update in db
        for key in request_json:
            check_synonym_recorded(key, request_json[key])
        if not request_json:
            # check one of the address ones (should have populated db)
            check_synonym_recorded('british columbia', ['bc', 'british columbia'])

        # check call to solr mock
        assert m.called == True
        assert m.call_count == 2
        assert solr_syn_url in m.request_history[0].url
        if request_json:
            assert m.request_history[0].json() == request_json
        else:
            assert 'british columbia' in m.request_history[0].json()
        assert solr_reload_url in m.request_history[1].url


@integration_solr
def test_update_synonyms(session, client, jwt):
    """Assert that update synonym operation is successful."""
    new_syn = 'test synonym'
    new_syn_list = ['ble bla', 'test synonym']
    # verify starting synonyms (built from checked in file)
    syn_url = bor_solr.synonyms_url + '/english'
    starting_syns = bor_solr.call_solr('GET', syn_url)
    assert starting_syns.status_code == HTTPStatus.OK
    starting_syn_mappings = (starting_syns.json()).get('synonymMappings')
    assert starting_syn_mappings
    assert starting_syn_mappings['initArgs']['ignoreCase'] == True
    assert starting_syn_mappings['managedMap']['british columbia'] == ['bc', 'british columbia']

    while new_syn in starting_syn_mappings['managedMap']:
        new_syn += str(randint(0, 999))
    # verify test integrity
    assert new_syn not in starting_syn_mappings['managedMap']
    # check
    api_response = client.put(f'/api/v1/internal/solr/update/synonyms',
                              data=json.dumps({new_syn: new_syn_list}),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    assert api_response.status_code == HTTPStatus.OK
    # check synonym update
    check_synonym_recorded(new_syn, new_syn_list)
    updated_syns = bor_solr.call_solr('GET', syn_url)
    assert updated_syns.status_code == HTTPStatus.OK
    updated_syn_mappings = (updated_syns.json()).get('synonymMappings')
    assert len(updated_syn_mappings['managedMap'].keys()) == len(starting_syn_mappings['managedMap'].keys()) + 1
    assert new_syn in updated_syn_mappings['managedMap']
    assert updated_syn_mappings['managedMap'][new_syn] == new_syn_list


def test_update_synonyms_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps({}),
                              headers=create_header(jwt, [], **{'Accept-Version': 'v1', 'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED
