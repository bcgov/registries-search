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

from search_api.exceptions import DbRecordNotFoundException
from search_api.models import DocumentAccessRequest
from search_api.services import simple_queue
from search_api.services.gcp_auth.auth_service import ensure_authorized_queue_user


bp = Blueprint('GCP_LISTENER', __name__, url_prefix='')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
@ensure_authorized_queue_user
def gcp_listener():
    """Process the incoming cloud event.

    returns status
        200 - on success or invalid message (do not return invalid message in the queue)
    """
    ce = simple_queue.get_simple_cloud_event(request, wrapped=True)
    if ce is None or ce.data is None or 'id' not in ce.data or 'statusCode' not in ce.data:
        # current flow says if msg is invalid, it should be ACKed to get out of the queue
        current_app.logger.error('Invalid Event Message Received: %s ', json.dumps(dataclasses.asdict(ce)))
        return {}, HTTPStatus.OK

    try:
        credit_card_payment = ce.data
        if credit_card_payment.get('corpTypeCode', '') != 'BUS':
            raise Exception('invalid or missing corpTypeCode.')  # noqa: E713 # pylint: disable=broad-exception-raised
        payment_id = credit_card_payment['id']

        dars = DocumentAccessRequest.find_by_payment_token(str(payment_id))

        if dars is None:
            raise DbRecordNotFoundException()

        for dar in dars:
            dar.status = credit_card_payment['statusCode']
            dar.save()

        return {}, HTTPStatus.OK
    except Exception:  # noqa pylint: disable=broad-except
        # Catch Exception so that any error is still caught and the message is removed from the queue
        current_app.logger.error('Error processing event: ', exc_info=True)
        return {}, HTTPStatus.OK
