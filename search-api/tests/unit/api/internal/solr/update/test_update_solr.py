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
"""Test-Suite to ensure that the solr doc update enpoint works as expected."""
import json
import time
from copy import deepcopy
from http import HTTPStatus

import pytest
import requests_mock

from search_api.enums import SolrDocEventStatus
from search_api.services import business_solr
from search_api.services.authz import SYSTEM_ROLE

from tests import integration_solr
from tests.unit.services.utils import create_header
from tests.unit.utils import (SOLR_UPDATE_REQUEST_TEMPLATE_CORP as CORP_TEMPLATE,
                              SOLR_UPDATE_REQUEST_TEMPLATE_FIRM as FIRM_TEMPLATE)

from . import check_update_recorded

@pytest.mark.parametrize('test_name,request_json', [
    ('corp', CORP_TEMPLATE),
    ('firm', FIRM_TEMPLATE)
])
def test_update_solr_mocked(app, session, client, jwt, test_name, request_json):
    """Assert that update operation sends correct payload to solr."""
    solr_url_update = app.config.get('SOLR_SVC_BUS_LEADER_URL') + '/business/update?commit=true&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url_update)
        
        api_response = client.put(f'/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.ACCEPTED
        # check business update
        business_identifier = request_json['business']['identifier']
        check_update_recorded(business_identifier)
            
        # check did not call to solr mock (only updates the DB)
        assert m.called == False
        # call sync to update solr
        api_response = client.get(f'/internal/solr/update/sync', headers={'content-type': 'application/json'})
        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check events were completed
        business_identifier = request_json['business']['identifier']
        check_update_recorded(business_identifier, status=SolrDocEventStatus.COMPLETE)
        # check call to solr was correct
        assert m.called == True
        assert m.call_count == 1

        # verify record update
        assert solr_url_update in m.request_history[0].url
        if test_name == 'corp':
            assert m.request_history[0].json() == [
                {
                    'id': 'BC1233987',
                    'identifier': 'BC1233987',
                    'legalType': 'BEN',
                    'name': 'Benefit test comp',
                    'status': 'ACTIVE',
                    'goodStanding': False,
                    'modernized': None,
                    'bn': '987654321BC0001',
                    'parties': None
                }
            ]
        else:
            assert m.request_history[0].json() == [
                {
                    'id': 'FM1233334',
                    'identifier': 'FM1233334',
                    'legalType': 'SP',
                    'name': 'Test ABC',
                    'status': 'ACTIVE',
                    'goodStanding': None,
                    'modernized': True,
                    'bn': '123456789',
                    'parties': {
                        'set': [
                            {
                                'id': 'FM1233334_1',
                                'parentBN': '123456789',
                                'partyName': 'TEST ABC',
                                'partyType': 'organization',
                                'parentName': 'Test ABC',
                                'partyRoles': ['proprietor'],
                                'parentStatus': 'ACTIVE',
                                'parentLegalType': 'SP',
                                'parentIdentifier': 'FM1233334'
                            }
                        ]
                    }
                }
            ]


@integration_solr
@pytest.mark.parametrize('test_name,request_json', [
    ('corp', CORP_TEMPLATE),
    ('firm', FIRM_TEMPLATE)
])
def test_update_solr(session, client, jwt, test_name, request_json):
    """Assert that update operation is successful."""
    # setup -- start with no docs
    business_solr.delete_all_docs()
    time.sleep(2)  # wait for solr to register update
    # update
    api_response = client.put(f'/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.ACCEPTED
    business_identifier = request_json['business']['identifier']
    party_ids = []
    si_ids = []
    # check business update
    check_update_recorded(business_identifier)
    # verify update has NOT synced to solr yet
    search_response = business_solr.query(payload={'query': f'id:{business_identifier}', 'fields': '*'})
    assert search_response['response']
    assert len(search_response['response']['docs']) == 0
    # call sync to update solr
    api_response = client.get(f'/internal/solr/update/sync', headers={'content-type': 'application/json'})
    # check success
    assert api_response.status_code == HTTPStatus.OK
    # check events were completed
    check_update_recorded(business_identifier, status=SolrDocEventStatus.COMPLETE)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    # verify search returns updated records
    search_response = business_solr.query(payload={'query': f'id:{business_identifier}', 'fields': '*'})
    assert search_response['response']
    assert len(search_response['response']['docs']) == 1


@pytest.mark.parametrize('test_name,legal_type,identifier,expected', [
    ('test_bc_add_prfx', 'BC', '0123456', 'BC0123456'),
    ('test_cc_add_prfx', 'CC', '1234567', 'BC1234567'),
    ('test_ulc_add_prfx', 'ULC', '2345678', 'BC2345678'),
    ('test_ben_add_prfx', 'BEN', '0000001', 'BC0000001'),
    ('test_bc_prfx_given', 'BC', 'BC0123466', 'BC0123466'),
    ('test_cc_prfx_given', 'CC', 'BC1234577', 'BC1234577'),
    ('test_ulc_prfx_given', 'ULC', 'BC234588', 'BC234588'),
    ('test_ben_add_prfx', 'BEN', 'BC0000002', 'BC0000002'),
    ('test_wrong_type_no_prfx', 'S', '0000003', '0000003'),
    ('test_wrong_type_prfx_given', 'S', 'S3456790', 'S3456790')
])
def test_update_bc_class_adds_prefix(app, session, client, jwt, test_name, legal_type, identifier, expected):
    """Assert prefixes are added to BC, ULC and CC identifiers and only when no prefix is given."""
    solr_url = app.config.get('SOLR_SVC_BUS_LEADER_URL') + '/bor/update?commit=true&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url)

        request_json = deepcopy(CORP_TEMPLATE)
        request_json['business']['legalType'] = legal_type
        request_json['business']['identifier'] = identifier

        api_response = client.put(f'/internal/solr/update',
                                data=json.dumps(request_json),
                                headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'}))
        # check
        assert api_response.status_code == HTTPStatus.ACCEPTED
        # check business update in model with altered identfier
        check_update_recorded(expected)


@integration_solr
@pytest.mark.parametrize('test_name, party_type, good_standing', [
    ('invalid_goodStanding', 'organization', 'non-boolean'),
    ('invalid_partyType', 'invalid type', 'true'),
])
def test_update_business_in_solr_invalid_data(session, client, jwt, test_name, party_type, good_standing):
    """Assert that error is returned."""
    request_json = deepcopy(FIRM_TEMPLATE)
    request_json['parties'][0]['officer']['partyType'] = party_type
    request_json['business']['goodStanding'] = good_standing
    api_response = client.put(f'/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'content-type': 'application/json'})
                              )
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    api_response = client.put(f'/internal/solr/update',
                              data=json.dumps(CORP_TEMPLATE),
                              headers=create_header(jwt, [], **{'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED
