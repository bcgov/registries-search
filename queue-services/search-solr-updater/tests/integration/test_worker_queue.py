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
from typing import List

import pytest
import requests_mock
from entity_queue_common.service_utils import subscribe_to_queue

from search_solr_updater.worker import cb_nr_subscription_handler
from .utils import get_random_number, helper_add_event_to_queue


@pytest.mark.asyncio
async def test_events_listener_queue(app, config, stan_server, event_loop, client_id, events_stan):
    """Assert that events can be retrieved and decoded from the Queue."""
    identifier = 'FM1234567'
    business_json = {
        'business': {
            'identifier': identifier,
            'legalName': 'test name',
            'legalType': 'GP',
            'state': 'ACTIVE',
            'taxId': '123456789BC0001'}}
    parties_json = {
        'parties': [{
            'officer': {
                'partyType': 'person',
                'firstName': 'name1',
                'lastName': 'name2'
            },
            'roles': [{'roleType': 'partner'}]
        }]}
    with requests_mock.mock() as m:
        m.post(config['KEYCLOAK_AUTH_TOKEN_URL'], json={'access_token': 'token'})
        m.get(f'{config["LEAR_SVC_URL"]}/businesses/FM1234567', json=business_json)
        m.get(f'{config["LEAR_SVC_URL"]}/businesses/FM1234567/parties', json=parties_json)
        m.put(f'{config["SEARCH_API_URL"]}/internal/solr/update')

        events_subject = 'test_subject'
        events_queue = 'test_queue'
        events_durable_name = 'test_durable'

        identifier = 'FM1234567'

        # register the handler to test it
        await subscribe_to_queue(events_stan,
                                events_subject,
                                events_queue,
                                events_durable_name,
                                cb_nr_subscription_handler)

        # add an event to queue
        await helper_add_event_to_queue(events_stan, events_subject, identifier)

        assert m.called == True
        assert m.call_count == 4
