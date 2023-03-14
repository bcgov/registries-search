# Copyright © 2022 Province of British Columbia
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
import functools
from enum import Enum
from http import HTTPStatus
from typing import Dict, List


class ResourceErrorCodes(str, Enum):
    """Render an Enum of error codes as message prefixes to facilitate identifying the source of the exception."""

    ACCOUNT_REQUIRED_ERR = '001'
    UNAUTHORIZED_ERR = '002'
    VALIDATION_ERR = '003'
    PAY_ERR = '004'
    DATABASE_ERR = '005'
    NOT_FOUND_ERR = '006'
    DUPLICATE_ERR = '007'
    PATH_PARAM_ERR = '008'
    DATA_MISMATCH_ERR = '009'
    DEFAULT_ERR = '010'
    SOLR_ERR = '011'
    AUTH_EXPIRED_ERR = '012'
    STORAGE_ERR = '013'


class BusinessException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error: str, status_code: HTTPStatus, *args, **kwargs):
        """Return a valid BusinessException."""
        super(BusinessException, self).__init__(*args, **kwargs)  # pylint: disable=super-with-arguments
        self.error = error
        self.status_code = status_code


class DatabaseException(Exception):
    """Database insert/update exception."""


class SolrException(Exception):
    """Solr search/update/delete exception."""

    def __init__(self, error: str, status_code: HTTPStatus, *args, **kwargs):
        """Return a valid SolrException."""
        super(SolrException, self).__init__(*args, **kwargs)  # pylint: disable=super-with-arguments
        self.error = error
        self.status_code = status_code


class ApiConnectionException(Exception):
    """Api Connection exception."""

    def __init__(self, code: int, detail: List[Dict]):
        """Initialize the error object."""
        super(ApiConnectionException, self).__init__()  # pylint: disable=super-with-arguments
        self.code = code
        self.detail = str(detail)


class StorageException(Exception):
    """Exception for document storage service related errors."""
