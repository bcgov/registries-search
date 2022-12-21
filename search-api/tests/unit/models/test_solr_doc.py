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
"""Tests to assure the SolrDoc Class."""
import pytest
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta

from search_api.models import SolrDoc
from search_api.services.solr.solr_docs import BusinessDoc

from tests.unit.services.test_solr import SOLR_TEST_DOCS


def test_solr_doc(session):
    """Assert that a solr doc can be stored in the service."""
    business_doc = deepcopy(SOLR_TEST_DOCS[0])

    solr_doc = SolrDoc(doc=asdict(business_doc), identifier=business_doc.identifier).save()

    assert solr_doc.id is not None
    # has default submission_date
    assert solr_doc.submission_date is not None


def test_find_most_recent_by_identifier(session):
    """Assert find_most_recent_by_identifier works as expected."""
    business_doc_1 = deepcopy(SOLR_TEST_DOCS[0])
    business_doc_2 = deepcopy(SOLR_TEST_DOCS[0])
    business_doc_2.name += '2'
    business_doc_3 = deepcopy(SOLR_TEST_DOCS[0])
    business_doc_3.name += '3'

    solr_doc_1 = SolrDoc(doc=asdict(business_doc_1), identifier=business_doc_1.identifier).save()
    solr_doc_2 = SolrDoc(doc=asdict(business_doc_2), identifier=business_doc_2.identifier).save()
    solr_doc_3 = SolrDoc(doc=asdict(business_doc_3), identifier=business_doc_3.identifier).save()

    # test method
    solr_doc = SolrDoc.find_most_recent_by_identifier(business_doc_1.identifier)
    assert solr_doc.id is not None
    assert solr_doc.id == solr_doc_3.id
    assert BusinessDoc(**solr_doc.doc).name == business_doc_3.name


def test_get_updated_identifiers_after_date(session):
    """Assert get_updated_identifiers_after_date works as expected."""
    business_doc_1 = deepcopy(SOLR_TEST_DOCS[0])
    business_doc_2 = deepcopy(SOLR_TEST_DOCS[0])
    business_doc_3 = deepcopy(SOLR_TEST_DOCS[1])
    business_doc_4 = deepcopy(SOLR_TEST_DOCS[2])

    for doc in [business_doc_1, business_doc_2, business_doc_3, business_doc_4]:
        SolrDoc(doc=asdict(doc), identifier=doc.identifier).save()

    identifiers = SolrDoc.get_updated_identifiers_after_date(datetime.utcnow() - timedelta(minutes=5))
    # should be 1 of each identifier (no dupes)
    assert len(identifiers) == 3
    assert business_doc_1.identifier in identifiers
    assert business_doc_3.identifier in identifiers
    assert business_doc_4.identifier in identifiers
