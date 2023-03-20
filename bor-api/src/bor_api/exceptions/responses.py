# Copyright © 2023 Province of British Columbia
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
"""Exception responses."""
from http import HTTPStatus

from flask import jsonify, current_app


def bad_request_response(message: str):
    """Build generic bad request response."""
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def exception_response(exception: Exception):
    """Build exception error response."""
    current_app.logger.error(str(exception))
    message = exception.get('message', 'Error processing request.')
    detail = exception.get('error', '')
    status_code = exception.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR)
    return jsonify({'message': message, 'detail': detail}), status_code
