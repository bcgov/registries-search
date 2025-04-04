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

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.models import DocumentAccessRequest, User
from search_api.services.authz import does_user_have_account
from search_api.utils.auth import jwt

bp = Blueprint("PURCHASE_REQUESTS", __name__, url_prefix="/purchases")


@bp.get("")
@bp.get("/<int:request_id>")
@cross_origin(origins="*")
@jwt.requires_auth
def get(request_id=None):  # noqa: PLR0911
    """Return all active requests for a business by an account or a request with the specified request id."""
    try:
        account_id = request.headers.get("Account-Id", None)
        if not account_id:
            return resource_utils.account_required_response()

        # updates user information with given jwt
        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)
        if not user:
            return resource_utils.default_exception_response("Error getting user information from JWT.")

        token = jwt.get_token_auth_header()
        user_is_part_of_org = does_user_have_account(token, account_id)

        if not user_is_part_of_org:
            return resource_utils.unauthorized_error_response(account_id)

        if request_id:
            access_request = DocumentAccessRequest.find_by_id(request_id)
            if not access_request:
                return resource_utils.not_found_error_response("Document Access Request", request_id)
            if str(access_request.account_id) != account_id:
                return resource_utils.unauthorized_error_response(account_id)
            return jsonify(documentAccessRequest=access_request.json)

        access_requests_list = []
        access_requests = DocumentAccessRequest.find_active_requests(account_id)
        for access_request in access_requests:
            access_requests_list.append(access_request.json)

        return jsonify(documentAccessRequests=access_requests_list)
    except Exception as default_exception:
        return resource_utils.default_exception_response(default_exception)
