# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API request handlers for solr updates / resyncs."""
from typing import Dict

from flask import current_app

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc, SolrDocEvent
from bor_api.services import bor_solr
from bor_api.services.solr.bor_solr_docs import Entity


def update_bor_solr(identifier: str, event_type: SolrDocEventType) -> Dict[str, str]:
    """Update the doc for the identifier in the solr instance."""
    doc_update = SolrDoc.find_most_recent_by_identifier(identifier)
    doc_event = SolrDocEvent(event_type=event_type, solr_doc_id=doc_update.id).save()
    try:
        bor_solr.create_or_replace_docs([Entity(**doc_update.doc)], force=True)
        doc_event.event_status = SolrDocEventStatus.COMPLETE
        doc_event.save()

    except Exception as err:  # noqa: B902
        # log / update event / pass err
        current_app.logger.debug('Failed to %s solr for %s', event_type, identifier)
        doc_event.event_status = SolrDocEventStatus.ERROR
        doc_event.save()
        raise err
