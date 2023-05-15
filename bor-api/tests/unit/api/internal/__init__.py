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
"""Test-Suite for the interal API endpoints."""
from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc
from bor_api.services.solr.solr_docs import Entity


def check_update_recorded(identifier: str, is_party: bool = False):
    """Assert the given identifier was recorded for an update."""
    solr_doc = SolrDoc.find_most_recent_by_identifier(identifier)
    assert solr_doc.identifier == identifier
    assert Entity(**solr_doc.doc).identifier == identifier
    identifier_q_set = Entity(**solr_doc.doc).identifier_q == identifier
    assert not identifier_q_set if is_party else identifier_q_set
    assert solr_doc._submitter_id is not None
    doc_events = solr_doc.solr_doc_events.all()
    assert len(doc_events) == 1
    assert doc_events[0].event_status == SolrDocEventStatus.COMPLETE
    assert doc_events[0].event_type == SolrDocEventType.UPDATE
