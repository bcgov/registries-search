# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Application Specific Exceptions, to manage the business errors.

@log_error - a decorator to automatically log the exception to the logger provided

BusinessException - error, status_code - Business rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
from http import HTTPStatus
from typing import Dict, List

from .responses import bad_request_response, exception_response


class AuthorizationException(Exception):
    """Authorization exception."""

    def __init__(self, error: str):
        """Return a valid AuthorizationException."""
        super()
        self.message = 'Unauthorized access.'
        self.error = error
        self.status_code = HTTPStatus.UNAUTHORIZED


class BusinessException(Exception):
    """Business rules exception."""

    def __init__(self, message: str, error: str, status_code: HTTPStatus = None):
        """Return a valid BusinessException."""
        super().__init__()
        self.message = message
        self.error = error
        if status_code:
            self.status_code = status_code


class DatabaseException(Exception):
    """Database insert/update exception."""

    def __init__(self, error: str):
        """Return a valid DatabaseException."""
        super().__init__()
        self.message = 'Database error while processing request.'
        self.error = error
        self.status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class ExternalServiceException(Exception):
    """3rd party service exception."""

    def __init__(self, error: str, status_code: HTTPStatus = None):
        """Return a valid ExternalServiceException."""
        super().__init__()
        self.message = '3rd party service error while processing request.'
        self.error = f"{error} {status_code or ''}"
        self.status_code = HTTPStatus.SERVICE_UNAVAILABLE


class SolrException(Exception):
    """Solr search/update/delete exception."""

    def __init__(self, error: str, status_code: HTTPStatus, *args, **kwargs):
        """Return a valid SolrException."""
        super().__init__(*args, **kwargs)
        if status_code != HTTPStatus.SERVICE_UNAVAILABLE:
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.message = 'Solr service error while processing request.'
        self.error = error
        self.status_code = status_code
