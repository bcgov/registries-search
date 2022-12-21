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

from search_api.enums import SolrDocEventStatus, SolrDocEventType

from .db import db


class SolrDocEvent(db.Model):  # pylint: disable=too-few-public-methods
    """Used to hold event information for a solr doc."""

    __tablename__ = 'solr_doc_events'

    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    event_status = db.Column(db.Enum(SolrDocEventStatus), default=SolrDocEventStatus.PENDING)
    event_type = db.Column(db.Enum(SolrDocEventType), nullable=False)

    solr_doc_id = db.Column(db.Integer, db.ForeignKey('solr_docs.id'), index=True)

    def save(self) -> SolrDocEvent:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
