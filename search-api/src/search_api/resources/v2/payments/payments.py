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
"""API endpoints for Search Credit Card (CC) payments."""
import dataclasses
import json
from http import HTTPStatus

from flask import Blueprint, current_app, request
from flask_cors import cross_origin

from search_api.services import simple_queue
from search_api.services.document_services.document_access_request import update_document_access_request_status_by_id
from search_api.services.gcp_auth.auth_service import ensure_authorized_queue_user

bp = Blueprint('GCP_LISTENER', __name__)  # pylint: disable=invalid-name



@bp.route("/", methods=("POST",))
@cross_origin(origin='*')
@ensure_authorized_queue_user
def gcp_listener():
    """Process the incoming cloud event.

    returns status
        200 - on success or invalid message (do not return invalid message in the queue)
        500 - if any issues returns 500 Internal Server Error so msg can return to the queue
    """
    ce = simple_queue.get_simple_cloud_event(request, wrapped=True)

    if not ce or not ce.data or not ce.data.id or not ce.data.status:
        current_app.logger.error('Invalid Event Message Received: %s ', json.dumps(dataclasses.asdict(ce)))
        return {}, HTTPStatus.BAD_REQUEST

    try:
        credit_card_payment = ce.data
        update_document_access_request_status_by_id(credit_card_payment.id, credit_card_payment.status)

        return {}, HTTPStatus.OK
    except Exception:  # NOQA # pylint:Q disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        current_app.logger.error('Error processing event: ', exc_info=True)
        return {}, HTTPStatus.INTERNAL_SERVER_ERROR
