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
"""Tests to assure the SolrDoc Class."""
import pytest

from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.models import SolrDocEvent


def test_solr_doc_event(session):
    """Assert that a solr doc event can be stored in the service."""
    event_update = SolrDocEvent(event_type=SolrDocEventType.UPDATE).save()
    event_resync = SolrDocEvent(event_type=SolrDocEventType.RESYNC).save()

    assert event_update.id is not None
    assert event_resync.id is not None
    # has default values
    assert event_update.event_date is not None
    assert event_resync.event_date is not None
    assert event_update.event_status == SolrDocEventStatus.PENDING
    assert event_resync.event_status == SolrDocEventStatus.PENDING
