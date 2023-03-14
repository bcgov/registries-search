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
"""Tests to assure the Document Access Request Class.

Test-Suite to ensure that the Document Access Request Class is working as expected.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User


def test_document_request_save(session):
    """Assert that a document access request can be stored in the service."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id = 123,
        submission_date = datetime.utcnow(),
        expiry_date = datetime.now()+ relativedelta(days=7)
    )

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL.value, document_key='test')
    document_access_request.documents.append(document)

    document_access_request.save()

    assert document_access_request.id is not None


def test_find_active_requests(session):
    """Assert that active access requests for a business by an account are returned."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id=123,
        payment_token=567,
        payment_completion_date=datetime.utcnow(),
        submission_date=datetime.utcnow(),
        expiry_date=datetime.now() + relativedelta(days=7),
        status=DocumentAccessRequest.Status.PAID.value
    )

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document_1 = Document(document_type=DocumentType.LETTER_UNDER_SEAL.value, document_key='test1')
    document_2 = Document(document_type=DocumentType.CERTIFICATE_OF_GOOD_STANDING.value, document_key='test2')
    document_3 = Document(document_type=DocumentType.CERTIFICATE_OF_STATUS.value, document_key='test3')
    document_access_request.documents.append(document_1)
    document_access_request.documents.append(document_2)
    document_access_request.documents.append(document_3)

    document_access_request.save()

    access_request = DocumentAccessRequest.find_active_requests(document_access_request.account_id,
                                                                document_access_request.business_identifier)
    assert len(access_request) == 1
    assert len(access_request[0].documents) == 3


def test_find_by_id(session):
    """Assert that a document access request can be retrieved using id."""
    """Assert that a document access request can be stored in the service."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id=123,
        submission_date=datetime.utcnow(),
        expiry_date=datetime.now() + relativedelta(days=7)
    )

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL.value, document_key='test')
    document_access_request.documents.append(document)

    document_access_request.save()
    assert document_access_request.id is not None

    access_request = DocumentAccessRequest.find_by_id(document_access_request.id)
    assert access_request is not None


def test_document_access_request_json(session):
    """Assert that active access requests for a business by an account are returned."""
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        business_name='test',
        account_id=123,
        payment_token=567,
        payment_status_code='COMPLETED',
        payment_completion_date=datetime.utcnow(),
        submission_date=datetime.utcnow(),
        expiry_date=datetime.now() + relativedelta(days=7),
        status=DocumentAccessRequest.Status.PAID
    )

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document_1 = Document(document_type=DocumentType.LETTER_UNDER_SEAL, document_key='test1')
    document_2 = Document(document_type=DocumentType.CERTIFICATE_OF_GOOD_STANDING, document_key='test2')
    document_access_request.documents.append(document_1)
    document_access_request.documents.append(document_2)

    document_access_request.save()
    access_request_json = {
       'businessIdentifier': 'CP1234567',
       'businessName': 'test',
       'documents': [
           {
                'documentKey': 'test1',
                'documentType': document_1.document_type.name,
                'fileName': None,
                'id': document_1.id
           },
           {
                'documentKey': 'test2',
                'documentType': document_2.document_type.name,
                'fileName': None,
                'id': document_2.id
            }
       ],
       'expiryDate': document_access_request.expiry_date.isoformat(),
       'id': document_access_request.id,
       'outputFileKey': None,
       'paymentStatus': 'COMPLETED',
       'status': 'PAID',
       'submissionDate': document_access_request.submission_date.isoformat(),
       'submitter': 'firstname lastname'
    }

    assert access_request_json == document_access_request.json

