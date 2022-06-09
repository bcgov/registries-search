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
"""API endpoints for Document Access Requests."""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.models import DocumentAccessRequest
from search_api.utils.auth import jwt


bp = Blueprint('DOCUMENT_REQUESTS', __name__)  # pylint: disable=invalid-name


@bp.route('/<string:business_identifier>/documents/requests/<int:request_id>', methods=['GET', 'OPTIONS'])
@bp.route('/<string:business_identifier>/documents/requests', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get(business_identifier, request_id=None):
    """Return all active requests for a business by an account or a request with the specified request id."""
    try:
        account_id = request.headers.get('accountId', None)
        if not account_id:
            return resource_utils.unauthorized_error_response(account_id)

        if request_id:
            access_request = DocumentAccessRequest.find_by_id(request_id)
            if not access_request:
                return resource_utils.not_found_error_response('Document Access Request', request_id)
            if str(access_request.account_id) != account_id:
                return resource_utils.unauthorized_error_response(account_id)
            return jsonify(documentAccessRequest=access_request.json)

        access_requests_list = []
        access_requests = DocumentAccessRequest.find_active_requests(account_id, business_identifier)
        for access_request in access_requests:
            access_requests_list.append(access_request.json)

        return jsonify(documentAccessRequests=access_requests_list)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
