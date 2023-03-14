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
"""Manages solr doc updates made to the Search Core (tracks updates made via the api)."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref

from .db import db


class SolrDoc(db.Model):
    """Used to hold the solr doc information."""

    __tablename__ = 'solr_docs'

    id = db.Column(db.Integer, primary_key=True)
    doc = db.Column(JSONB)
    identifier = db.Column(db.String(10), nullable=False, index=True)
    submission_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, index=True)
    _submitter_id = db.Column('submitter_id', db.Integer, db.ForeignKey('users.id'))

    submitter = db.relationship('User', backref=backref('submitter', uselist=False), foreign_keys=[_submitter_id])

    solr_doc_events = db.relationship('SolrDocEvent', lazy='dynamic')

    @classmethod
    def find_most_recent_by_identifier(cls, identifier: str) -> SolrDoc:
        """Return most recently submitted SolrDoc by identifier."""
        return cls.query.filter_by(identifier=identifier).order_by(cls.submission_date.desc()).first()

    @staticmethod
    def get_updated_identifiers_after_date(date: datetime) -> List[str]:
        """Return all identifiers with a submitted SolrDoc after the date."""
        return [x[0] for x in db.session.query(SolrDoc.identifier)
                .filter(SolrDoc.submission_date > date)
                .group_by(SolrDoc.identifier).all()]

    def save(self) -> SolrDoc:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
