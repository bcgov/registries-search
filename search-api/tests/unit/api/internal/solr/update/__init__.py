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
from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.models import SolrDoc
from search_api.services.business_solr.doc_models import BusinessDoc


def check_update_recorded(identifier: str, status=SolrDocEventStatus.PENDING):
    """Assert the given identifier was recorded for an update."""
    solr_doc = SolrDoc.find_most_recent_by_identifier(identifier)
    assert solr_doc
    assert solr_doc.identifier == identifier
    assert BusinessDoc(**solr_doc.doc).id == identifier
    assert solr_doc._submitter_id is not None
    doc_events = solr_doc.solr_doc_events.all()
    assert len(doc_events) == 1
    assert doc_events[0].event_status == status
    assert doc_events[0].event_type == SolrDocEventType.UPDATE
