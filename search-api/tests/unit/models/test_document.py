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
import pytest

from search_api.exceptions import BusinessException
from search_api.models import Document


def test_document_save(session):
    """Assert that a document can be stored in the service."""
    document = Document(document_type=Document.DocumentTypes.CERTIFICATE_OF_GOOD_STANDING,
                        _document_key='test')

    document.save()

    assert document.id is not None


def test_find_by_document_key(session):
    """Assert that a document can be retrieved using document key."""
    document = Document(document_type=Document.DocumentTypes.LETTER_UNDER_SEAL,
                        _document_key='test')

    document.save()

    u = Document.find_by_document_key('test')

    assert u is not None
    assert u.id == document.id


def test_find_by_id(session):
    """Assert that a document can be retrieved using document id."""
    document = Document(document_type=Document.DocumentTypes.LETTER_UNDER_SEAL,
                        _document_key='test')

    document.save()

    u = Document.find_by_id(document.id)

    assert u is not None
