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
from flask import current_app

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc, SolrDocEvent, db
from bor_api.services import solr
from bor_api.services.bor_solr.doc_models import Entity, EntityRole
from bor_api.services.bor_solr.fields import EntityRoleField
from bor_api.services.bor_solr.utils.query_builders import build_base_query


def update_bor_solr(entity_ids: list[str], doc_events: list[SolrDocEvent]):
    """Update the docs for the entity_ids in the solr instance."""
    businesses: list[dict] = []
    people: list[Entity] = []
    for entity_id in entity_ids:
        doc_update = SolrDoc.find_most_recent_by_entity_id(entity_id)
        entity = Entity(**doc_update.doc)
        if entity.entityType == "PERSON":
            people.append(entity)
        else:
            # get all role records containing this business
            query_roles_with_business = build_base_query(
                query={"value": entity.identifier},
                fields={EntityRoleField.RELATED_IDENTIFIER_Q: "parent"},
                boost_fields={},
                fuzzy_fields={},
                synonym_fields={},
            )

            payload = {**query_roles_with_business, "fields": ["id", "_nest_parent_"]}
            roles_with_business = solr.query(payload, 0, 1000)
            for role in roles_with_business.get("response", {}).get("docs", []):
                # init via EntityRole to capture calculated values like related_q/address_q
                entity_role = EntityRole(
                    id=role["id"],
                    relatedAddresses=entity.entityAddresses,
                    relatedIdentifier=entity.identifier,
                    relatedLegalType=entity.legalType,
                    relatedBN=entity.bn,
                    relatedEmail=entity.email,
                    relatedName=entity.legalName,
                    relatedEntityType="BUSINESS",
                    relatedState=entity.state,
                    roleType="",
                    roleDates=None,
                )
                # these are applied via partial atomic updates requiring id and _root_
                businesses.append(
                    {
                        "_root_": role["_nest_parent_"],
                        "id": entity_role.id,
                        EntityRoleField.RELATED_ADDRESSES.value: {"set": entity_role.relatedAddresses},
                        EntityRoleField.RELATED_BN.value: {"set": entity_role.relatedBN},
                        EntityRoleField.RELATED_EMAIL.value: {"set": entity_role.relatedEmail},
                        EntityRoleField.RELATED_LEGAL_TYPE.value: {"set": entity_role.relatedLegalType},
                        EntityRoleField.RELATED_NAME.value: {"set": entity_role.relatedName},
                        EntityRoleField.RELATED_STATE.value: {"set": entity_role.relatedState},
                        EntityRoleField.RELATED_Q.value: {"set": entity_role.related_q},
                    }
                )
    try:
        if people:
            # update people
            solr.create_or_replace_docs(people, additive=False)

        if businesses:
            # update all previously existing related business records if any existed previously
            solr.create_or_replace_docs(raw_docs=businesses)

        SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:
        # log / update event / pass err
        current_app.logger.debug("Failed to UPDATE solr for %s", entity_ids)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err


def resync_bor_solr(entity_ids: list[str]):
    """Resync the docs for the entity_ids in the solr instance."""
    entities: list[Entity] = []
    doc_events: list[SolrDocEvent] = []
    for entity_id in entity_ids:
        doc_update = SolrDoc.find_most_recent_by_entity_id(entity_id)
        # make sure it has a regular update event - TODO: rework this once solr_temp is merged into solr
        update_events = db.session.query(SolrDocEvent).filter(SolrDocEvent.solr_doc_id == doc_update.id).all()
        if len([x for x in update_events if x.event_type == SolrDocEventType.UPDATE]) == 0:
            # no regular update so skip
            continue
        entities.append(Entity(**doc_update.doc))
        doc_event = SolrDocEvent(event_type=SolrDocEventType.RESYNC, solr_doc_id=doc_update.id).save()
        doc_events.append(doc_event)
    try:
        if len(entities) > 0:
            solr.create_or_replace_docs(entities, additive=False)
            SolrDocEvent.update_events_status(SolrDocEventStatus.COMPLETE, doc_events)

    except Exception as err:
        # log / update event / pass err
        current_app.logger.debug("Failed to RESYNC solr for %s", entity_ids)
        SolrDocEvent.update_events_status(SolrDocEventStatus.ERROR, doc_events)
        raise err
