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
from __future__ import annotations

from search_api.enums import DocumentType

from .db import db


class Document(db.Model):
    """Used to hold the documents requested in an access request."""

    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Enum(DocumentType), index=True)
    document_key = db.Column('document_key', db.String(100), nullable=False)
    file_name = db.Column('file_name', db.String(100))
    access_request_id = db.Column('access_request_id', db.Integer, db.ForeignKey('document_access_request.id'))

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        document = {
            'id': self.id,
            'documentType': self.document_type.name,
            'documentKey': self.document_key,
            'fileName': self.file_name
        }
        return document

    @classmethod
    def find_by_id(cls, document_id: int = None) -> Document:
        """Return a Document that has the specified id."""
        return cls.query.filter_by(id=document_id).one_or_none()

    @classmethod
    def find_by_document_key(cls, document_key: str) -> Document:
        """Return a Document having the specified document key."""
        return cls.query.filter_by(document_key=document_key).one_or_none()

    def save(self):
        """Store the Document."""
        db.session.add(self)
        db.session.commit()
