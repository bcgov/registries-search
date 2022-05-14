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
import time
from http import HTTPStatus

import pytest
from flask import current_app, Flask

from search_api.resources.v1.businesses.search import _business_search, _business_suggest
from search_api.services.solr import SolrDoc, SolrField

from tests import integration_solr


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-identifier', 'CP00', ['CP0034567'],['<b>CP00</b>34567']),
])
def test_business_suggest_identifier(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # setup solr mock
    mocked_docs = [SolrDoc(x, 'test doc', 'ACTIVE', 'BEN').json() for x in mocked_terms]
    requests_mock.get(f"{current_app.config.get('SOLR_SVC_URL')}/search/suggest",json={})
    requests_mock.get(
        f"{current_app.config.get('SOLR_SVC_URL')}/search/select?q={SolrField.NAME_SINGLE}:{query}",json={})
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
    ('test-identifier', 'CP00', ['CP0034567'],['<b>CP00</b>34567']),
    # ('test-bn', '0012334', ['BN0<b>0012334</b>']),
])
def test_business_suggest_bn(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # TODO: finish test
    # setup solr mock
    # requests_mock.get('/search/suggest',json={'suggest': {'name': {query: {'suggestions': mocked_terms}}}})
    # # call select
    # suggestions = _business_suggest(query, None)
    # # test
    # assert len(suggestions) == len(expected)
    # for suggestion in suggestions:
    #     assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-identifier', 'CP00', ['CP0034567'],['<b>CP00</b>34567']),
    # ('test-name-exact', 'tests 2222', ['<b>TESTS 2222</b>']),
    # ('test-partial-1', 'tester', ['<b>TESTER</b> 1111']),
    # ('test-partial-2', 'tester 11', ['<b>TESTER 11</b>11']),
    # ('test-partial-3', 'ots of ords', ['LOTS OF WORDS IN HERE']),
])
def test_business_suggest_name(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # TODO: finish test
    # setup solr mock
    # requests_mock.get('http://localhost:8983/solr/search/suggest',json={'suggest': {'name': {query: {'suggestions': mocked_terms}}}})
    # # call select
    # suggestions = _business_suggest(query, None)
    # # test
    # assert len(suggestions) == len(expected)
    # for suggestion in suggestions:
    #     assert suggestion['value'] in expected


@pytest.mark.parametrize('test_name,query,mocked_terms,expected', [
    ('test-identifier', 'CP00', ['CP0034567'],['<b>CP00</b>34567']),
    # ('test-bn-identifier-name', '123', [
    #     'TEST <b>123</b>4',
    #     'CP<b>123</b>4567',
    #     'BN000<b>123</b>34']),
])
def test_business_suggest_all(session, client, requests_mock, test_name, query, mocked_terms, expected):
    """Assert that solr business suggest call works as expected."""
    # TODO: finish test
    # setup solr mock
    # requests_mock.get('http://localhost:8983/solr/search/suggest',json={'suggest': {'name': {query: {'suggestions': mocked_terms}}}})
    # # call select
    # suggestions = _business_suggest(query, None)
    # # test
    # assert len(suggestions) == len(expected)
    # for suggestion in suggestions:
    #     assert suggestion['value'] in expected

# TODO: test_business_search, test_suggest_endpoint, test_facets_endpoint
