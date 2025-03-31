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
from datetime import UTC, datetime, timezone
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from flask import Blueprint, current_app, request
from flask_cors import cross_origin

from search_api.exceptions import BusinessException, DbRecordNotFoundException
from search_api.models import DocumentAccessRequest
from search_api.services import simple_queue
from search_api.services.gcp_auth.auth_service import ensure_authorized_queue_user

bp = Blueprint("GCP_LISTENER", __name__, url_prefix="")


@bp.post("")
@cross_origin(origins="*")
@ensure_authorized_queue_user
def gcp_listener():
    """Process the incoming cloud event.

    returns status
        200 - on success or invalid message (do not return invalid message in the queue)
    """
    ce = simple_queue.get_simple_cloud_event(request, wrapped=True)
    if ce is None or ce.data is None or "id" not in ce.data or "statusCode" not in ce.data:
        # current flow says if msg is invalid, it should be ACKed to get out of the queue
        current_app.logger.error("Invalid Event Message Received: %s ", json.dumps(dataclasses.asdict(ce)))
        return {}, HTTPStatus.OK

    try:
        # NOTE: this will be triggered for any payment (CC, PAD, etc.), but we only need to update for CC
        payment = ce.data
        if payment.get("corpTypeCode", "") != "BUS":
            raise BusinessException("invalid or missing corpTypeCode.", HTTPStatus.BAD_REQUEST)
        if not (payment_id := payment.get("id")):
            raise BusinessException("missing payment id.", HTTPStatus.BAD_REQUEST)
        if not (payment_status := payment.get("statusCode")):
            raise BusinessException("missing payment statusCode.", HTTPStatus.BAD_REQUEST)

        dars = DocumentAccessRequest.find_by_payment_token(str(payment_id))

        if dars is None:
            raise DbRecordNotFoundException()

        for dar in dars:
            if dar.status == DocumentAccessRequest.Status.COMPLETED:
                # This document is already in a completed state so skip
                current_app.logger.debug(
                    "Document Access Request already in a completed state for DAR id, Invoice id: %s, %s",
                    dar.id,
                    payment_id)
                continue

            if payment_status in ["COMPLETED", "APPROVED"]:
                # set dar status + payment_completion_date + expiry date
                dar.status = DocumentAccessRequest.Status.COMPLETED
                # NOTE: payment_completion_date is for when pay was marked completed in this api,
                #       which is not the same as the invoice completion date
                now = datetime.now(UTC)
                dar.payment_completion_date = now
                dar.expiry_date = now + relativedelta(
                    days=current_app.config["DOCUMENT_REQUEST_DAYS_DURATION"])

                # NOTE: below is only used for ops
                if dar.payment_status_code == "CREATED":
                    # NOTE: this causes an exception when dar.payment_status_code != 'CREATED'
                    dar.payment_status_code = payment_status
            else:
                current_app.logger.debug("Unexpected status given in pay event %s, %s", payment_id, payment_status)
                raise BusinessException("Unexpected pay status", HTTPStatus.NOT_IMPLEMENTED)
            dar.save()
        return {}, HTTPStatus.OK
    except Exception as err:
        # Catch Exception so that any error is still caught and the message is removed from the queue
        current_app.logger.error("Error processing pay event: %s", err.with_traceback(None))
        return {}, HTTPStatus.OK
