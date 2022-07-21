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
"""Test-Suite to ensure that the search endpoints/functions work as expected."""
from http import HTTPStatus

import pytest
from flask import current_app, Flask

from search_api.request_handlers import business_search, business_suggest, parties_search
from search_api.request_handlers.search import SearchParams
from search_api.services.solr import Solr, SolrField

from tests.unit.services.test_solr import create_solr_doc, SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-identifier', 'CP00', ['CP0034567'], ['<b>CP00</b>34567']),
])
def test_business_suggest_identifier(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [create_solr_doc(x, 'test doc', 'ACTIVE', 'BEN').json for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.NAME_SINGLE}%3A{query}",json={})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.IDENTIFIER_Q}%3A{query} " + \
        f'OR {SolrField.BN_Q}:{query}',json={'response': {'docs': mocked_docs}})
    # call select
    suggestions = business_suggest(query, True, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-bn', '0012334', ['BN00012334'], ['BN0<b>0012334</b>']),
])
def test_business_suggest_bn(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [create_solr_doc('BC1234567', 'test doc', 'ACTIVE', 'BEN', x).json for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.NAME_SINGLE}:{query}",json={})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.IDENTIFIER_Q}:{query} " + \
        f'OR {SolrField.BN_Q}:{query}',json={'response': {'docs': mocked_docs}})
    # call select
    suggestions = business_suggest(query, True, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-name', 'test 2222', ['TEST 2222', 'TESTERS 2222156'], ['<b>TEST 2222</b>', 'TESTERS 2222156']),
])
def test_business_suggest_name(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [create_solr_doc('BC1234567', x, 'ACTIVE', 'BEN').json for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[{'term':mocked_terms[0]}]}}}})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.NAME_SINGLE}:{query.split()[0]}",json={'response': {'docs': [mocked_docs[1]]}})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.IDENTIFIER_Q}:{query} " + \
        f'OR {SolrField.BN_Q}:{query}',json={'response': {'docs': []}})
    # call select
    suggestions = business_suggest(query, True, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mock_names,mock_ids,mock_bns,expected', [
    ('test-bn-identifier-name', '123', ['TEST 1234'],['CP1234567'],['BN00012334'],['TEST <b>123</b>4','CP<b>123</b>4567','BN000<b>123</b>34']),
])
def test_business_suggest_all(session, client, requests_mock, test_name, query, mock_names, mock_ids, mock_bns, expected):
    """Assert that search business suggest call works as expected."""
    # setup solr mock
    mocked_name_docs = [create_solr_doc('BC0024562', x, 'ACTIVE', 'BEN').json for x in mock_names]
    mocked_identifier_docs = [create_solr_doc(x, 'test identifier match', 'ACTIVE', 'BEN').json for x in mock_ids]
    mocked_bn_docs = [create_solr_doc('BC0004567', 'test bn match', 'ACTIVE', 'BEN', x).json for x in mock_bns]

    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[]}}}})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.NAME_SINGLE}:{query}",json={'response': {'docs': mocked_name_docs}})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/query?q={SolrField.IDENTIFIER_Q}:{query} " + \
        f'OR {SolrField.BN_Q}:{query}',json={'response': {'docs': mocked_identifier_docs + mocked_bn_docs}})
    # call select
    suggestions = business_suggest(query, True, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mock_names,mock_ids,mock_bns,expected', [
    ('test-bus-search',
     '123',
     [x.json for x in SOLR_TEST_DOCS[:2]],
     [x.json for x in SOLR_TEST_DOCS[2:4]],
     [x.json for x in SOLR_TEST_DOCS[4:5]],
     [x.json for x in SOLR_TEST_DOCS[:5]]),
])
def test_business_search(session, client, requests_mock, test_name, query, mock_names, mock_ids, mock_bns, expected):
    """Assert that search business search call works as expected."""
    # setup solr mock
    num_found = len(expected)
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response': {'docs':mock_names+mock_ids+mock_bns,'numFound':num_found,'start':0}})
    # call select
    params = SearchParams(query, None, None)
    results = business_search(params)
    # test
    assert results['response']['docs'] == expected
    assert results['response']['numFound'] == num_found
    assert results['response']['start'] == 0


@pytest.mark.parametrize('test_name,query,mock_docs', [
    ('test-party-search',
     '1',
     [x.json for x in SOLR_TEST_DOCS[8:10]]),
])
def test_parties_search(session, client, requests_mock, test_name, query, mock_docs):
    """Assert that search parties search call works as expected."""
    # setup solr mock
    parties_docs = []
    for doc in mock_docs:
        parties_docs += doc['parties']
    num_found = len(parties_docs)
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response': {'docs':parties_docs,'numFound':num_found,'start':0}})
    # call select
    params = SearchParams(query, None, None)
    results = parties_search(params)
    # test
    assert results['response']['docs'] == parties_docs
    assert results['response']['numFound'] == num_found
    assert results['response']['start'] == 0


@pytest.mark.parametrize('test_name,query,mocks,highlight,expected', [
    ('test-single-result', '123', ['123 test name'], False, [{'type':SolrField.NAME,'value':'123 TEST NAME'}]),
    ('test-single-result-highlight', '123', ['123 test name'], True, [{'type':SolrField.NAME,'value':'<b>123</b> TEST NAME'}]),
    ('test-two-results', '123', ['123 test name', 'BC0001234'], False, [{'type':SolrField.NAME,'value':'123 TEST NAME'}, {'type':SolrField.IDENTIFIER,'value':'BC0001234'}]),
    ('test-two-results-highlight', '123', ['123 test name', 'BC0001234'], True, [{'type':SolrField.NAME,'value':'<b>123</b> TEST NAME'}, {'type':SolrField.IDENTIFIER,'value':'BC000<b>123</b>4'}]),
    ('test-three-results', '123', ['123 test name', 'BC0001234', '123456789BC0001'], False, [{'type':SolrField.NAME,'value':'123 TEST NAME'}, {'type':SolrField.IDENTIFIER,'value':'BC0001234'}, {'type':SolrField.BN,'value':'123456789BC0001'}]),
    ('test-three-results-highlight', '123', ['123 test name', 'BC0001234', '123456789BC0001'], True, [{'type':SolrField.NAME,'value':'<b>123</b> TEST NAME'}, {'type':SolrField.IDENTIFIER,'value':'BC000<b>123</b>4'}, {'type':SolrField.BN,'value':'<b>123</b>456789BC0001'}]),
])
def test_endpoint_suggest(session, client, requests_mock, test_name, query, mocks, highlight, expected):
    """Assert that search suggest endpoint works as expected."""
    # setup mock - need to add more here if max_results > 1
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[{'term':mocks[0]}]}}}})
    if len(mocks) > 2:
        requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response':{'docs':[{SolrField.IDENTIFIER:mocks[1]},{SolrField.IDENTIFIER: '',SolrField.BN:mocks[2]}]}})
    elif len(mocks) > 1:
        requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response':{'docs':[{SolrField.IDENTIFIER:mocks[1]}]}})
    # call endpoint
    url = f'/api/v1/businesses/search/suggest?query={query}&rows={len(mocks)}'
    if highlight:
        url += f'&highlight={highlight}'
    resp = client.get(url)
    # check response
    assert resp.status_code == HTTPStatus.OK
    assert resp.json['results'] == expected


@pytest.mark.parametrize('test_name,query_params,mock_names,mock_ids,mock_bns,expected_docs', [
    ('test-facets',
     {'query':'123','start':0,'rows':5},
     [x.json for x in SOLR_TEST_DOCS[:2]],
     [x.json for x in SOLR_TEST_DOCS[2:4]],
     [x.json for x in SOLR_TEST_DOCS[4:5]],
     [x.json for x in SOLR_TEST_DOCS[:5]]),
])
def test_endpoint_facets(session, client, requests_mock, test_name, query_params, mock_names, mock_ids, mock_bns, expected_docs):
    """Assert that search facets endpoint works as expected."""
    # setup mock
    num_found = len(expected_docs)
    facets_mock = {'facet_counts':{'facet_fields':{SolrField.TYPE:['BEN',23,'CP',10,'SP',102],SolrField.STATE:['ACTIVE',23,'HISTORICAL',10]}}}
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response':{'docs':mock_names+mock_ids+mock_bns,'numFound':num_found,'start':0},**facets_mock})
    # call endpoint
    query = query_params['query']
    start = query_params['start']
    rows = query_params['rows']
    resp = client.get(f'/api/v1/businesses/search/facets?query={query}&start={start}&rows={rows}')
    # check response
    assert resp.status_code == HTTPStatus.OK
    assert resp.json['facets'] == Solr.parse_facets(facets_mock)
    assert resp.json['searchResults']['queryInfo']['rows'] == rows
    assert resp.json['searchResults']['queryInfo']['query'] == query
    assert resp.json['searchResults']['queryInfo']['start'] == start
    assert resp.json['searchResults']['totalResults'] == num_found
    assert resp.json['searchResults']['results'] == expected_docs


@pytest.mark.parametrize('test_name,query_params,mock_docs', [
    ('test-parties',
     {'query':'1','start':0,'rows':5},
     [x.json for x in SOLR_TEST_DOCS[8:10]]),
])
def test_endpoint_parties(session, client, requests_mock, test_name, query_params, mock_docs):
    """Assert that search parties endpoint works as expected."""
    # setup mock
    parties_docs = []
    for doc in mock_docs:
        parties_docs += doc['parties']
    num_found = len(parties_docs)
    facets_mock = {'facet_counts':{'facet_fields':{SolrField.TYPE:['SP',2,'GP',10],SolrField.STATE:['ACTIVE',7,'HISTORICAL',5],SolrField.PARTY_ROLE:['proprietor',2,'partner',13]}}}
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/query",json={'response':{'docs':parties_docs,'numFound':num_found,'start':0},**facets_mock})
    # call endpoint
    query = query_params['query']
    start = query_params['start']
    rows = query_params['rows']
    resp = client.get(f'/api/v1/businesses/search/parties?query={query}&start={start}&rows={rows}&categories=partyRoles:partner,proprietor')
    # check response
    assert resp.status_code == HTTPStatus.OK
    assert resp.json['facets'] == Solr.parse_facets(facets_mock)
    assert resp.json['searchResults']['queryInfo']['rows'] == rows
    assert resp.json['searchResults']['queryInfo']['query'] == query
    assert resp.json['searchResults']['queryInfo']['start'] == start
    assert resp.json['searchResults']['queryInfo']['categories']['partyRoles'] == ['partner', 'proprietor']
    assert resp.json['searchResults']['totalResults'] == num_found
    assert resp.json['searchResults']['results'] == parties_docs
    