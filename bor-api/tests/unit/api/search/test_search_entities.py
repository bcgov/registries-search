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
"""Test-Suite to ensure that the search endpoints/functions work as expected."""
import time
from dataclasses import asdict
from http import HTTPStatus

import pytest
from flask import Flask

from bor_api.services import bor_solr
from bor_api.services.solr import Solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils import SearchParams, entities_search

from tests import integration_solr
from tests.unit.utils import create_solr_doc, SOLR_TEST_DOCS


@pytest.mark.skip('skipped until implementation finished')
@pytest.mark.parametrize('test_name,query,mock_names,mock_ids,mock_bns,expected', [
    ('test-entity-search',
     '123',
     [asdict(x) for x in SOLR_TEST_DOCS[:2]],
     [asdict(x) for x in SOLR_TEST_DOCS[2:4]],
     [asdict(x) for x in SOLR_TEST_DOCS[4:5]],
     [asdict(x) for x in SOLR_TEST_DOCS[:5]]),
])
def test_entities_search(app, session, client, requests_mock, test_name, query, mock_names, mock_ids, mock_bns, expected):
    """Assert that search business search call works as expected."""
    # setup solr mock
    num_found = len(expected)
    requests_mock.get(f"{app.config.get('SOLR_SVC_URL')}/search/query", json={'response': {'docs': mock_names + mock_ids + mock_bns, 'numFound': num_found, 'start': 0}})
    # call select
    params = SearchParams({Field.LEGAL_NAME.value: query}, None, None)
    results = business_search(params)
    # test
    assert results['response']['docs'] == expected
    assert results['response']['numFound'] == num_found
    assert results['response']['start'] == 0


@pytest.mark.skip('skipped until implementation finished')
@pytest.mark.parametrize('test_name,query_params,mock_names,mock_ids,mock_bns,expected_docs', [
    ('test_facets',
     {'query': '123', 'start': 0, 'rows': 5},
     [asdict(x) for x in SOLR_TEST_DOCS[:2]],
     [asdict(x) for x in SOLR_TEST_DOCS[2:4]],
     [asdict(x) for x in SOLR_TEST_DOCS[4:5]],
     [asdict(x) for x in SOLR_TEST_DOCS[:5]]),
    ('test_special_chars_only', {'query': '`~!@#$%^*()_-={}[]\\|', 'start': 0, 'rows': 10}, [], [], [], []),
    ('test_:_only', {'query': ':test', 'start': 0, 'rows': 10}, [], [], [], []),
    ('test_start_with_:', {'query': ':test', 'start': 0, 'rows': 10}, [], [], [], [])
])
def test_endpoint_entities(app, session, client, requests_mock, test_name, query_params, mock_names, mock_ids, mock_bns, expected_docs):
    """Assert that search entities endpoint works as expected."""
    # setup mock
    num_found = len(expected_docs)
    facets_mock = {'facet_counts': {'facet_fields': {SolrField.TYPE.value: ['BEN', 23, 'CP', 10, 'SP', 102], SolrField.STATE.value: ['ACTIVE', 23, 'HISTORICAL', 10]}}}
    requests_mock.get(f"{app.config.get('SOLR_SVC_URL')}/search/query", json={'response': {'docs': mock_names + mock_ids + mock_bns, 'numFound': num_found, 'start': 0}, **facets_mock})
    # call endpoint
    query = query_params['query']
    start = query_params['start']
    rows = query_params['rows']
    resp = client.get(f'/api/v1/businesses/search/facets?query=value:{query}&start={start}&rows={rows}')
    # check response
    assert resp.status_code == HTTPStatus.OK
    if expected_docs:
        assert resp.json['facets'] == Solr.parse_facets(facets_mock)
        assert resp.json['searchResults']['queryInfo']['rows'] == rows
        assert resp.json['searchResults']['queryInfo']['query']['value'] == query or query[0] == ':'
        assert resp.json['searchResults']['queryInfo']['start'] == start
        assert resp.json['searchResults']['totalResults'] == num_found
        assert resp.json['searchResults']['results'] == expected_docs


# uncomment and alter once solr config finished
# @integration_solr
# @pytest.mark.parametrize('test_name,doc_name,path,endpoint,match', [
#     ('test_bus_search_value', 'Test basic query', 'facets?query=value:basic', 'facets', True),
#     ('test_bus_search_name', 'Test names filter', 'facets?query=value:test::name:names', 'facets', True),
#     ('test_bus_search_name_no_match', 'Test name filter no match', 'facets?query=value:test::name:names', 'facets', False),
#     ('test_bus_search_name_&', 'Test name filter & match', 'facets?query=value:test::name:filter&', 'facets', True),
#     ('test_party_search_value', 'Test basic party query', 'parties?query=value:party&categories=partyRoles:partner,proprietor', 'parties', True),
#     ('test_party_search_owner_name', 'Test party owner name filter query', 'parties?query=value:party::partyName:person owner name filter&categories=partyRoles:partner,proprietor', 'parties', True),
#     ('test_party_search_parent_name', 'Test party parent name filter query', 'parties?query=value:party::parentName:name filter&categories=partyRoles:partner,proprietor', 'parties', True),
# ])
# def test_endpoint_full_integration(app, session, client, test_name, doc_name, path, endpoint, match):
#     """Assert that search endpoints work as expected."""
#     bor_solr.init_app(app)
#     bor_solr.delete_all_docs()
#     bor_solr.create_or_replace_docs([create_solr_doc('FM0000001', doc_name, 'ACTIVE', 'SP', '123', [(f'person {doc_name}', 'proprietor', 'person')])])
#     time.sleep(2)  # wait for solr to register update
#     resp = client.get(f'/api/v1/businesses/search/{path}')

#     assert resp.status_code == HTTPStatus.OK
#     assert resp.json['searchResults']['totalResults'] == (1 if match else 0)
#     validation_field = 'name' if endpoint == 'facets' else 'parentName'
#     if match:
#         assert resp.json['searchResults']['results'][0][validation_field] == doc_name
