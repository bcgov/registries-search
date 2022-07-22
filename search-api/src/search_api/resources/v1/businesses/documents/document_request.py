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
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.models import DocumentAccessRequest
from search_api.request_handlers.document_access_request_handler import create_invoice, save_request
from search_api.services.validator import RequestValidator
from search_api.utils.auth import jwt
from search_api.services import get_role


bp = Blueprint('DOCUMENT_REQUESTS', __name__, url_prefix='/requests')  # pylint: disable=invalid-name


@bp.get('')
@bp.get('/<int:request_id>')
@cross_origin(origin='*')
@jwt.requires_auth
def get(business_identifier, request_id=None):
    """Return all active requests for a business by an account or a request with the specified request id."""
    try:
        account_id = request.headers.get('Account-Id', None)
        if not account_id:
            return resource_utils.account_required_response()

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


@bp.post('')
@cross_origin(origin='*')
@jwt.requires_auth
def post(business_identifier):
    """Create a new request for the business."""
    try:
        account_id = request.headers.get('Account-Id', None)
        if not account_id:
            return resource_utils.account_required_response()

        token = jwt.get_token_auth_header()
        request_json = request.get_json()
        role = get_role(jwt, account_id)

        errors = RequestValidator.validate_document_access_request(request_json, account_id, token, role)
        if errors:
            return resource_utils.bad_request_response(errors)

        document_access_request = save_request(account_id, business_identifier, request_json)

        pay_message, pay_code = create_invoice(document_access_request, jwt, request_json)
        reply = document_access_request.json
        if pay_code != HTTPStatus.CREATED:
            reply['errors'] = [pay_message]

        return jsonify(reply), pay_code

    except Exception as default_exception:   # noqa: B902
        return resource_utils.default_exception_response(default_exception)
