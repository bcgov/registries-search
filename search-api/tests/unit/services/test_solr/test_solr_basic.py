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
from search_api.services.solr import Solr, SolrDoc, SolrField

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
def test_solr_create_delete(app, test_name, identifier, state, name, legal_type, bn):
    """Assert that solr docs can be updates/searched/deleted."""
    solr.init_app(app)
    solr.delete_all_docs()
    # add new doc
    new_doc = SolrDoc(identifier=identifier, name=name, state=state, legal_type=legal_type, tax_id=bn)
    added = solr.create_or_replace_docs([new_doc.json()])
    assert added.status_code == HTTPStatus.OK
    time.sleep(2) # takes up to 1 second for solr to register update
    # search new doc
    resp = solr.query(f'q={SolrField.IDENTIFIER_Q}:{identifier}', 0, 10)
    docs = resp['response']['docs']
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
    resp = solr.query(f'q={SolrField.IDENTIFIER_Q}:{identifier}', 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 0


@pytest.mark.parametrize('test_name,params,expected', [
    ('test-basic-basic', {'query': 'name', 'fields': [SolrField.NAME_Q], 'wild': []}, f'q={SolrField.NAME_Q}:name'),
    ('test-basic-basic-wild', {'query': 'name', 'fields': [SolrField.NAME_Q], 'wild': [SolrField.NAME_Q]}, f'q={SolrField.NAME_Q}:name*'),
    ('test-basic-multi', {'query': 'name', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': []}, f'q={SolrField.NAME_Q}:name OR {SolrField.NAME_STEM_AGRO}:name'),
    ('test-basic-multi-wild-1', {'query': 'name', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_Q]}, f'q={SolrField.NAME_Q}:name* OR {SolrField.NAME_STEM_AGRO}:name'),
    ('test-basic-multi-wild-2', {'query': 'name', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_STEM_AGRO]}, f'q={SolrField.NAME_Q}:name OR {SolrField.NAME_STEM_AGRO}:name*'),
    ('test-basic-multi-wild-3', {'query': 'name', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO]}, f'q={SolrField.NAME_Q}:name* OR {SolrField.NAME_STEM_AGRO}:name*'),
    ('test-multi-basic', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q], 'wild': []}, f'q={SolrField.NAME_Q}:name1&fq={SolrField.NAME_Q}:name2&fq={SolrField.NAME_Q}:name3'),
    ('test-multi-basic-wild', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q], 'wild': [SolrField.NAME_Q]}, f'q={SolrField.NAME_Q}:name1*&fq={SolrField.NAME_Q}:name2*&fq={SolrField.NAME_Q}:name3*'),
    ('test-multi-multi', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': []}, f'q={SolrField.NAME_Q}:name1 OR {SolrField.NAME_STEM_AGRO}:name1&fq={SolrField.NAME_Q}:name2 OR {SolrField.NAME_STEM_AGRO}:name2&fq={SolrField.NAME_Q}:name3 OR {SolrField.NAME_STEM_AGRO}:name3'),
    ('test-multi-multi-wild-1', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_Q]}, f'q={SolrField.NAME_Q}:name1* OR {SolrField.NAME_STEM_AGRO}:name1&fq={SolrField.NAME_Q}:name2* OR {SolrField.NAME_STEM_AGRO}:name2&fq={SolrField.NAME_Q}:name3* OR {SolrField.NAME_STEM_AGRO}:name3'),
    ('test-multi-multi-wild-2', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_STEM_AGRO]}, f'q={SolrField.NAME_Q}:name1 OR {SolrField.NAME_STEM_AGRO}:name1*&fq={SolrField.NAME_Q}:name2 OR {SolrField.NAME_STEM_AGRO}:name2*&fq={SolrField.NAME_Q}:name3 OR {SolrField.NAME_STEM_AGRO}:name3*'),
    ('test-multi-multi-wild-3', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO], 'wild': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO]}, f'q={SolrField.NAME_Q}:name1* OR {SolrField.NAME_STEM_AGRO}:name1*&fq={SolrField.NAME_Q}:name2* OR {SolrField.NAME_STEM_AGRO}:name2*&fq={SolrField.NAME_Q}:name3* OR {SolrField.NAME_STEM_AGRO}:name3*'),
    ('test-complex-1', {'query': 'name1 name2 name3', 'fields': [SolrField.NAME_Q, SolrField.NAME_STEM_AGRO, SolrField.IDENTIFIER_Q, SolrField.BN_Q], 'wild': [SolrField.IDENTIFIER_Q, SolrField.BN_Q]}, f'q={SolrField.NAME_Q}:name1 OR {SolrField.NAME_STEM_AGRO}:name1 OR {SolrField.IDENTIFIER_Q}:name1* OR {SolrField.BN_Q}:name1*&fq={SolrField.NAME_Q}:name2 OR {SolrField.NAME_STEM_AGRO}:name2 OR {SolrField.IDENTIFIER_Q}:name2* OR {SolrField.BN_Q}:name2*&fq={SolrField.NAME_Q}:name3 OR {SolrField.NAME_STEM_AGRO}:name3 OR {SolrField.IDENTIFIER_Q}:name3* OR {SolrField.BN_Q}:name3*'),
])
def test_build_split_query(test_name, params, expected):
    """Assert that the build_split_query function works as expected."""
    split_query = Solr.build_split_query(params['query'], params['fields'], params['wild'])
    assert split_query == expected


@pytest.mark.parametrize('test_name,query,names,expected', [
    ('test-1', '1234567', ['1234567 B.C. LTD.'], ['<b>1234567</b> B.C. LTD.']),
    ('test-2', 'my query', ['MY QUERY 1', 'THIS IS MY QUERY'], ['<b>MY QUERY</b> 1', 'THIS IS <b>MY QUERY</b>']),
])
def test_highlight_names(test_name, query, names, expected):
    """Assert the highlight names function works as expected."""
    highlighted_names = Solr.highlight_names(query.upper(), names)
    assert highlighted_names == expected


@pytest.mark.parametrize('test_name,facet_data,expected', [
    ('test-1',
     {'facet_counts':{'facet_fields': {SolrField.TYPE:['BEN',23,'CP',10,'SP',102],SolrField.STATE:['ACTIVE',23,'HISTORICAL',10]}}},
     {'fields':{SolrField.TYPE:[{'value':'BEN','count':23},{'value':'CP','count':10},{'value':'SP','count':102}],SolrField.STATE:[{'value':'ACTIVE','count':23},{'value':'HISTORICAL','count':10}]}}),
])
def test_parse_facets(test_name, facet_data, expected):
    """Assert the parse facets function works as expected."""
    facet_info = Solr.parse_facets(facet_data)
    assert facet_info == expected
