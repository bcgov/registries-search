# Copyright © 2024 Province of British Columbia
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
"""API endpoint for syncing entity records in solr."""
from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify
from flask_cors import cross_origin

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.exceptions import exception_response
from bor_api.models import SolrDoc, SolrDocEvent
from bor_api.services import solr
from bor_api.services.solr_update_helper import update_bor_solr

bp = Blueprint("SYNC", __name__, url_prefix="/sync")


def _validate_follower(now: datetime):
    """Return validation errors to do with the follower Solr instance."""
    errors = []
    if solr.follower_url != solr.leader_url:
        # verify the follower core details
        details: dict = (solr.replication("details", False)).json()["details"]
        # NOTE: replace tzinfo needed because strptime %Z is not working as documented
        #   - issue: accepts the tz in the string but doesn't add it to the dateime obj
        last_replication = (
            datetime.strptime(details["follower"]["indexReplicatedAt"], "%a %b %d %H:%M:%S %Z %Y")
        ).replace(tzinfo=UTC)
        current_app.logger.debug(f"Last replication was at {last_replication.isoformat()}")

        # verify polling is active
        if details["follower"]["isPollingDisabled"] == "true":
            errors.append("Follower polling disabled when it should be enabled.")

        # verify last_replication datetime is within a reasonable timeframe
        if last_replication + timedelta(hours=current_app.config.get("LAST_REPLICATION_THRESHOLD")) < now:
            # its been too long since a replication. Log / return error
            errors.append("Follower last replication datetime is longer than expected.")
    return errors


def _is_synced(actual_doc: dict, expected_doc: dict):
    """Return if True if the actual_doc and expected_doc are synced."""
    role: dict = (actual_doc.get("roles", [{}]))[0]
    address: dict = (actual_doc.get("entityAddresses", [{}]))[0]

    expected_role: dict = expected_doc["roles"][0] if expected_doc["roles"] else {}
    expected_address: dict = expected_doc["entityAddresses"][0] if expected_doc["entityAddresses"] else {}

    # verify important elements match the update
    name_eq = actual_doc.get("legalName") == expected_doc.get("legalName")
    related_id_eq = role.get("relatedIdentifier") == expected_role.get("relatedIdentifier")
    related_name_eq = role.get("relatedName") == expected_role.get("relatedName")
    related_state_eq = role.get("relatedState") == expected_role.get("relatedState")
    role_type_eq = role.get("roleType") == expected_role.get("roleType")
    street_eq = address.get("streetAddress") == expected_address.get("streetAddress")
    return name_eq and related_id_eq and related_name_eq and related_state_eq and role_type_eq and street_eq


@bp.get("")
@cross_origin(origins="*")
def sync_solr():
    """Sync docs in the DB that haven't been applied to SOLR yet."""
    try:
        pending_update_events = SolrDocEvent.get_events_by_status(
            statuses=[SolrDocEventStatus.PENDING],
            event_types=[SolrDocEventType.UPDATE, SolrDocEventType.RESYNC],
            limit=current_app.config.get("MAX_BATCH_UPDATE_NUM"),
        )
        err_update_events = SolrDocEvent.get_events_by_status(
            statuses=[SolrDocEventStatus.ERROR],
            event_types=[SolrDocEventType.UPDATE, SolrDocEventType.RESYNC],
            limit=current_app.config.get("MAX_BATCH_UPDATE_NUM"),
        )

        for event_list in [pending_update_events, err_update_events]:
            identifiers_to_sync = [(SolrDoc.get_by_id(event.solr_doc_id)).entity_id for event in event_list]
            current_app.logger.debug(f"Syncing: {identifiers_to_sync}")
            if identifiers_to_sync:
                update_bor_solr(identifiers_to_sync, event_list)

        return jsonify({"message": "Sync successful."}), HTTPStatus.OK

    except Exception as exception:
        return exception_response(exception)


@bp.get("/heartbeat")
@cross_origin(origins="*")
def sync_follower_heartbeat():
    """Verify the solr follower instance is serving updated/synced records."""
    try:
        now = datetime.now(UTC)

        if errors := _validate_follower(now):
            current_app.logger.error(errors)
            return jsonify({"errors": errors}), HTTPStatus.INTERNAL_SERVER_ERROR

        # verify an update that happened in the last hour (if there is one)
        events_to_verify = SolrDocEvent.get_events_by_status(
            statuses=[SolrDocEventStatus.COMPLETE],
            event_types=[SolrDocEventType.UPDATE],
            start_date=now - timedelta(minutes=60),
            limit=2,
        )

        if len(events_to_verify) == 0 or events_to_verify[0].event_date + timedelta(minutes=5) > now:
            # either no updates to check or the event may not be reflected in the search yet
            current_app.logger.debug("No update events to verify in the last hour.")
        else:
            # there was an update in the last hour and it is at least 5 minutes old
            doc_obj_to_verify = SolrDoc.get_by_id(events_to_verify[0].solr_doc_id)
            if doc_obj_to_verify.doc["entityType"] == "BUSINESS":
                # skip business event for this check
                if len(events_to_verify) < 2:  # noqa: PLR2004
                    # should never get here
                    message = "Business event without corresponding person update event."
                    current_app.logger.error(message)
                    return jsonify({"message": message}), HTTPStatus.INTERNAL_SERVER_ERROR
                doc_obj_to_verify = SolrDoc.get_by_id(events_to_verify[1].solr_doc_id)
                # if the second event pulled is also a business then skip (should happen very rarely)
                if doc_obj_to_verify.doc["entityType"] == "BUSINESS":
                    current_app.logger.debug("Did not pull a person update event. Skipping verification.")
                    return jsonify({"message": "Skipped."}), HTTPStatus.OK

            most_recent_doc_for_entity = SolrDoc.find_most_recent_by_entity_id(doc_obj_to_verify.entity_id)
            if most_recent_doc_for_entity.id != doc_obj_to_verify.id:
                # there's been an update since so skip verification of this event
                current_app.logger.debug("Update event has been altered since. Skipping verification.")
            else:
                current_app.logger.debug(f"Verifying sync for: {doc_obj_to_verify.entity_id}...")
                expected_doc: dict = doc_obj_to_verify.doc
                response = solr.query({"query": f"id:{expected_doc['id']}", "fields": "*, [child]"})
                actual_doc: dict = response["response"]["docs"][0] if response["response"]["docs"] else {}

                if not _is_synced(actual_doc, expected_doc):
                    # data returned from the follower does match the update or is not there
                    current_app.logger.debug(f"Entity expected: {expected_doc}")
                    current_app.logger.debug(f"Entity served: {actual_doc}")
                    message = f"Follower failed to update entity: {doc_obj_to_verify.entity_id}."
                    current_app.logger.error(message)
                    return jsonify({"message": message}), HTTPStatus.INTERNAL_SERVER_ERROR

                current_app.logger.debug(f"Sync verified for: {doc_obj_to_verify.entity_id}")

        return jsonify({"message": "Follower synchronization is healthy."}), HTTPStatus.OK

    except Exception as exception:
        return exception_response(exception)
