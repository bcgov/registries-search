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
from flask import current_app

from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.models import SolrDoc, SolrDocEvent
from search_api.services import business_solr
from search_api.services.business_solr.doc_models import BusinessDoc


def update_business_solr(identifiers: list[str], doc_events: list[SolrDocEvent]):
    """Update the docs for the entity_ids in the solr instance."""
    businesses: list[BusinessDoc] = []
    for identifier in identifiers:
        doc_update = SolrDoc.find_most_recent_by_identifier(identifier)
        businesses.append(BusinessDoc(**doc_update.doc))
    try:
        # update people
        business_solr.create_or_replace_docs(businesses, additive=False)
        SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:  # noqa: B902
        # log / update event / pass err
        current_app.logger.debug('Failed to UPDATE solr for %s', identifiers)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err


def resync_business_solr(identifiers: list[str]):
    """Re-apply the docs for the given identifiers."""
    businesses: list[BusinessDoc] = []
    doc_events: list[SolrDocEvent] = []
    for identifier in identifiers:
        doc_update = SolrDoc.find_most_recent_by_identifier(identifier)
        businesses.append(BusinessDoc(**doc_update.doc))
        # add separate event for resync
        doc_event = SolrDocEvent(event_type=SolrDocEventType.RESYNC, solr_doc_id=doc_update.id).save()
        doc_events.append(doc_event)
    try:
        if len(businesses) > 0:
            business_solr.create_or_replace_docs(businesses, additive=False)
            SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:  # noqa: B902
        # log / update event / pass err
        current_app.logger.debug('Failed to RESYNC solr for %s', identifiers)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err
