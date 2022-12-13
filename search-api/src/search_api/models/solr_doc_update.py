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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref

from search_api.enums import SolrDocStatus

from .db import db


class SolrDocUpdate(db.Model):
    """Used to hold the solr doc update information."""

    __tablename__ = 'solr_doc_updates'

    id = db.Column(db.Integer, primary_key=True)
    doc = db.Column(JSONB)
    identifier = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Enum(SolrDocStatus), default=SolrDocStatus.PENDING, index=True)
    submission_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, index=True)
    _submitter_id = db.Column('submitter_id', db.Integer, db.ForeignKey('users.id'))

    submitter = db.relationship('User', backref=backref('submitter', uselist=False), foreign_keys=[_submitter_id])
