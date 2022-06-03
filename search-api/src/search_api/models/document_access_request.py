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
"""Table for storing document access request details."""
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import backref

from .db import db


class DocumentAccessRequest(db.Model):
    """Used to hold the document access request information."""

    class Status(str, Enum):
        """Enum of the request statuses."""

        CREATED = 'CREATED'
        PAID = 'PAID'
        ERROR = 'ERROR'
        COMPLETED = 'COMPLETED'

    __versioned__ = {}
    __tablename__ = 'document_access_request'

    id = db.Column(db.Integer, primary_key=True)
    business_identifier = db.Column('business_identifier', db.String(10), index=True)
    status = db.Column('status', db.String(20), default=Status.CREATED)
    account_id = db.Column('account_id', db.Integer)
    _payment_status_code = db.Column('payment_status_code', db.String(50))
    _payment_token = db.Column('payment_id', db.String(4096))
    _payment_completion_date = db.Column('payment_completion_date', db.DateTime(timezone=True))
    submission_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime(timezone=True))
    _output_file_key = db.Column('output_file_key', db.String(100), nullable=False)
    _submitter_id = db.Column('submitter_id', db.Integer, db.ForeignKey('users.id'))

    submitter = db.relationship('User', backref=backref('filing_submitter', uselist=False),
                                foreign_keys=[_submitter_id])
    documents = db.relationship('Document', backref='document_access_request', cascade='all, delete, delete-orphan')

    def save(self):
        """Store the request into the db."""
        db.session.add(self)
        db.session.commit()
