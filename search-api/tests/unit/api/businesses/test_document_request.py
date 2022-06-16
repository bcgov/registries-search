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
"""Test-Suite to ensure that the document access endpoints/functions work as expected."""
import json
from datetime import datetime
from http import HTTPStatus

from dateutil.relativedelta import relativedelta

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User
from search_api.services.authz import STAFF_ROLE
from search_api.services.validator import RequestValidator
from tests.unit import MockResponse
from tests.unit.services.utils import create_header


DOCUMENT_ACCESS_REQUEST_TEMPLATE = {
    "documentAccessRequest":{
        "documents": [
            {
                "type": "BUSINESS_SUMMARY_FILING_HISTORY"
            }
        ]
    }
}


def test_get_business_documents(session, client, jwt):
    """Assert that document requests are returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 1


def test_get_business_documents_no_payment(session, client, jwt):
    """Assert that document requests with no payment are not returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    create_document_access_request(business_identifier, account_id, False)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 0


def test_get_business_documents_no_records(session, client, jwt):
    """Assert that document requests are not returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 0


def test_get_business_documents_invalid_account(session, client, jwt):
    """Assert that document requests are not returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    create_document_access_request(business_identifier, account_id)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': 234})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 0



def test_get_business_document_by_id(session, client, jwt):
    """Assert that the document request having the specified id is returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    access_request = create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests/{access_request.id}',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequest' in rv.json


def test_get_business_document_by_invalid_id(session, client, jwt):
    """Assert that document request is not returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    access_request = create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests/567',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_get_business_document_by_id_unauthorized(session, client, jwt):
    """Assert that unauthorized error is returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    access_request = create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/businesses/{business_identifier}/documents/requests/{access_request.id}',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': 567})
                    )
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_post_business_document(session, client, jwt, mocker):
    """Assert that unauthorized error is returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    mocker.patch('search_api.services.validator.RequestValidator.validate_document_access_request',
                 return_value=[])
    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss')
    mocker.patch('search_api.models.User.get_or_create_user_by_jwt', return_value=user)
    mock_response = MockResponse({'id': 123}, HTTPStatus.CREATED)
    mocker.patch('search_api.request_handlers.document_access_request_handler.create_payment',
                 return_value=mock_response)
    api_response = client.post(f'/api/v1/businesses/{business_identifier}/documents/requests',
                     data=json.dumps(DOCUMENT_ACCESS_REQUEST_TEMPLATE),
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id,
                                                                                     'content-type': 'application/json'
                                                                                     })
                    )
    # check
    assert api_response.status_code == HTTPStatus.CREATED
    response_json = api_response.json
    assert response_json['expiryDate']
    assert response_json['id']


def test_post_business_document_payment_failure(session, client, jwt, mocker):
    """Assert that unauthorized error is returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    mocker.patch('search_api.services.validator.RequestValidator.validate_document_access_request',
                 return_value=[])
    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss')
    mocker.patch('search_api.models.User.get_or_create_user_by_jwt', return_value=user)
    mock_response = MockResponse({'id': 123}, HTTPStatus.BAD_REQUEST)
    mocker.patch('search_api.request_handlers.document_access_request_handler.create_payment',
                 return_value=mock_response)
    api_response = client.post(f'/api/v1/businesses/{business_identifier}/documents/requests',
                     data=json.dumps(DOCUMENT_ACCESS_REQUEST_TEMPLATE),
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id,
                                                                                     'content-type': 'application/json'
                                                                                     })
                    )
    # check
    assert api_response.status_code == HTTPStatus.PAYMENT_REQUIRED
    response_json = api_response.json
    assert not response_json['expiryDate']
    assert response_json['id']


def create_document_access_request(identifier: str, account_id: int, is_paid: bool = False):
    """Creates a document access request."""
    document_access_request = DocumentAccessRequest(
            business_identifier=identifier,
            account_id = account_id,
            submission_date = datetime.utcnow(),
            expiry_date = datetime.now()+ relativedelta(days=7)
    )
    if is_paid:
        document_access_request.payment_token=567
        document_access_request.payment_completion_date=datetime.utcnow()
        document_access_request.status=DocumentAccessRequest.Status.PAID.value

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss')
    document_access_request.submitter = user

    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL.value, document_key='test')
    document_access_request.documents.append(document)

    document_access_request.save()

    assert document_access_request.id is not None
    return document_access_request
