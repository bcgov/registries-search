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
"""BOR Solr update functions."""
# TODO: turn this into a class that isn't BOR specific
from flask import current_app

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc, SolrDocEvent
from bor_api.services import solr, solr_temp
from bor_api.services.bor_solr.doc_models import Entity


def update_bor_solr(entity_ids: list[str], doc_events: list[SolrDocEvent], temp: bool = False):
    """Update the docs for the entity_ids in the solr instance."""
    entities: list[Entity] = []
    for entity_id in entity_ids:
        doc_update = SolrDoc.find_most_recent_by_entity_id(entity_id)
        entities.append(Entity(**doc_update.doc))
    try:
        if temp:
            # TODO: remove this once solr_temp is merged into solr
            solr_temp.create_or_replace_docs(docs=entities, additive=False)
        else:
            solr.create_or_replace_docs(entities)
        SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:  # noqa: B902
        # log / update event / pass err
        current_app.logger.debug('Failed to UPDATE solr for %s', entity_ids)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err


def resync_bor_solr(entity_ids: list[str]):
    """Resync the docs for the entity_ids in the solr instance."""
    entities: list[Entity] = []
    doc_events: list[SolrDocEvent] = []
    for entity_id in entity_ids:
        doc_update = SolrDoc.find_most_recent_by_entity_id(entity_id)
        entities.append(Entity(**doc_update.doc))
        doc_event = SolrDocEvent(event_type=SolrDocEventType.RESYNC, solr_doc_id=doc_update.id).save()
        doc_events.append(doc_event)
    try:
        solr.create_or_replace_docs(entities)
        SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:  # noqa: B902
        # log / update event / pass err
        current_app.logger.debug('Failed to RESYNC solr for %s', entity_ids)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err
