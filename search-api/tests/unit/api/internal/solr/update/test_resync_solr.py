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
"""Test-Suite to ensure that the solr business update endpoints/functions work as expected."""
import time
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
import requests_mock

from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.models import SolrDoc, SolrDocEvent
from search_api.services import business_solr
from search_api.services.authz import SYSTEM_ROLE, STAFF_ROLE, PUBLIC_USER
from search_api.services.business_solr.doc_models import BusinessDoc

from tests import integration_solr
from tests.unit.services.utils import create_header
from tests.unit.utils import SOLR_TEST_DOCS


def prep_resync(businesses: list[BusinessDoc]) -> list[tuple[BusinessDoc, SolrDoc, SolrDoc]]:
    """Setup resync state."""
    setup_info = []
    for orig_bus in businesses:
        # set one record to find and one record to miss (older / current version)
        business = deepcopy(orig_bus)
        business.name = f'{business.id} test_update_business_in_solr'
        solr_doc = SolrDoc(doc=asdict(business), identifier=business.id).save()
        SolrDocEvent(solr_doc_id=solr_doc.id, event_status=SolrDocEventStatus.COMPLETE, event_type=SolrDocEventType.UPDATE).save()
        entity_old = deepcopy(business)
        entity_old.name = f'{business.id} test_should_not_have_updated'
        solr_doc_old = SolrDoc(doc=asdict(entity_old), identifier=entity_old.id).save()
        solr_doc_old.submission_date = datetime.utcnow() - timedelta(minutes=10)
        solr_doc_old.save()
        SolrDocEvent(solr_doc_id=solr_doc_old.id, event_status=SolrDocEventStatus.COMPLETE, event_type=SolrDocEventType.UPDATE).save()
        setup_info.append((business, solr_doc, solr_doc_old))
        
    return setup_info
    

@pytest.mark.parametrize('test_name,payload,businesses', [
    ('resync_minutes_single', {'minutesOffset': 5}, [SOLR_TEST_DOCS[0]]),
    ('resync_minutes_multi', {'minutesOffset': 5}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1]]),
    ('resync_minutes_mix', {'minutesOffset': 5}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1], SOLR_TEST_DOCS[2]]),
    ('resync_minutes_nothing_to_do', {'minutesOffset': 5}, []),
    ('resync_identifiers_single', {'identifiers': []}, [SOLR_TEST_DOCS[0]]),
    ('resync_identifiers_multi', {'identifiers': []}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1]]),
    ('resync_identifiers_mix', {'identifiers': []}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1], SOLR_TEST_DOCS[2]]),
])
def test_resync_solr_mocked(app, session, client, jwt, test_name, payload: dict, businesses: list[BusinessDoc]):
    """Assert that resync operation sends correct payload to solr."""
    solr_url = app.config.get('SOLR_SVC_BUS_LEADER_URL') + '/business/update?commit=true&overwrite=true&wt=json'
    if 'identifiers' in payload:
        payload['identifiers'] = [x.id for x in businesses]

    setup_info = prep_resync(businesses)

    with requests_mock.mock() as m:
        m.post(solr_url)
        
        api_response = client.post(f'/api/v1/internal/solr/update/resync',
                                   json=payload,
                                   headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                                'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.CREATED
        
        if not businesses:
            # should not have resynced anything since nothing to update
            assert m.called == False
            assert m.call_count == 0
        else:
            # check call to solr mock
            assert m.called == True
            assert m.call_count == 1  # batch call for all entities
            
            for info in setup_info:
                business = info[0]
                solr_doc = info[1]
                solr_doc_old = info[2]
                doc_events = solr_doc.solr_doc_events.all()
                assert len(doc_events) == 2
                for event in doc_events:
                    assert event.event_status == SolrDocEventStatus.COMPLETE
                    assert event.event_type in [SolrDocEventType.RESYNC, SolrDocEventType.UPDATE]
                # did not update the older record
                assert len(solr_doc_old.solr_doc_events.all()) == 1

                assert solr_url in m.request_history[0].url

                business_in_payload = False
                for payload_business in m.request_history[0].json():
                    # this info was sent as a payload
                    business_after_set_conversion = asdict(business)
                    for key in ['parties']:
                        if key_value := business_after_set_conversion.get(key):
                            business_after_set_conversion[key] = {'set': key_value}

                    if payload_business == business_after_set_conversion:
                        business_in_payload = True
                        break
                assert business_in_payload


@integration_solr
@pytest.mark.parametrize('test_name,payload,businesses', [
    ('resync_minutes', {'minutesOffset': 5}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1], SOLR_TEST_DOCS[2]]),
    ('resync_identifiers', {'identifiers': []}, [SOLR_TEST_DOCS[0], SOLR_TEST_DOCS[1], SOLR_TEST_DOCS[2]]),
])
def test_resync_solr(session, client, jwt, test_name, payload: dict, businesses: list[BusinessDoc]):
    """Assert that the resync update operation is successful."""
    if 'identifiers' in payload:
        payload['identifiers'] = [x.id for x in businesses]

    # remove any existing solr docs
    business_solr.delete_all_docs()

    setup_info = prep_resync(businesses)
    api_response = client.post(f'/api/v1/internal/solr/update/resync',
                               json=payload,
                               headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.CREATED

    for business, solr_doc, solr_doc_old in setup_info:
        doc_events = solr_doc.solr_doc_events.all()
        assert len(doc_events) == 2
        for event in doc_events:
            assert event.event_status == SolrDocEventStatus.COMPLETE
            assert event.event_type in [SolrDocEventType.RESYNC, SolrDocEventType.UPDATE]
        # did not update the older record
        assert len(solr_doc_old.solr_doc_events.all()) == 1

        time.sleep(2)  # wait for solr to register update
        search_response = business_solr.query(payload={'query': f'id:{business.id}', 'fields': '*'})
        assert search_response['response']['numFound'] == 1
        assert search_response['response']['docs'][0]['name'] == business.name


@pytest.mark.parametrize('test_name,payload', [
    ('missing_required_field', {'bla': 2}),
    ('invalid_minute', {'minutesOffset': 'invalid'}),
])
def test_resync_solr_invalid_data(app, session, client, jwt, test_name, payload):
    """Assert that error is returned if data missing."""

    api_response = client.post(f'/api/v1/internal/solr/update/resync',
                               json=payload,
                               headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    for role in [STAFF_ROLE, PUBLIC_USER]:
        api_response = client.post(f'/api/v1/internal/solr/update/resync',
                                   data={'identifiers': ['BC1234567']},
                                   headers=create_header(jwt, [role], **{'Accept-Version': 'v1',
                                                                         'content-type': 'application/json'}))
        # check
        assert api_response.status_code == HTTPStatus.UNAUTHORIZED
