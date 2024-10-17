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
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus


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


@dataclass
class BaseExceptionE(Exception):
    """Base exception class for custom exceptions."""

    error: str
    message: str = None
    status_code: HTTPStatus = None


@dataclass
class SolrException(BaseExceptionE):
    """Solr search/update/delete exception."""

    def __post_init__(self):
        """Return a valid SolrException."""
        if self.status_code != HTTPStatus.SERVICE_UNAVAILABLE:
            self.error += f', {self.status_code}'
            self.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.message = 'Solr service error while processing request.'


class DbRecordNotFoundException(BaseExceptionE):
    """Row not found in database"""

    def __init__(self):
        self.message = "DB record not found"
        self.status_code = HTTPStatus.NOT_FOUND
        super().__init__()


class BusinessException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error: str, status_code: HTTPStatus, *args, **kwargs):
        """Return a valid BusinessException."""
        super(BusinessException, self).__init__(*args, **kwargs)  # pylint: disable=super-with-arguments
        self.error = error
        self.status_code = status_code


class ApiConnectionException(Exception):
    """Api Connection exception."""

    def __init__(self, code: int, detail: list[dict]):
        """Initialize the error object."""
        super(ApiConnectionException, self).__init__()  # pylint: disable=super-with-arguments
        self.code = code
        self.detail = str(detail)


class StorageException(Exception):
    """Exception for document storage service related errors."""
