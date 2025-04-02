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
"""API endpoint for resyncing entity records in solr."""
from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin

from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import SolrDoc
from bor_api.services import SYSTEM_ROLE, jwt
from bor_api.services.solr_update_helper import resync_bor_solr

bp = Blueprint("RESYNC", __name__, url_prefix="/resync")


@bp.post("")
@cross_origin(origins="*")
@jwt.requires_roles([SYSTEM_ROLE])
def resync_solr():
    """Resync solr docs from the given date or identifiers given."""
    try:
        request_json = request.json
        from_datetime = datetime.now(UTC)
        minutes_offset = request_json.get("minutesOffset", None)
        identifiers_to_resync = request_json.get("identifiers", None)
        if not minutes_offset and not identifiers_to_resync:
            return bad_request_response('Missing required field "minutesOffset" or "identifiers".')
        try:
            minutes_offset = float(minutes_offset)
        except:
            if not identifiers_to_resync:
                return bad_request_response('Invalid value for field "minutesOffset". Expecting a number.')

        if minutes_offset:
            # get all updates since the from_datetime
            resync_date = from_datetime - timedelta(minutes=minutes_offset)
            identifiers_to_resync = SolrDoc.get_updated_entity_ids_after_date(resync_date)

        if identifiers_to_resync:
            current_app.logger.debug(f"Resyncing: {identifiers_to_resync}")
            resync_bor_solr(identifiers_to_resync)
        else:
            current_app.logger.debug("No records to resync.")

        return jsonify({"message": "Resync successful."}), HTTPStatus.CREATED

    except Exception as exception:
        return exception_response(exception)
