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

from sqlalchemy import event

from search_api.enums import SolrDocEventStatus, SolrDocEventType

from .db import db


class SolrDocEvent(db.Model):  # pylint: disable=too-few-public-methods
    """Used to hold event information for a solr doc."""

    __tablename__ = 'solr_doc_events'

    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    event_last_update = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    event_status = db.Column(db.Enum(SolrDocEventStatus), default=SolrDocEventStatus.PENDING)
    event_type = db.Column(db.Enum(SolrDocEventType), nullable=False)

    solr_doc_id = db.Column(db.Integer, db.ForeignKey('solr_docs.id'), index=True)

    def save(self) -> SolrDocEvent:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
    
    @classmethod
    def get_events_by_status(cls,
                             statuses: list[SolrDocEventStatus],
                             event_type: SolrDocEventType = None,
                             start_date: datetime = None,
                             limit: int = None) -> list[SolrDocEvent]:
        """Update the status of the given events."""
        query = cls.query.filter(cls.event_status.in_(statuses))
        if event_type:
            query = query.filter(cls.event_type == event_type)
        if start_date:
            query = query.filter(cls.event_date > start_date)

        query = query.order_by(cls.event_date)
        if limit:
            query = query.limit(limit)

        return query.all()

    @classmethod
    def update_events_status(cls, status: SolrDocEventStatus, events: list[SolrDocEvent]):
        """Update the status of the given events."""
        for doc_event in events:
            doc_event.event_status = status
            db.session.add(doc_event)
        db.session.commit()


@event.listens_for(SolrDocEvent, 'before_update')
def receive_before_change(mapper, connection, target: SolrDocEvent):  # pylint: disable=unused-argument
    """Set the last updated value."""
    target.event_last_update = datetime.utcnow()
