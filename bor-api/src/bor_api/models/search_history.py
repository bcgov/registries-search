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

from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import JSONB

from bor_api.enums import SearchAccessLevel

from .db import db


class SearchHistory(db.Model):
    """Used to hold search history information."""

    __tablename__ = "search_history"

    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(JSONB)
    results = db.Column(JSONB)
    search_date = db.Column(db.DateTime(timezone=True), default=datetime.now(UTC), index=True)
    submitter_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    submitter_account_id = db.Column(db.Integer, index=True, nullable=True)
    access_level = db.Column(db.Enum(SearchAccessLevel), index=True, nullable=True)

    user = db.relationship("User", back_populates="searches")

    def save(self) -> SearchHistory:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
