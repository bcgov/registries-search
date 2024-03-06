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
"""Test-Suite for the internal solr update API endpoints."""
from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc
from bor_api.services.bor_solr.doc_models import Entity


def check_update_recorded(entity_id: str, is_party=False, status=SolrDocEventStatus.PENDING, is_owner=False):
    """Assert the given identifier was recorded for an update."""
    solr_doc = SolrDoc.find_most_recent_by_entity_id(entity_id)
    assert solr_doc
    assert solr_doc.entity_id == entity_id
    assert Entity(**solr_doc.doc).id == entity_id
    identifier_set = Entity(**solr_doc.doc).identifier == entity_id
    assert identifier_set != is_party
    assert solr_doc._submitter_id is not None
    doc_events = solr_doc.solr_doc_events.all()
    if not is_owner:
        assert len(doc_events) == 2
        assert doc_events[0].event_status == status
        assert doc_events[0].event_type == SolrDocEventType.UPDATE
        assert doc_events[1].event_status == status
        assert doc_events[1].event_type == SolrDocEventType.UPDATE_EXT
    else:
        assert len(doc_events) == 1
        assert doc_events[0].event_status == status
        assert doc_events[0].event_type == SolrDocEventType.UPDATE_EXT
