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
from __future__ import annotations

from datetime import datetime, timezone
from enum import auto
from http import HTTPStatus

from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref

from search_api.exceptions import BusinessException
from search_api.utils.base import BaseEnum

from .db import db


class DocumentAccessRequest(db.Model):
    """Used to hold the document access request information."""

    class Status(BaseEnum):
        """Enum of the request statuses."""

        CREATED = auto()
        PAID = auto()
        ERROR = auto()
        COMPLETED = auto()  # After all docs are generated and stored.

    __tablename__ = 'document_access_request'

    id = db.Column(db.Integer, primary_key=True)
    business_identifier = db.Column('business_identifier', db.String(10), index=True)
    business_name = db.Column('business_name', db.String(1000))
    status = db.Column('status', db.Enum(Status), default=Status.CREATED)
    account_id = db.Column('account_id', db.Integer)
    _payment_status_code = db.Column('payment_status_code', db.String(50))
    _payment_token = db.Column('payment_id', db.String(4096))
    _payment_completion_date = db.Column('payment_completion_date', db.DateTime(timezone=True))
    submission_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime(timezone=True))
    _output_file_key = db.Column('output_file_key', db.String(100))
    _submitter_id = db.Column('submitter_id', db.Integer, db.ForeignKey('users.id'))

    submitter = db.relationship('User', backref=backref('filing_submitter', uselist=False),
                                foreign_keys=[_submitter_id])
    documents = db.relationship('Document', backref='document_access_request', cascade='all, delete, delete-orphan')

    @hybrid_property
    def is_active(self) -> bool:
        """Return if this object is active or not."""
        return self.expiry_date > datetime.now(timezone.utc)

    @hybrid_property
    def payment_status_code(self):
        """Property containing the payment error type."""
        return self._payment_status_code

    @payment_status_code.setter
    def payment_status_code(self, error_type: str):
        if self.locked:
            self._raise_default_lock_exception()
        self._payment_status_code = error_type

    @hybrid_property
    def payment_token(self):
        """Property containing the payment token."""
        return self._payment_token

    @payment_token.setter
    def payment_token(self, token: int):
        if self.locked:
            self._raise_default_lock_exception()
        self._payment_token = token

    @hybrid_property
    def payment_completion_date(self):
        """Property containing the date the payment cleared."""
        return self._payment_completion_date

    @payment_completion_date.setter
    def payment_completion_date(self, value: datetime):

        if self.locked or self._payment_token:
            self._payment_completion_date = value

        else:
            raise BusinessException(
                error='Payment Dates cannot be set.',
                status_code=HTTPStatus.FORBIDDEN
            )

    @property
    def locked(self):
        """Return the locked state of the request.

        Once an access request has an payment attached, it can no longer be altered and is locked.
        """
        insp = inspect(self)
        attr_state = insp.attrs._payment_token  # pylint: disable=protected-access;
        if self._payment_token and not attr_state.history.added:
            return True
        return False

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        document_access_request = {
            'id': self.id,
            'businessIdentifier': self.business_identifier,
            'businessName': self.business_name,
            'status': self.status.name,
            'paymentStatus': self.payment_status_code,
            'submissionDate': self.submission_date.isoformat(),
            'expiryDate': self.expiry_date.isoformat() if self.expiry_date else None,
            'outputFileKey': self._output_file_key,
            'submitter': self.submitter.display_name if self.submitter else None
        }

        documents = []

        for document in self.documents:
            documents.append(document.json)

        document_access_request['documents'] = documents

        return document_access_request

    @classmethod
    def find_active_requests(cls, account_id: int, business_identifier: str = None):
        """Return all active requests matching specified account id and business identifier."""
        query = db.session.query(DocumentAccessRequest).\
            filter(DocumentAccessRequest.account_id == account_id).\
            filter(DocumentAccessRequest.is_active).\
            filter(DocumentAccessRequest.status.in_([DocumentAccessRequest.Status.PAID,
                                                     DocumentAccessRequest.Status.COMPLETED]))
        if business_identifier:
            query = query.filter(DocumentAccessRequest.business_identifier == business_identifier)

        query = query.order_by(DocumentAccessRequest.id.desc())
        return query.all()

    @classmethod
    def find_by_id(cls, request_id: int) -> DocumentAccessRequest:
        """Return a request having the specified id."""
        return cls.query.filter_by(id=request_id).one_or_none()

    @staticmethod
    def _raise_default_lock_exception():
        raise BusinessException(
            error='Request cannot be modified after the invoice is created.',
            status_code=HTTPStatus.FORBIDDEN
        )

    def save(self):
        """Store the request into the db."""
        db.session.add(self)
        db.session.commit()
