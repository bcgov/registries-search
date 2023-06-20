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
"""Manages solr synonym lists (used for prepping solr queries over synonym fields)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from .db import db


class SolrSynonymList(db.Model):
    """Used to hold solr synonym information."""

    __tablename__ = 'bor_solr_synonym_lists'

    synonym = db.Column(db.String(250), primary_key=True)
    synonym_list = db.Column(JSONB)
    last_update_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, index=True)

    @classmethod
    def find_by_synonym(cls, synonym: str) -> SolrSynonymList:
        """Return all the solr synonym objects for synonyms including the given phrase/word."""
        return cls.query.filter_by(synonym=synonym.lower()).one_or_none()

    @classmethod
    def find_all_beginning_with_phrase(cls, phrase: str) -> SolrSynonymList:
        """Return all the solr synonym objects for synonyms including the given phrase/word."""
        return cls.query.filter(cls.synonym.ilike(f'{phrase}%')).all()

    def save(self) -> SolrSynonymList:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self
