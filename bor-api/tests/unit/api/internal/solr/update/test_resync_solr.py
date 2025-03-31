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
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest
import requests_mock

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc, SolrDocEvent
from bor_api.services import solr
from bor_api.services.authz import SYSTEM_ROLE, STAFF_ROLE, PUBLIC_USER
from bor_api.services.bor_solr.doc_models import Entity

from tests import integration_solr
from tests.unit.test_utils import create_header
from tests.unit.test_utils.solr_doc_data import TEST_BUSINESSES, TEST_PERSONS


def prep_resync(entities: list[Entity]) -> list[tuple[Entity, SolrDoc, SolrDoc]]:
    """Setup resync state."""
    setup_info = []
    for orig_entity in entities:
        # set one record to find and one record to miss (older / current version)
        entity = deepcopy(orig_entity)
        entity.legalName = f"{entity.id} test_update_business_in_solr"
        entity.name_q = entity.legalName
        solr_doc = SolrDoc(doc=asdict(entity), entity_id=entity.id).save()
        SolrDocEvent(
            solr_doc_id=solr_doc.id, event_status=SolrDocEventStatus.COMPLETE, event_type=SolrDocEventType.UPDATE
        ).save()
        entity_old = deepcopy(entity)
        entity_old.legalName = f"{entity.id} test_should_not_have_updated"
        entity_old.name_q = entity_old.legalName
        solr_doc_old = SolrDoc(doc=asdict(entity_old), entity_id=entity_old.id).save()
        solr_doc_old.submission_date = datetime.now(timezone.utc) - timedelta(minutes=10)
        solr_doc_old.save()
        SolrDocEvent(
            solr_doc_id=solr_doc_old.id, event_status=SolrDocEventStatus.COMPLETE, event_type=SolrDocEventType.UPDATE
        ).save()
        setup_info.append((entity, solr_doc, solr_doc_old))

    return setup_info


@pytest.mark.parametrize(
    "test_name,payload,entities",
    [
        ("resync_minutes_single", {"minutesOffset": 5}, [TEST_PERSONS[0]]),
        ("resync_minutes_multi", {"minutesOffset": 5}, [TEST_PERSONS[0], TEST_PERSONS[1]]),
        ("resync_minutes_mix", {"minutesOffset": 5}, [TEST_PERSONS[0], TEST_PERSONS[1], TEST_BUSINESSES[2]]),
        ("resync_minutes_nothing_to_do", {"minutesOffset": 5}, []),
        ("resync_identifiers_single", {"identifiers": []}, [TEST_PERSONS[0]]),
        ("resync_identifiers_multi", {"identifiers": []}, [TEST_PERSONS[0], TEST_PERSONS[1]]),
        ("resync_identifiers_mix", {"identifiers": []}, [TEST_PERSONS[0], TEST_PERSONS[1], TEST_BUSINESSES[0]]),
    ],
)
def test_resync_solr_mocked(app, session, client, jwt, test_name, payload: dict, entities: list[Entity]):
    """Assert that resync operation sends correct payload to solr."""
    solr_url = app.config.get("SOLR_SVC_LEADER_URL") + "/bor/update?commit=true&overwrite=true&wt=json"
    if "identifiers" in payload:
        payload["identifiers"] = [x.id for x in entities]

    setup_info = prep_resync(entities)

    with requests_mock.mock() as m:
        m.post(solr_url)

        api_response = client.post(
            f"/api/v1/internal/solr/update/resync",
            json=payload,
            headers=create_header(jwt, [SYSTEM_ROLE], **{"Accept-Version": "v1", "content-type": "application/json"}),
        )

        # check success
        assert api_response.status_code == HTTPStatus.CREATED

        if not entities:
            # should not have resynced anything since nothing to update
            assert m.called == False
            assert m.call_count == 0
        else:
            # check call to solr mock
            assert m.called == True
            assert m.call_count == 1  # batch call for all entities

            for info in setup_info:
                entity = info[0]
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

                entity_in_payload = False
                for payload_entity in m.request_history[0].json():
                    # this info was sent as a payload
                    entity_after_set_conversion = asdict(entity)
                    for key in ["entityAddresses", "nationalities", "roles", "taxResidencies"]:
                        if key_value := entity_after_set_conversion.get(key):
                            entity_after_set_conversion[key] = {"set": key_value}

                    if payload_entity == entity_after_set_conversion:
                        entity_in_payload = True
                        break
                assert entity_in_payload


@integration_solr
@pytest.mark.parametrize(
    "test_name,payload,entities",
    [
        ("resync_minutes", {"minutesOffset": 5}, [TEST_PERSONS[0], TEST_PERSONS[1], TEST_BUSINESSES[2]]),
        ("resync_identifiers", {"identifiers": []}, [TEST_PERSONS[0], TEST_PERSONS[1], TEST_BUSINESSES[0]]),
    ],
)
def test_resync_solr(session, client, jwt, test_name, payload: dict, entities: list[Entity]):
    """Assert that the resync update operation is successful."""
    if "identifiers" in payload:
        payload["identifiers"] = [x.id for x in entities]

    # remove any existing solr docs
    solr.delete_all_docs()

    setup_info = prep_resync(entities)
    api_response = client.post(
        f"/api/v1/internal/solr/update/resync",
        json=payload,
        headers=create_header(jwt, [SYSTEM_ROLE], **{"Accept-Version": "v1", "content-type": "application/json"}),
    )
    # check
    assert api_response.status_code == HTTPStatus.CREATED

    for entity, solr_doc, solr_doc_old in setup_info:
        doc_events = solr_doc.solr_doc_events.all()
        assert len(doc_events) == 2
        for event in doc_events:
            assert event.event_status == SolrDocEventStatus.COMPLETE
            assert event.event_type in [SolrDocEventType.RESYNC, SolrDocEventType.UPDATE]
        # did not update the older record
        assert len(solr_doc_old.solr_doc_events.all()) == 1

        time.sleep(2)  # wait for solr to register update
        search_response = solr.query(payload={"query": f"legalName_q:{entity.id}", "fields": "*"})
        assert search_response["response"]["numFound"] == 1
        assert search_response["response"]["docs"][0]["legalName"] == entity.legalName


@pytest.mark.parametrize(
    "test_name,payload",
    [
        ("missing_required_field", {"bla": 2}),
        ("invalid_minute", {"minutesOffset": "invalid"}),
    ],
)
def test_resync_solr_invalid_data(app, session, client, jwt, test_name, payload):
    """Assert that error is returned if data missing."""

    api_response = client.post(
        f"/api/v1/internal/solr/update/resync",
        json=payload,
        headers=create_header(jwt, [SYSTEM_ROLE], **{"Accept-Version": "v1", "content-type": "application/json"}),
    )
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    for role in [STAFF_ROLE, PUBLIC_USER]:
        api_response = client.post(
            f"/api/v1/internal/solr/update/resync",
            data={"identifiers": ["BC1234567"]},
            headers=create_header(jwt, [role], **{"Accept-Version": "v1", "content-type": "application/json"}),
        )
        # check
        assert api_response.status_code == HTTPStatus.UNAUTHORIZED
