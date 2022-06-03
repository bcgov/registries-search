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
"""Table for storing document details."""
from enum import Enum

from .db import db


class Document(db.Model):
    """Used to hold the documents requested in an access request."""

    class DocumentTypes(str, Enum):
        """Enum of the document types."""

        BUSINESS_SUMMARY_FILING_HISTORY = 'summary_history'
        CERTIFICATE_OF_GOOD_STANDING = 'cogs'
        CERTIFICATE_OF_STATUS = 'cert_of_status'
        LETTER_UNDER_SEAL = 'letter_under_seal'

    __versioned__ = {}
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(30), index=True)
    _document_key = db.Column('document_key', db.String(100), nullable=False)
    _file_name = db.Column('file_name', db.String(100))
    _file_key = db.Column('file_key', db.String(100))
    access_request_id = db.Column('access_request_id', db.Integer, db.ForeignKey('document_access_request.id'))

    @classmethod
    def find_by_id(cls, submitter_id: int = None):
        """Return a Document that has the specified id."""
        return cls.query.filter_by(id=submitter_id).one_or_none()

    @classmethod
    def find_by_document_key(cls, document_key: str):
        """Return a Document having the specified document key."""
        return cls.query.filter_by(_document_key=document_key).one_or_none()

    def save(self):
        """Store the Document."""
        db.session.add(self)
        db.session.commit()
