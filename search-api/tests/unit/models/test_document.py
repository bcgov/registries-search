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
"""Tests to assure the Document Class.

Test-Suite to ensure that the Document Class is working as expected.
"""
from search_api.enums import DocumentType
from search_api.models import Document


def test_document_save(session):
    """Assert that a document can be stored in the service."""
    document = Document(document_type=DocumentType.CERTIFICATE_OF_GOOD_STANDING,
                        document_key='test')

    document.save()

    assert document.id is not None


def test_find_by_document_key(session):
    """Assert that a document can be retrieved using document key."""
    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL,
                        document_key='test')

    document.save()

    retrieved_document = Document.find_by_document_key('test')

    assert retrieved_document is not None
    assert retrieved_document.id == document.id


def test_find_by_id(session):
    """Assert that a document can be retrieved using document id."""
    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL,
                        document_key='test')

    document.save()

    retrieved_document = Document.find_by_id(document.id)

    assert retrieved_document is not None


def test_document_json(session):
    """Assert that a document can be retrieved using document id."""
    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL,
                        document_key='test')

    document.save()

    document_json={
        'documentKey': document.document_key,
        'documentType': document.document_type.name,
        'fileName': None,
        'id': document.id
    }

    assert document.json == document_json
