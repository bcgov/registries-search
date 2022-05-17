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

from search_api.resources.v1.businesses.search import _business_search, _business_suggest
from search_api.services.solr import Solr, SolrDoc, SolrField

from tests.unit.services.test_solr import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-identifier', 'CP00', ['CP0034567'],['<b>CP00</b>34567']),
])
def test_business_suggest_identifier(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [SolrDoc(x, 'test doc', 'ACTIVE', 'BEN').json() for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.NAME_SINGLE}:{query}",json={})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.IDENTIFIER_SELECT}:{query} " + \
        f'OR {SolrField.BN_SELECT}:{query}',json={'response': {'docs': mocked_docs}})
    # call select
    suggestions = _business_suggest(query, None)
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
    mocked_docs = [SolrDoc('BC1234567', 'test doc', 'ACTIVE', 'BEN', x).json() for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.NAME_SINGLE}:{query}",json={})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.IDENTIFIER_SELECT}:{query} " + \
        f'OR {SolrField.BN_SELECT}:{query}',json={'response': {'docs': mocked_docs}})
    # call select
    suggestions = _business_suggest(query, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-name', 'test 2222', ['TEST 2222', 'TESTERS 2222156'],['<b>TEST 2222</b>', 'TESTERS 2222156']),
])
def test_business_suggest_name(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [SolrDoc('BC1234567', x, 'ACTIVE', 'BEN').json() for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[{'term':mocked_terms[0]}]}}}})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.NAME_SINGLE}:{query.split()[0]}",json={'response': {'docs': [mocked_docs[1]]}})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.IDENTIFIER_SELECT}:{query} " + \
        f'OR {SolrField.BN_SELECT}:{query}',json={'response': {'docs': []}})
    # call select
    suggestions = _business_suggest(query, None)
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
    mocked_name_docs = [SolrDoc('BC0024562', x, 'ACTIVE', 'BEN').json() for x in mock_names]
    mocked_identifier_docs = [SolrDoc(x, 'test identifier match', 'ACTIVE', 'BEN').json() for x in mock_ids]
    mocked_bn_docs = [SolrDoc('BC0004567', 'test bn match', 'ACTIVE', 'BEN', x).json() for x in mock_bns]

    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[]}}}})
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.NAME_SINGLE}:{query}",json={'response': {'docs': mocked_name_docs}})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.IDENTIFIER_SELECT}:{query} " + \
        f'OR {SolrField.BN_SELECT}:{query}',json={'response': {'docs': mocked_identifier_docs + mocked_bn_docs}})
    # call select
    suggestions = _business_suggest(query, None)
    # test
    assert len(suggestions) == len(expected)
    for suggestion in suggestions:
        assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mock_names,mock_ids,mock_bns,expected', [
    ('test-bus-search', '123', SOLR_TEST_DOCS[:2],SOLR_TEST_DOCS[2:4],SOLR_TEST_DOCS[4:5],SOLR_TEST_DOCS[:5]),
])
def test_business_search(session, client, requests_mock, test_name, query, mock_names, mock_ids, mock_bns, expected):
    """Assert that search business search call works as expected."""
    # setup solr mock
    num_found = len(expected)
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select",json={'response': {'docs':mock_names+mock_ids+mock_bns,'numFound':num_found,'start':0}})
    # call select
    results = _business_search(query, None, None, None, None)
    # test
    assert results['response']['docs'] == expected
    assert results['response']['numFound'] == num_found
    assert results['response']['start'] == 0


@pytest.mark.parametrize('test_name,query,mock_name,expected', [
    ('test-single-result', '123', '123 test name', {'results':[{'type':SolrField.NAME,'value':'<b>123</b> TEST NAME'}]}),
])
def test_endpoint_suggest(session, client, requests_mock, test_name, query, mock_name, expected):
    """Assert that search suggest endpoint works as expected."""
    # setup mock - need to add more here if max_results > 1
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={'suggest':{'name':{query:{'suggestions':[{'term':mock_name}]}}}})
    # call endpoint
    resp = client.get(f'/api/v1/businesses/search/suggest?query={query}&max_results={1}')
    # check response
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == expected


@pytest.mark.parametrize('test_name,query_params,mock_names,mock_ids,mock_bns,expected_docs', [
    ('test-facets', {'query':'123','start':0,'rows':5}, SOLR_TEST_DOCS[:2],SOLR_TEST_DOCS[2:4],SOLR_TEST_DOCS[4:5],SOLR_TEST_DOCS[:5]),
])
def test_endpoint_facets(session, client, requests_mock, test_name, query_params, mock_names, mock_ids, mock_bns, expected_docs):
    """Assert that search suggest endpoint works as expected."""
    # setup mock
    num_found = len(expected_docs)
    facets_mock = {'facet_counts':{'facet_fields':{SolrField.TYPE:['BEN',23,'CP',10,'SP',102],SolrField.STATE:['ACTIVE',23,'HISTORICAL',10]}}}
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/select",json={'response':{'docs':mock_names+mock_ids+mock_bns,'numFound':num_found,'start':0},**facets_mock})
    # call endpoint
    query = query_params['query']
    start = query_params['start']
    rows = query_params['rows']
    resp = client.get(f'/api/v1/businesses/search/facets?query={query}&start_row={start}&num_of_rows={rows}')
    # check response
    assert resp.status_code == HTTPStatus.OK
    assert resp.json['facets'] == Solr.parse_facets(facets_mock)
    assert resp.json['searchResults']['queryInfo']['num_of_rows'] == rows
    assert resp.json['searchResults']['queryInfo']['query'] == query
    assert resp.json['searchResults']['queryInfo']['start_row'] == start
    assert resp.json['searchResults']['queryInfo']['total_rows'] == num_found
    assert resp.json['results'] == expected_docs
    