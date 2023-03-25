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

    solr_doc = SolrDoc(doc=asdict(entity_doc), identifier=entity_doc.identifier).save()

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

    solr_doc_1 = SolrDoc(doc=asdict(entity_doc_1), identifier=entity_doc_1.identifier).save()
    solr_doc_2 = SolrDoc(doc=asdict(entity_doc_2), identifier=entity_doc_2.identifier).save()
    solr_doc_3 = SolrDoc(doc=asdict(entity_doc_3), identifier=entity_doc_3.identifier).save()

    # test method
    solr_doc = SolrDoc.find_most_recent_by_identifier(entity_doc_1.identifier)
    assert solr_doc.id is not None
    assert solr_doc.id == solr_doc_3.id
    assert Entity(**solr_doc.doc).legalName == entity_doc_3.legalName


def test_get_updated_identifiers_after_date(session):
    """Assert get_updated_identifiers_after_date works as expected."""
    entity_doc_1 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_2 = deepcopy(SOLR_TEST_DOCS[0])
    entity_doc_3 = deepcopy(SOLR_TEST_DOCS[1])
    entity_doc_4 = deepcopy(SOLR_TEST_DOCS[2])

    for doc in [entity_doc_1, entity_doc_2, entity_doc_3, entity_doc_4]:
        SolrDoc(doc=asdict(doc), identifier=doc.identifier).save()

    identifiers = SolrDoc.get_updated_identifiers_after_date(datetime.utcnow() - timedelta(minutes=5))
    # should be 1 of each identifier (no dupes)
    assert len(identifiers) == 3
    assert entity_doc_1.identifier in identifiers
    assert entity_doc_3.identifier in identifiers
    assert entity_doc_4.identifier in identifiers
