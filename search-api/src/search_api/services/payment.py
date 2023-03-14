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
from flask import current_app
from flask_jwt_oidc import JwtManager

from search_api.enums import DocumentType
from search_api.exceptions import ApiConnectionException
from search_api.models import UserRoles
from search_api.services import BASIC_USER, SBC_STAFF, STAFF_ROLE, is_staff


# Maps Document Type to Pay API Filing Type
DOCUMENT_TYPE_TO_FILING_TYPE = {
    DocumentType.BUSINESS_SUMMARY_FILING_HISTORY.name: {
        BASIC_USER: 'BSRCH',
        STAFF_ROLE: 'SBSRCH',
        SBC_STAFF: 'SBSRCH'
    },
    DocumentType.CERTIFICATE_OF_GOOD_STANDING.name: {
        BASIC_USER: 'CGOOD',
        STAFF_ROLE: 'CGOOD',
        SBC_STAFF: 'CGOOD'
    },
    DocumentType.CERTIFICATE_OF_STATUS.name: {
        BASIC_USER: 'CSTAT',
        STAFF_ROLE: 'CSTAT',
        SBC_STAFF: 'CSTAT'
    },
    DocumentType.LETTER_UNDER_SEAL.name: {
        BASIC_USER: 'LSEAL',
        STAFF_ROLE: 'LSEAL',
        SBC_STAFF: 'LSEAL'
    }
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


# pylint: disable=too-many-locals
def create_payment(account_id: str, filing_types: [], user_jwt: JwtManager, header: dict, business_json: str) -> \
        Tuple[int, dict, int]:
    """Create the invoice for the document access request."""
    payment_svc_url = current_app.config.get('PAYMENT_SVC_URL')

    payload = PAYMENT_REQUEST_TEMPLATE
    payload['filingInfo']['filingTypes'] = filing_types

    if folio_number := header.get('folioNumber', None):
        payload['filingInfo']['folioNumber'] = folio_number

    if is_staff(user_jwt):
        special_role = UserRoles.STAFF
    else:
        special_role = None

    if special_role:
        account_info = {}
        if header.get('routingSlipNumber', None):
            account_info['routingSlip'] = header.get('routingSlipNumber')
        if header.get('bcolAccountNumber', None):
            account_info['bcolAccountNumber'] = header.get('bcolAccountNumber')
        if header.get('datNumber', None):
            account_info['datNumber'] = header.get('datNumber')

        if account_info:
            payload['accountInfo'] = account_info

    legal_type = business_json.get('legalType')
    label_name = 'Registration Number' if legal_type in ['SP', 'GP'] else 'Incorporation Number'

    payload['details'] = [{
        'label': f'{label_name}: ',
        'value': business_json.get('identifier')
    }]
    payload['businessInfo']['businessIdentifier'] = business_json.get('identifier')

    try:
        token = user_jwt.get_token_auth_header()
        headers = {'Authorization': 'Bearer ' + token,
                   'Content-Type': 'application/json',
                   'Account-Id': account_id}
        pay_api_timeout = current_app.config.get('PAY_API_TIMEOUT')
        payment_response = requests.post(url=payment_svc_url, json=payload, headers=headers, timeout=pay_api_timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
        current_app.logger.error('Payment connection failure:', err)
        raise ApiConnectionException(HTTPStatus.PAYMENT_REQUIRED,
                                     [{'message': 'Unable to create invoice for payment.'}]) from err
    return payment_response
