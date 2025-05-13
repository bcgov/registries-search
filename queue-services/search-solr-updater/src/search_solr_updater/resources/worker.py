# Copyright © 2025 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the "License");
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    https://opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Exposes endpoints for the worker."""
from http import HTTPStatus

from flask import Blueprint, current_app, request
from simple_cloudevent import SimpleCloudEvent

from search_solr_updater.exceptions import ExternalServiceException
from search_solr_updater.services import gcp_queue, process_business_event
from search_solr_updater.services.auth import verify_gcp_jwt

bp = Blueprint("WORKER", __name__, url_prefix="/worker")


@bp.post("")
def worker():
    """Use endpoint to process Queue Msg objects."""
    try:
        if not request.data:
            return {}, HTTPStatus.OK
        if msg := verify_gcp_jwt():
            current_app.logger.info(msg)
            return {}, HTTPStatus.FORBIDDEN

        current_app.logger.info(f"Incoming raw msg: {request.data!s}")

        # Get cloud event
        if not (ce := gcp_queue.get_simple_cloud_event(request, wrapped=True)) or not isinstance(ce, SimpleCloudEvent):
            # Decision here is to return a 200, so the event is removed from the Queue
            current_app.logger.debug(f"ignoring message, raw payload: {ce!s}")
            return {}, HTTPStatus.OK

        current_app.logger.info(f"received ce: {ce!s}")

        process_business_event(ce)
        return {}, HTTPStatus.OK

    except ExternalServiceException as err:
        # This could be a temporary error so put back on the queue
        message_id = ce.id if ce else None
        current_app.logger.error("Queue Error - Generic exception: %s %s",
                                 f"Message with id: {message_id} has been put back on the queue for reprocessing.",
                                 str(err),
                                 exc_info=True)
        return {}, HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as err:
        # Unlikely to be temporary so log err for ops and remove from the queue
        message_id = ce.id if ce else None
        current_app.logger.error("Queue Error - Generic exception: %s %s",
                                 f"Message with id: {message_id} needs manual ops intervention.",
                                 str(err),
                                 exc_info=True)
        return {}, HTTPStatus.OK