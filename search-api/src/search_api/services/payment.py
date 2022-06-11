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
"""Manages filing type codes and payment service interactions."""

from http import HTTPStatus
from typing import Tuple

import requests
from requests import exceptions
from flask import current_app
from flask_jwt_oidc import JwtManager

from search_api.exceptions import ApiConnectionException
from search_api.models import Document


# Maps Document Type to Pay API Filing Type
DOCUMENT_TYPE_TO_FILING_TYPE = {
    Document.DocumentType.BUSINESS_SUMMARY_FILING_HISTORY.name: 'BSRCH'
}

PAYMENT_REQUEST_TEMPLATE = {
    'filingInfo': {
        'filingTypes': [
            {'filingTypeCode': ''}
        ]
    },
    'businessInfo': {
        'corpType': 'BUS'
    }
}


def create_payment(account_id: str, filing_types: [], user_jwt: JwtManager) -> Tuple[int, dict, int]:
    """Create the invoice for the document access request."""
    payment_svc_url = current_app.config.get('PAYMENT_SVC_URL')

    payload = PAYMENT_REQUEST_TEMPLATE
    payload['filingInfo']['filingTypes'] = filing_types
    try:
        token = user_jwt.get_token_auth_header()
        headers = {'Authorization': 'Bearer ' + token,
                   'Content-Type': 'application/json',
                   'Account-Id': account_id}
        payment_response = requests.post(url=payment_svc_url, json=payload, headers=headers, timeout=20.0)
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        current_app.logger.error('Payment connection failure:', err)
        raise ApiConnectionException(HTTPStatus.PAYMENT_REQUIRED,
                                     [{'message': 'Unable to create invoice for payment.'}])
    return payment_response
