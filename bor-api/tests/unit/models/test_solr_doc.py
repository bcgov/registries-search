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
"""Tests to assure the SolrDoc Class."""
import pytest
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta

from bor_api.models import SolrDoc
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.solr_docs import Entity

from tests.unit.utils import SOLR_TEST_DOCS


def test_solr_doc(session):
    """Assert that a solr doc can be stored in the service."""
    entity_doc = deepcopy(SOLR_TEST_DOCS[0])

    solr_doc = SolrDoc(doc=asdict(entity_doc), entity_id=entity_doc.id).save()

    assert solr_doc.id is not None
    # has default submission_date
    assert solr_doc.submission_date is not None


def test_find_most_recent_by_identifier(session):
    """Assert find_most_recent_by_identifier works as expected."""
    entity_doc_1 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_2 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_2.legalName += '2'
    entity_doc_3 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_3.legalName += '3'

    SolrDoc(doc=asdict(entity_doc_1), entity_id=entity_doc_1.id).save()
    SolrDoc(doc=asdict(entity_doc_2), entity_id=entity_doc_2.id).save()
    solr_doc_3 = SolrDoc(doc=asdict(entity_doc_3), entity_id=entity_doc_3.id).save()

    # test method
    solr_doc = SolrDoc.find_most_recent_by_entity_id(entity_doc_1.id)
    assert solr_doc.id is not None
    assert solr_doc.id == solr_doc_3.id
    assert Entity(**solr_doc.doc).legalName == entity_doc_3.legalName


def test_get_updated_entity_ids_after_date(session):
    """Assert get_updated_entity_ids_after_date works as expected."""
    entity_doc_1 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_2 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_3 = deepcopy(SOLR_TEST_DOCS[1])
    entity_doc_4 = deepcopy(SOLR_TEST_DOCS[2])

    for doc in [entity_doc_1, entity_doc_2, entity_doc_3, entity_doc_4]:
        SolrDoc(doc=asdict(doc), entity_id=doc.id).save()

    entity_ids = SolrDoc.get_updated_entity_ids_after_date(datetime.utcnow() - timedelta(minutes=5))
    # should be 1 of each identifier (no dupes)
    assert len(entity_ids) == 3
    assert entity_doc_1.id in entity_ids
    assert entity_doc_3.id in entity_ids
    assert entity_doc_4.id in entity_ids
