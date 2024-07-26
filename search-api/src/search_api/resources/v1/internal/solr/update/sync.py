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

import search_api.resources.utils as resource_utils
from search_api.enums import SolrDocEventStatus, SolrDocEventType
from search_api.exceptions import SolrException
from search_api.models import SolrDoc, SolrDocEvent
from search_api.request_handlers import update_business_solr
from search_api.services import business_solr
from search_api.services.business_solr.doc_fields import BusinessField


bp = Blueprint('SYNC', __name__, url_prefix='/sync')  # pylint: disable=invalid-name


@bp.get('')
@cross_origin(origin='*')
def sync_solr():
    """Sync docs in the DB that haven't been applied to SOLR yet."""
    try:
        pending_update_events = SolrDocEvent.get_events_by_status(statuses=[SolrDocEventStatus.PENDING,
                                                                            SolrDocEventStatus.ERROR],
                                                                  event_type=SolrDocEventType.UPDATE,
                                                                  limit=current_app.config.get('MAX_BATCH_UPDATE_NUM'))

        identifiers_to_sync = [(SolrDoc.get_by_id(event.solr_doc_id)).identifier for event in pending_update_events]
        current_app.logger.debug(f'Syncing: {identifiers_to_sync}')
        if identifiers_to_sync:
            update_business_solr(identifiers_to_sync, pending_update_events)
        return jsonify({'message': 'Sync successful.'}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as exception:  # noqa: B902
        return resource_utils.default_exception_response(exception)


@bp.get('/heartbeat')
@cross_origin(origin='*')
def sync_follower_heartbeat():  # pylint: disable=too-many-branches,too-many-statements
    """Verify the solr follower instance is serving updated/synced records."""
    try:
        now = datetime.now(UTC)
        if business_solr.follower_url != business_solr.leader_url:
            # verify the follower core details
            details: dict = (business_solr.replication('details', False)).json()['details']
            # NOTE: replace tzinfo needed because strptime %Z is not working as documented
            #   - issue: accepts the tz in the string but doesn't add it to the dateime obj
            last_replication = (datetime.strptime(details['follower']['indexReplicatedAt'],
                                                  '%a %b %d %H:%M:%S %Z %Y')).replace(tzinfo=UTC)
            current_app.logger.debug(f'Last replication was at {last_replication.isoformat()}')

            errors = []
            # verify polling is active
            if details['follower']['isPollingDisabled'] == 'true':
                errors.append('Follower polling disabled when it should be enabled.')

            # verify last_replication datetime is within a reasonable timeframe
            if last_replication + timedelta(hours=current_app.config.get('LAST_REPLICATION_THRESHOLD')) < now:
                # its been too long since a replication. Log / return error
                errors.append('Follower last replication datetime is longer than expected.')

            if errors:
                current_app.logger.error(errors)
                return jsonify({'errors': errors}), HTTPStatus.INTERNAL_SERVER_ERROR

        # verify an update that happened in the last hour (if there is one)
        events_to_verify = SolrDocEvent.get_events_by_status(statuses=[SolrDocEventStatus.COMPLETE],
                                                             event_type=SolrDocEventType.UPDATE,
                                                             start_date=now - timedelta(minutes=60),
                                                             limit=2)

        if len(events_to_verify) == 0 or events_to_verify[0].event_date + timedelta(minutes=5) > now:
            # either no updates to check or the event may not be reflected in the search yet
            current_app.logger.debug('No update events to verify in the last hour.')
        else:
            # there was an update in the last hour and it is at least 5 minutes old
            doc_obj_to_verify = SolrDoc.get_by_id(events_to_verify[0].solr_doc_id)

            most_recent_business_doc = SolrDoc.find_most_recent_by_identifier(doc_obj_to_verify.identifier)
            if most_recent_business_doc.id != doc_obj_to_verify.id:
                # there's been an update since so skip verification of this event
                current_app.logger.debug('Update event has been altered since. Skipping verification.')
            else:
                current_app.logger.debug(f'Verifying sync for: {doc_obj_to_verify.identifier}...')
                doc: dict = doc_obj_to_verify.doc
                response = business_solr.query({'query': f"id:{doc['id']}", 'fields': '*, [child]'})

                business: dict = response['response']['docs'][0] if response['response']['docs'] else {}

                # verify important elements match the update
                fields = [
                    BusinessField.NAME, BusinessField.IDENTIFIER, BusinessField.TYPE,
                    BusinessField.STATE, BusinessField.GOOD_STANDING, BusinessField.BN
                ]
                is_equal = True
                for field in fields:
                    if business.get(field.value) != doc.get(field.value):
                        current_app.logger.debug(f'{field} mismatch')
                        is_equal = False
                        break

                if not is_equal:
                    # data returned from the follower does match the update or is not there
                    current_app.logger.debug(f'Business expected: {doc}')
                    current_app.logger.debug(f'Business served: {business}')
                    message = f'Follower failed to update entity: {doc_obj_to_verify.identifier}.'
                    current_app.logger.error(message)
                    return jsonify({'message': message}), HTTPStatus.INTERNAL_SERVER_ERROR

                current_app.logger.debug(f'Sync verified for: {doc_obj_to_verify.identifier}')

        return jsonify({'message': 'Follower synchronization is healthy.'}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as exception:  # noqa: B902
        return resource_utils.default_exception_response(exception)
