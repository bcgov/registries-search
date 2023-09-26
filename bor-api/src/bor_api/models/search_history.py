# Copyright © 2023 Province of British Columbia
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
"""Manages user search history."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from .db import db


class SearchHistory(db.Model):  # pylint: disable=too-few-public-methods
    """Used to hold search history information."""

    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(JSONB)
    results = db.Column(JSONB)
    search_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, index=True)
    submitter_id = db.Column('submitter_id', db.Integer, db.ForeignKey('users.id'), index=True)

    user = db.relationship('User', back_populates='searches')

    def save(self) -> SearchHistory:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
