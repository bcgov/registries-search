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

from bor_api.enums import SolrSynonymType
from bor_api.models import SolrSynonymList
from bor_api.services import bor_solr
from bor_api.services.authz import SYSTEM_ROLE

from tests.unit.utils import create_header
from tests import integration_solr


def check_synonym_recorded(synonym: str, synonym_list: list[str], synonym_type: SolrSynonymType):
    """Assert the given synonym was recorded in the db."""
    synonym_list_record = SolrSynonymList.find_by_synonym(synonym, synonym_type)
    assert synonym_list_record.synonym == synonym
    assert set(synonym_list_record.synonym_list) == set(synonym_list)


@pytest.mark.parametrize('test_name,request_json', [
    ('reload_all_synonyms', {}),
    ('create/update_new_synonyms_address', {
        'ADDRESS': {'unmapped1 territory1': ['ut', 'unmapped territory']}}),
    ('create/update_new_synonyms_name', {
        'NAME': {
            'this should not exist yet': ['walaby', 'bla blah'],
            'another one that should not exist': ['we waa', 'heloworld', 'fun testing'],
            'singlewordnotinlist': ['sjkfv']}}),
    ('create/update_new_synonyms_all', {
        'ADDRESS': {'unmapped territory': ['ut', 'unmapped territory']},
        'NAME': {
            'this should not exist yet': ['walaby', 'bla blah'],
            'another one that should not exist': ['we waa', 'heloworld', 'fun testing'],
            'singlewordnotinlist': ['sjkfv']}})
])
def test_update_synonyms_mocked(app, session, client, jwt, test_name, request_json):
    """Assert the update operation sends correct payload to solr."""
    solr_syn_url_address = app.config.get('SOLR_SVC_URL') + '/bor/schema/analysis/synonyms/ADDRESS'
    solr_syn_url_name = app.config.get('SOLR_SVC_URL') + '/bor/schema/analysis/synonyms/NAME'
    solr_reload_url = app.config.get('SOLR_SVC_URL') + '/admin/cores?action=RELOAD&core=bor'

    with requests_mock.mock() as m:
        m.put(solr_syn_url_address)
        m.put(solr_syn_url_name)
        m.get(solr_reload_url)
        
        api_response = client.put(f'/api/v1/internal/solr/update/synonyms',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check synonym update in db
        for synonym_type in request_json:
            for synonym in request_json[synonym_type]:
                check_synonym_recorded(synonym, request_json[synonym_type][synonym], synonym_type)
        if not request_json:
            # check one of the address ones (should have populated db)
            check_synonym_recorded('british columbia', ['bc', 'british columbia'], SolrSynonymType.ADDRESS)
            # should also be in name list
            check_synonym_recorded('british columbia', ['bc', 'british columbia'], SolrSynonymType.NAME)
            # check one of the name specific ones
            check_synonym_recorded('chute', ['shoot', 'chute'], SolrSynonymType.NAME)

        # check call to solr mock
        assert m.called == True
        # check calls were made to update each synonym type and 1 was made to reload the core
        assert m.call_count == (len(request_json.keys()) or 2) + 1
        if SolrSynonymType.ADDRESS in request_json:
            assert solr_syn_url_address == m.request_history[0].url
            assert m.request_history[0].json() == request_json[SolrSynonymType.ADDRESS]
            if SolrSynonymType.NAME in request_json:
                assert solr_syn_url_name == m.request_history[1].url
                assert m.request_history[1].json() == request_json[SolrSynonymType.NAME]
        elif SolrSynonymType.NAME in request_json:
            assert solr_syn_url_name == m.request_history[0].url
            assert m.request_history[0].json() == request_json[SolrSynonymType.NAME]
        else:
            assert 'british columbia' in m.request_history[0].json()
            assert 'chute' in m.request_history[1].json()
        assert solr_reload_url == m.request_history[m.call_count - 1].url


@integration_solr
def test_update_synonyms(session, client, jwt):
    """Assert that update synonym operation is successful."""
    new_syn = 'test synonym'
    new_syn_list = ['ble bla', 'test synonym']
    
    def get_synonym_map(synonym_type: SolrSynonymType):
        """Verify synonym file and return synonym map."""
        syn_url = f'{bor_solr.synonyms_url}/{synonym_type.value}'
        starting_syns = bor_solr.call_solr('GET', syn_url)
        assert starting_syns.status_code == HTTPStatus.OK
        starting_syn_mappings = (starting_syns.json()).get('synonymMappings')
        assert starting_syn_mappings
        assert starting_syn_mappings['initArgs']['ignoreCase'] == True
        return starting_syn_mappings['managedMap']

    # verify starting synonyms (built from checked in file)
    start_syn_address_map = get_synonym_map(SolrSynonymType.ADDRESS)
    start_syn_name_map = get_synonym_map(SolrSynonymType.NAME)

    while (new_syn in start_syn_address_map) or (new_syn in start_syn_name_map):
        new_syn += str(randint(0, 999))
    # verify test integrity
    assert new_syn not in start_syn_address_map and new_syn not in start_syn_name_map
    synonym_update_json = {
        SolrSynonymType.ADDRESS: {new_syn: new_syn_list},
        SolrSynonymType.NAME: {new_syn: new_syn_list}}
    # check
    api_response = client.put(f'/api/v1/internal/solr/update/synonyms',
                              data=json.dumps(synonym_update_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    assert api_response.status_code == HTTPStatus.OK
    # check synonym update
    check_synonym_recorded(new_syn, new_syn_list, SolrSynonymType.ADDRESS)
    check_synonym_recorded(new_syn, new_syn_list, SolrSynonymType.NAME)
    starting_syn_maps = [start_syn_address_map, start_syn_name_map]
    updated_syn_maps = [get_synonym_map(SolrSynonymType.ADDRESS), get_synonym_map(SolrSynonymType.NAME)]
    for i, syn_map in enumerate(updated_syn_maps):
        assert len(syn_map.keys()) == len(starting_syn_maps[i]) + 1
        assert new_syn in syn_map
        assert syn_map[new_syn] == new_syn_list


def test_update_synonyms_unauthorized(client, jwt):
    """Assert that an unauthorized error is returned if unauthorized."""
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps({}),
                              headers=create_header(jwt, [], **{'Accept-Version': 'v1', 'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_synonyms_bad_request(client, jwt):
    """Assert that a bad request error is returned if payload is invalid."""
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps({'ADRES': {'bla': ['bla']}, 'NOM':{'bla': ['bla']}}),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1', 'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST
