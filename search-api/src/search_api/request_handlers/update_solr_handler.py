# Copyright © 2022 Province of British Columbia
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
from time import sleep
from typing import Dict

from flask import current_app

from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.models import SolrDoc, SolrDocEvent
from search_api.services import search_solr
from search_api.services.solr.solr_docs import BusinessDoc


def update_search_solr(identifier: str, event_type: SolrDocEventType) -> Dict[str, str]:
    """Update the doc for the identifier in the solr instance."""
    doc_update = SolrDoc.find_most_recent_by_identifier(identifier)
    if doc_update:
        doc_event = SolrDocEvent(event_type=event_type, solr_doc_id=doc_update.id).save()
        try:
            # pause for 1 second before update so that solr doesn't get overloaded on large batches of this call
            sleep(1)
            search_solr.create_or_replace_docs([BusinessDoc(**doc_update.doc)], force=True)
            doc_event.event_status = SolrDocEventStatus.COMPLETE
            doc_event.save()

        except Exception as err:  # noqa: B902
            # log / update event / pass err
            current_app.logger.debug('Failed to %s solr for %s', event_type, identifier)
            doc_event.event_status = SolrDocEventStatus.ERROR
            doc_event.save()
            raise err
