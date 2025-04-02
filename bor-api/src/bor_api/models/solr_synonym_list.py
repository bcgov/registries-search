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

from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import JSONB

from bor_api.enums import SolrSynonymType
from bor_api.utils.util import utcnow

from .db import db


class SolrSynonymList(db.Model):
    """Used to hold solr synonym information."""

    __tablename__ = "bor_solr_synonym_lists"

    id = db.Column(db.Integer, primary_key=True)
    synonym = db.Column(db.String(250), index=True, nullable=False)
    synonym_list = db.Column(JSONB)
    synonym_type = db.Column(db.Enum(SolrSynonymType), default=SolrSynonymType.NAME, index=True)
    last_update_date = db.Column(db.DateTime(timezone=True), default=utcnow)

    @classmethod
    def find_by_synonym(cls, synonym: str, synonym_type: SolrSynonymType) -> SolrSynonymList:
        """Return all the solr synonym objects for synonyms including the given phrase/word."""
        return cls.query.filter_by(synonym=synonym.lower(), synonym_type=synonym_type).one_or_none()

    @classmethod
    def find_all_beginning_with_phrase(cls, phrase: str, synonym_type: SolrSynonymType) -> SolrSynonymList:
        """Return all the solr synonym objects for synonyms including the given phrase/word."""
        return cls.query.filter_by(synonym_type=synonym_type).filter(cls.synonym.ilike(f"{phrase}%")).all()

    def save(self) -> SolrSynonymList:
        """Store the update into the db."""
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def create_or_replace_all(synonyms: dict[str, list[str]], synonym_type: SolrSynonymType):
        """Add or replace the given synonyms inside the db."""
        for synonym, synonym_list in synonyms.items():
            if synonym_list_record := SolrSynonymList.find_by_synonym(synonym, synonym_type):
                synonym_list_record.synonym_list = synonym_list
                synonym_list_record.last_update_date = datetime.now(UTC)
                db.session.add(synonym_list_record)
            else:
                db.session.add(
                    SolrSynonymList(synonym=synonym, synonym_list=synonym_list, synonym_type=synonym_type)
                )
        db.session.commit()
