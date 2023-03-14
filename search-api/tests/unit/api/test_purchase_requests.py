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

from datetime import datetime
from http import HTTPStatus

from dateutil.relativedelta import relativedelta

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User
from search_api.services.authz import STAFF_ROLE
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

def test_get_business_documents_by_account(session, client, jwt):
    """Assert that document requests are returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/purchases',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': account_id})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 1


def test_get_business_documents_by_account_invalid_account(session, client, jwt):
    """Assert that document requests are not returned."""
    account_id = 123
    business_identifier = 'CP1234567'
    create_document_access_request(business_identifier, account_id, True)
    rv = client.get(f'/api/v1/purchases',
                    headers=create_header(jwt, [STAFF_ROLE], business_identifier, **{'Accept-Version': 'v1',
                                                                                     'Account-Id': 456})
                    )
    # check
    assert rv.status_code == HTTPStatus.OK
    assert 'documentAccessRequests' in rv.json
    assert len(rv.json['documentAccessRequests']) == 0


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
        document_access_request.status=DocumentAccessRequest.Status.PAID

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL, document_key='test')
    document_access_request.documents.append(document)

    document_access_request.save()

    assert document_access_request.id is not None
    return document_access_request