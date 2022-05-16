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
"""Test-Suite to ensure that the Solr Service is working as expected for updates/deletes/searches."""
import time
from http import HTTPStatus

import pytest
from flask import Flask

from search_api.services import solr
from search_api.services.solr import SolrDoc, SolrField

from tests import integration_solr


@pytest.mark.parametrize('test_name,identifier,state,name,legal_type,bn', [
    ('test-1', 'CP1', 'ACTIVE', 'BASIC TEST 1', 'CP', '12345'),
])
def test_solr_doc(test_name, identifier, state, name, legal_type, bn):
    """Assert that solr doc class works as expected."""
    new_doc = SolrDoc(identifier=identifier, name=name, state=state, legal_type=legal_type, tax_id=bn)
    assert new_doc
    json = new_doc.json()
    assert json
    assert json.get(SolrField.IDENTIFIER) == identifier
    assert json.get(SolrField.STATE) == state
    assert json.get(SolrField.NAME) == name
    assert json.get(SolrField.TYPE) == legal_type
    assert json.get(SolrField.BN) == bn


@integration_solr
@pytest.mark.parametrize('test_name,identifier,state,name,legal_type,bn', [
    ('test-1', 'CP1234577', 'ACTIVE', 'BASIC TEST 1', 'CP', '12345'),
])
def test_solr_create_delete(test_name, identifier, state, name, legal_type, bn):
    """Assert that solr docs can be updates/searched/deleted."""
    solr.delete_all_docs()
    # add new doc
    new_doc = SolrDoc(identifier=identifier, name=name, state=state, legal_type=legal_type, tax_id=bn)
    added = solr.create_or_replace_docs([new_doc.json()])
    assert added.status_code == HTTPStatus.OK
    time.sleep(1) # takes up to 1 second for solr to register update
    # search new doc
    docs = solr.select(f'q={SolrField.IDENTIFIER_SELECT}:{identifier}', 1)
    assert docs[0][SolrField.IDENTIFIER] == identifier
    assert docs[0][SolrField.BN] == bn
    assert docs[0][SolrField.NAME] == name
    assert docs[0][SolrField.STATE] == state
    assert docs[0][SolrField.TYPE] == legal_type
    # delete doc
    deleted = solr.delete_docs([identifier])
    assert deleted.status_code == HTTPStatus.OK
    time.sleep(1) # takes up to 1 second for solr to register update
    # test search returns nothing
    docs = solr.select(f'q={SolrField.IDENTIFIER_SELECT}:{identifier}', 1)
    assert len(docs) == 0

# TODO: test build_split_query, highlight_names, parse_facets
