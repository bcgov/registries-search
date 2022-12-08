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

"""Tests to verify the request handler works as expected."""

from datetime import datetime
from http import HTTPStatus

from flask import current_app, g

from search_api.models import DocumentAccessRequest, User
from search_api.request_handlers.document_access_request_handler import create_invoice, save_request


DOCUMENT_ACCESS_REQUEST_TEMPLATE = {
    "documentAccessRequest":{
        "documents": [
            {
                "type": "BUSINESS_SUMMARY_FILING_HISTORY"
            }
        ]
    }
}

def test_save_request(client, session, jwt, mocker):
    """Assert that request can be saved."""
    g.jwt_oidc_token_info={}
    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    user.save()
    mocker.patch('search_api.models.User.get_or_create_user_by_jwt', return_value=user)
    document_access_request = save_request(1, 1, DOCUMENT_ACCESS_REQUEST_TEMPLATE)
    assert document_access_request.id
    assert len(document_access_request.documents) == 1
    assert document_access_request.submitter.firstname == user.firstname


def test_create_invoice(client, session, jwt, mocker):
    """Assert that access request is updated with payment details."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id=123,
        submission_date=datetime.utcnow()
    )

    document_access_request.save()

    request_json = {
        'header': {
            'folioNumber': '1234'
        },
        'documentAccessRequest': {
            'businessIdentifier': document_access_request.business_identifier
        }
    }

    mock_response = MockResponse({'id': 123},HTTPStatus.CREATED)
    mocker.patch('search_api.request_handlers.document_access_request_handler.create_payment',
                 return_value=mock_response)
    mocker.patch('search_api.request_handlers.document_access_request_handler.get_role',
                 return_value='basic')

    business_json = {'identifier': 'BC1234567', 'legalType': 'BC', 'legalName': 'Test - 1234567'}
    create_invoice(document_access_request, jwt, request_json, business_json)

    document_access_request = DocumentAccessRequest.find_by_id(document_access_request.id)
    assert document_access_request.payment_token
    assert document_access_request.payment_completion_date
    assert document_access_request.expiry_date


def test_create_invoice_failure(client, session, jwt, mocker):
    """Assert that access request is updated with payment error."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id=123,
        submission_date=datetime.utcnow()
    )
    document_access_request.save()

    request_json = {
        'header': {
            'folioNumber': '1234'
        },
        'documentAccessRequest': document_access_request
    }

    mock_response = MockResponse({'type': 'BAD_REQUEST'},HTTPStatus.BAD_REQUEST)
    mocker.patch('search_api.request_handlers.document_access_request_handler.create_payment',
                 return_value=mock_response)
    mocker.patch('search_api.request_handlers.document_access_request_handler.get_role',
                 return_value='basic')
    business_json = {'identifier': 'BC1234567', 'legalType': 'BC', 'legalName': 'Test - 1234567'}
    create_invoice(document_access_request, jwt, request_json, business_json)

    document_access_request = DocumentAccessRequest.find_by_id(document_access_request.id)

    assert document_access_request.payment_status_code == 'BAD_REQUEST'
    assert document_access_request.payment_token is None
    assert document_access_request.payment_completion_date is None
    assert document_access_request.expiry_date is None


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
