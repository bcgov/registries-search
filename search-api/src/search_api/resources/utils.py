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
"""Resource helper utilities for processing requests."""
from http import HTTPStatus

from flask import current_app, jsonify

from search_api.exceptions import BaseExceptionE, ResourceErrorCodes

# Resource error messages
# Model business error messages in models.utils.py
ACCOUNT_REQUIRED = "{code}: Account-Id header required."
UNAUTHORIZED = "{code}: authorization failure submitting a request for {account_id}."
ACCOUNT_ACCESS = "{code}: the account ID {account_id} cannot access statement information for " + \
                 "registration number {registration_num}."
STAFF_SEARCH_BCOL_FAS = "{code}: provide either a BCOL Account Number or a Routing Slip Number but not both."
SBC_SEARCH_NO_PAYMENT = "{code}: provide either a BCOL Account Number or a Routing Slip Number."
DATABASE = "{code}: {context} database error for {account_id}."
NOT_FOUND = "{code}: no {item} found for {key}."
PATH_PARAM = "{code}: a {param_name} path parameter is required."
PATH_MISMATCH = "{code}: the path value ({path_value}) does not match the data {description} value ({data_value})."
DEFAULT = "{code}: error processing request."
PAYMENT = "{code}:{status} payment error for account {account_id}."
SOLR = "{code}: {status} solr error while processing request."
STORAGE = "{code}: GCP storage error while processing request."

CERTIFIED_PARAM = "certified"
ROUTING_SLIP_PARAM = "routingSlipNumber"
DAT_NUMBER_PARAM = "datNumber"
BCOL_NUMBER_PARAM = "bcolAccountNumber"

REG_STAFF_DESC = "BC Registries Staff"
SBC_STAFF_DESC = "SBC Staff"
BCOL_STAFF_DESC = "BC Online Help"


def serialize(errors):
    """Serialize errors."""
    error_message = []
    if errors:
        for error in errors:
            error_message.append("Schema validation: " + error.message + ".")
    return error_message


def get_account_id(req):
    """Get account ID from request headers."""
    return req.headers.get("Account-Id")


def is_pdf(req):
    """Check if request headers Accept is application/pdf."""
    accept = req.headers.get("Accept")
    return accept and accept.upper() == "APPLICATION/PDF"


def get_apikey(req):
    """Get gateway api key from request headers."""
    return req.headers.get("x-apikey")


def account_required_response():
    """Build account required error response."""
    message = ACCOUNT_REQUIRED.format(code=ResourceErrorCodes.ACCOUNT_REQUIRED_ERR)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def bad_request_response(message: str, errors: list[dict[str, str]] | None = None):
    """Build generic bad request response."""
    return jsonify({"message": message, "details": errors or []}), HTTPStatus.BAD_REQUEST


def exception_response(exception: BaseExceptionE):
    """Build exception error response."""
    current_app.logger.error(repr(exception))
    try:
        message = exception.message or "Error processing request."
        detail = exception.error or repr(exception)
        status_code = exception.status_code or HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception:
        # uncaught exception
        message = "Error processing request."
        detail = repr(exception)
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return jsonify({"message": message, "detail": detail}), status_code


def sbc_payment_required(message: str, detail: str, error_type: str):
    """Build sbc payment required error response."""
    return jsonify({"message": message, "detail": detail, "type": error_type}), HTTPStatus.PAYMENT_REQUIRED


def default_exception_response(exception):
    """Build default 500 exception error response."""
    current_app.logger.error(exception.with_traceback(None))
    message = DEFAULT.format(code=ResourceErrorCodes.DEFAULT_ERR)
    return jsonify({"message": message, "detail": exception.with_traceback(None)}), HTTPStatus.INTERNAL_SERVER_ERROR


def not_found_error_response(item, key):
    """Build a not found error response."""
    message = NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR, item=item, key=key)
    current_app.logger.info(str(HTTPStatus.NOT_FOUND.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.NOT_FOUND


def unauthorized_error_response(account_id):
    """Build an unauthorized error response."""
    message = UNAUTHORIZED.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR, account_id=account_id)
    current_app.logger.info(str(HTTPStatus.UNAUTHORIZED.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.UNAUTHORIZED


def authorization_expired_error_response(account_id):
    """Build an unauthorized error response."""
    message = UNAUTHORIZED.format(code=ResourceErrorCodes.AUTH_EXPIRED_ERR, account_id=account_id)
    current_app.logger.info(str(HTTPStatus.UNAUTHORIZED.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.UNAUTHORIZED


def gcp_storage_service_error(detail):
    """Build a storage servcie error response."""
    message = STORAGE.format(code=ResourceErrorCodes.STORAGE_ERR)
    current_app.logger.info(str(HTTPStatus.INTERNAL_SERVER_ERROR.value) + ": " + detail)
    return jsonify({"message": message, "detail": detail}), HTTPStatus.INTERNAL_SERVER_ERROR
