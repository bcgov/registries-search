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

from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin
from simple_cloudevent import to_queue_message

import search_api.resources.utils as resource_utils
from search_api.exceptions import ApiConnectionException
from search_api.models import DocumentAccessRequest, User
from search_api.request_handlers.document_access_request_handler import create_invoice, save_request
from search_api.services import get_role
from search_api.services import queue
from search_api.services.document_services import create_doc_request_ce
from search_api.services.entity import get_business
from search_api.services.flags import Flags
from search_api.services.validator import RequestValidator
from search_api.utils.auth import jwt


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
def post(business_identifier):  # pylint: disable=too-many-return-statements
    """Create a new request for the business."""
    try:
        account_id = request.headers.get('Account-Id', None)
        if not account_id:
            return resource_utils.account_required_response()
        business_response = get_business(business_identifier)
        if business_response.status_code not in [HTTPStatus.OK]:
            return resource_utils.bad_request_response('Business not found.')

        business_json = business_response.json().get('business')

        token = jwt.get_token_auth_header()
        request_json = request.get_json()
        role = get_role(jwt, account_id)
        token_dict = g.jwt_oidc_token_info

        errors = RequestValidator.validate_document_access_request(request_json, account_id, token, role)
        if errors:
            return resource_utils.bad_request_response(errors)

        document_access_request = save_request(account_id, business_identifier, request_json)

        pay_response, pay_code = create_invoice(document_access_request, jwt, request_json, business_json)
        if pay_code != HTTPStatus.CREATED:
            # format the error same as others (UI needs to parse this after gateway wraps the error response)
            error_type = pay_response.get('error', {}).get('type')
            detail = pay_response.get('error', {}).get('detail') or pay_response.get('error')
            message = 'Invoice creation failed.'
            return resource_utils.sbc_payment_required(message, detail, error_type)

        try:
            # pylint: disable=E0601,W0311; # noqa: E117,E129,E501; doesn't understand the walrus koo koo kachoo
            if pay_code == HTTPStatus.CREATED and \
                (ff_queue_doc_request_name := current_app.config.get('FF_QUEUE_DOC_REQUEST_NAME')) and \
                (user := User.find_by_jwt_token(token_dict)) and \
                (ff_queue_doc_request_flag := Flags.value(ff_queue_doc_request_name,
                                                          Flags.flag_user(user, account_id, jwt))) and \
                isinstance(ff_queue_doc_request_flag, bool) and \
                ff_queue_doc_request_flag:  # noqa: E129

                    # Create a CloudEvent and publish to the correct subject; # noqa: E117
                    # noqa: E117
                    project_id = current_app.config.get('QUEUE_PROJECT_ID')  # noqa: E117
                    topic = current_app.config.get('QUEUE_TOPIC')   # noqa: E117
                    ce = create_doc_request_ce(document_access_request)   # pylint: disable=invalid-name; noqa: E117

                    queue.publish(
                        subject=queue.create_subject(project_id, topic),
                        msg=to_queue_message(ce)
                    )
        except Exception as err:  # noqa: B902
            # will need to decide on how to best notify there is an error
            msg = f'Identifier: {business_identifier} Unable to put document request on Queue'
            current_app.logger.error(msg, err.with_traceback(None))

        return jsonify(document_access_request.json), pay_code

    except ApiConnectionException as err:
        current_app.logger.error(err)
        return jsonify({'message': 'Error creating new business request.', 'detail': err.detail}), err.code

    except Exception as default_exception:   # noqa: B902
        current_app.logger.error(default_exception.with_traceback(None))
        return resource_utils.default_exception_response(default_exception)
