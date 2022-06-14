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
"""Manages LEAR api interactions."""
from http import HTTPStatus

import requests
from requests import exceptions
from flask import current_app

from search_api.exceptions import ApiConnectionException
from search_api.models import Document
from search_api.services.authz import get_bearer_token


# DocumentType mapper to document name used in LEAR for business documents
DOCUMENT_NAME = {
    Document.DocumentType.BUSINESS_SUMMARY_FILING_HISTORY: 'summary',
}


def get_business_document(identifier: str, document_type: Document.DocumentType):
    """Get the business document for the given identifier and type."""
    document_name = DOCUMENT_NAME[document_type]
    if not document_name:
        raise ApiConnectionException(HTTPStatus.NOT_IMPLEMENTED,
                                     [{'message': f'Report type for {document_type.name} does not exist.'}])

    lear_svc_url = f"{current_app.config.get('LEAR_SVC_URL')}/businesses/{identifier}/documents/{document_name}"
    try:
        token = get_bearer_token()
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/pdf'}
        lear_response = requests.get(url=lear_svc_url, headers=headers, timeout=20.0)
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        current_app.logger.error('LEAR connection failure:', err)
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{'message': 'Unable to get business document pdf from lear.'}])
    return lear_response


def get_business_filing_document(identifier: str, filing_id: int):
    """Get the business filing document for the given identifier and id."""
    lear_svc_url = f"{current_app.config.get('LEAR_SVC_URL')}/businesses/{identifier}/filings/{filing_id}"
    try:
        token = get_bearer_token()
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/pdf'}
        lear_response = requests.get(url=lear_svc_url, headers=headers, timeout=20.0)
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        current_app.logger.error('LEAR connection failure:', err)
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{'message': 'Unable to get business document pdf from lear.'}])
    return lear_response
