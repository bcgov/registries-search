# Copyright © 2022 Province of British Columbia
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
"""Test Suite to ensure the worker routines are working as expected."""
import json
import os
import time
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from flask import Flask
from simple_cloudevent import SimpleCloudEvent, to_queue_message


BEN_BUSINESS = {
    'business': {
        'goodStanding': True,
        'identifier': 'BC1234567',
        'legalName': 'Benefit Company',
        'legalType': 'BEN',
        'state': 'ACTIVE',
        'taxId': '123456789BC0001'
    }
}
BEN_PARTIES = {
    'parties': [{
        'officer': {
            'partyType': 'person',
            'firstName': 'name1',
            'lastName': 'name2'
        },
        'roles': [{'roleType': 'director'}]
    }]
}
FIRM_PRIMARY_NAME = 'primary name'
FIRM_BUSINESS = {
    'business': {
        'alternateNames': [
            {
                'entityType': 'GP',
                'identifier': 'FM0483929',
                'name': 'NOT primary name',
                'type': 'DBA'
            },
            {
                'entityType': 'GP',
                'identifier': 'FM1234567',
                'name': FIRM_PRIMARY_NAME,
                'type': 'DBA'
            }
        ],
        'goodStanding': True,
        'identifier': 'FM1234567',
        'legalName': 'name1 name2',
        'legalType': 'GP',
        'state': 'ACTIVE',
        'taxId': '123456789BC0001'
    }
}
FIRM_PARTIES = {
    'parties': [
        {
            'officer': {
                'partyType': 'person',
                'firstName': 'name1',
                'lastName': 'name2'
            },
            'roles': [{'roleType': 'partner'}, {'roleType': 'director'}]
        },{
            'officer': {
                'partyType': 'person',
                'firstName': 'director',
                'lastName': 'invalid'
            },
            'roles': [{'roleType': 'director'}]
        }
    ]
}


@pytest.mark.parametrize('test_name, business, parties, is_firm', [
    ('test-ben-company', BEN_BUSINESS, BEN_PARTIES, False),
    ('test-firm', FIRM_BUSINESS, FIRM_PARTIES, True)
])
@patch("search_solr_updater.resources.worker.verify_gcp_jwt")
@patch("search_solr_updater.resources.worker.gcp_queue.get_simple_cloud_event")
def test_business_event(mock_get_event: MagicMock, mock_verify: MagicMock, app: Flask, client, test_name, business, parties, is_firm):
    """Assert that events can be retrieved and decoded from the Queue."""
    identifier = business['business']['identifier']
    kc_url = app.config['ACCOUNT_SVC_AUTH_URL']
    bus_url = f'{app.config["LEAR_SVC_URL"]}/businesses/{identifier}?slim=True'
    parties_url = f'{app.config["LEAR_SVC_URL"]}/businesses/{identifier}/parties?slim=True'
    search_url = f'{app.config["SEARCH_SVC_URL"]}/internal/solr/update'

    with requests_mock.mock() as m:
        m.post(kc_url, json={'access_token': 'token'})
        m.get(bus_url, json=business)
        m.get(parties_url, json=parties)
        m.put(search_url)

        msg = SimpleCloudEvent(id=1, type='bc.registry.business.test', data={'identifier': identifier})
        mock_verify.return_value = None
        mock_get_event.return_value = msg
        resp = client.post("/worker", data=to_queue_message(msg))

        assert resp.status_code == HTTPStatus.OK

        assert m.called == True
        assert m.call_count == 4
        assert m.request_history[0].url == kc_url + '/'
        assert m.request_history[1].url == bus_url
        assert m.request_history[2].url == parties_url
        assert m.request_history[3].url == search_url
        if not is_firm:
            assert m.last_request.json() == { **business, 'parties': [] }
        else:
            expected_business_json = { **business }
            expected_business_json['business']['legalName'] = FIRM_PRIMARY_NAME
            expected_parties = {
                'parties': [{
                    'officer': {
                        'partyType': 'person',
                        'firstName': 'name1',
                        'lastName': 'name2'
                    },
                    'roles': [{'roleType': 'partner'}]
                }]
            }
            assert m.last_request.json() == { **expected_business_json, **expected_parties }
