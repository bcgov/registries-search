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
from __future__ import annotations

import secrets
import string
from datetime import datetime
from http import HTTPStatus
from typing import Tuple

from dateutil.relativedelta import relativedelta
from flask import current_app, g
from flask_jwt_oidc import JwtManager

from search_api.enums import DocumentType
from search_api.exceptions import ApiConnectionException
from search_api.models import Document, DocumentAccessRequest, User
from search_api.services.payment import DOCUMENT_TYPE_TO_FILING_TYPE, create_payment
from search_api.services import get_role, STAFF_ROLE


def save_request(account_id, business_identifier, request_json) -> DocumentAccessRequest:
    """Validate and saves the request in db."""
    user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)
    document_access_request: DocumentAccessRequest = DocumentAccessRequest(
        business_identifier=business_identifier,
        account_id=account_id,
        _submitter_id=user.id,
        submission_date=datetime.utcnow(),
        business_name=request_json.get('business', {}).get('businessName')
    )
    for doc in request_json.get('documentAccessRequest', {}).get('documents', []):
        document_type = DocumentType.get_enum_by_name(doc.get('type'))
        document = Document(
            document_type=document_type,
            document_key=_generate_key()
        )
        document_access_request.documents.append(document)
    document_access_request.save()
    return document_access_request


def create_invoice(document_access_request: DocumentAccessRequest, user_jwt: JwtManager, request_json: dict,
                   business_json: dict) -> Tuple[int, dict, int]:
    """Create the invoice in SBC Payments and updates the access request record with payment details."""
    try:
        filing_types = []
        header = request_json.get('header', {})
        waive_fees = False
        role = get_role(user_jwt, document_access_request.account_id)
        if role in [STAFF_ROLE] and header.get('waiveFees', False):
            waive_fees = True
        for document in document_access_request.documents:
            filing_types.append({
                'filingTypeCode': DOCUMENT_TYPE_TO_FILING_TYPE.get(document.document_type.name).get(role),
                'waiveFees': waive_fees})
        payment_response = create_payment(str(document_access_request.account_id), filing_types, user_jwt,
                                          header, business_json)

        if payment_response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            payment_completion_date = datetime.utcnow()
            pid = payment_response.json().get('id')
            document_access_request.payment_token = pid
            document_access_request.payment_status_code = payment_response.json().get('statusCode', '')
            document_access_request.payment_completion_date = payment_completion_date
            validity_in_days = current_app.config.get('DOCUMENT_REQUEST_VALIDITY_DURATION', 14)
            document_access_request.expiry_date = payment_completion_date + relativedelta(days=validity_in_days)
            document_access_request.status = DocumentAccessRequest.Status.PAID
            document_access_request.save()
            return {'isPaymentActionRequired': payment_response.json().get('isPaymentActionRequired',
                                                                           False)}, HTTPStatus.CREATED

        if payment_response.status_code == HTTPStatus.BAD_REQUEST:
            # Set payment error type used to retrieve error messages from pay-api
            error_type = payment_response.json().get('type')
            document_access_request.payment_status_code = error_type
            document_access_request.save()
            return {'error': payment_response.json()}, HTTPStatus.PAYMENT_REQUIRED

        current_app.logger.debug(f'status: {payment_response.status_code}, json: {payment_response.json()}.')
        current_app.logger.error('Received unhandled pay-api error.')
        return {'error': {'detail': payment_response.json(), 'type': 'UNHANDLED'}}, HTTPStatus.PAYMENT_REQUIRED
    except ApiConnectionException as connection_error:
        return {'error': connection_error.detail}, HTTPStatus.PAYMENT_REQUIRED


def _generate_key():
    allowed_characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(allowed_characters) for _ in range(9))
