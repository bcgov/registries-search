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
"""Test-Suite to ensure that the Solr Service is working as expected for all queries."""
import time
from http import HTTPStatus

import pytest
from flask import Flask

from search_api.services import solr
from search_api.services.solr import Solr, SolrDoc, SolrField

from tests import integration_solr
from . import SOLR_TEST_DOCS


@integration_solr
@pytest.mark.parametrize('test_name,query,expected', [
    # ('test-doesnt-match-identifier', 'CP00', []),
    # ('test-doesnt-match-bn', 'BN00012334', []),
    # ('test-name-exact', 'tests 2222', ['tests 2222']),
    # ('test-case', 'not case sensitive', ['NOt Case SENSitive']),
    # ('test-partial-1', 'tester', ['tester 1111']),
    # ('test-partial-2', 'tester 11', ['tester 1111']),
    # ('test-partial-3', 'lots of wor', ['lots of words in here']),
    # ('test-all-words-match', 'tests oops 2222', []),
    # ('test-stem-matches', 'test 2222', ['tests 2222']),
    ('test-multiple-matches', 'test', ['test 1234', 'tester 1111', 'tests 2222', 'test 3333', '4444 test']),
])
def test_solr_suggest_name(app, test_name, query, expected):
    """Assert that solr suggest call works as expected."""
    # setup
    solr.init_app(app)
    solr.delete_all_docs()
    solr.create_or_replace_docs(SOLR_TEST_DOCS)
    time.sleep(1) # wait for solr to register update
    # call suggester
    suggestions = solr.suggest(query, 10, True)
    assert len(suggestions) == len(expected)
    for name in expected:
        assert name.upper() in suggestions


@integration_solr
@pytest.mark.parametrize('test_name,query,query_field,base_fields,expected_field,expected', [
    ('test-identifier', 'CP00', SolrField.IDENTIFIER_Q, True, SolrField.IDENTIFIER, ['CP0034567']),
    ('test-bn', '0012334', SolrField.BN_Q, True, SolrField.BN, ['BN00012334']),
    ('test-name-exact', 'tests 2222', SolrField.NAME_SINGLE, True, SolrField.NAME, ['tests 2222']),
    ('test-case', 'not case sensitive', SolrField.NAME_SINGLE, True, SolrField.NAME, ['NOt Case SENSitive']),
    ('test-partial-1', 'tester', SolrField.NAME_SINGLE, True, SolrField.NAME, ['tester 1111']),
    ('test-partial-2', 'tester 11', SolrField.NAME_SINGLE, True, SolrField.NAME, ['tester 1111']),
    ('test-partial-3', 'lots of wor', SolrField.NAME_SINGLE, True, SolrField.NAME, ['lots of words in here']),
    ('test-partial-4', 'ots of ords', SolrField.NAME_SINGLE, True, SolrField.NAME, ['lots of words in here']),
    ('test-all-words-match', 'tests oops 2222', SolrField.NAME_SINGLE, True, SolrField.NAME, []),
    ('test-multiple-matches', 'test 1', SolrField.NAME_SINGLE, True, SolrField.NAME, ['test 1234', 'tester 1111']),
    ('test-parties-1', 'org', SolrField.PARTY_NAME_SINGLE, False, SolrField.PARTY_NAME, ['org 1', 'test org partner']),
    ('test-parties-2', 'person', SolrField.PARTY_NAME_SINGLE, False, SolrField.PARTY_NAME, ['person 1','test person partner']),
    ('test-parties-3', 'test Person', SolrField.PARTY_NAME_SINGLE, False, SolrField.PARTY_NAME, ['test person partner']),
    ('test-parties-4', 'test partner', SolrField.PARTY_NAME_SINGLE, False, SolrField.PARTY_NAME, ['test org partner','test person partner']),
    ('test-special-chars-name-&&', '01 special && char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['01 solr special && char']),
    ('test-special-chars-name-||', '02 special || char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['02 solr special || char']),
    ('test-special-chars-name-:', '03 special: char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['03 solr special: char']),
    ('test-special-chars-name-+', '04 special + char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['04 solr special + char']),
    ('test-special-chars-name--', '05 special - char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['05 solr special - char']),
    ('test-special-chars-name-!', '06 special ! char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['06 solr special ! char']),
    ('test-special-chars-name-\\', '07 special \ char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['07 solr special \ char']),
    ('test-special-chars-name-()', '08 special (char)', SolrField.NAME_SINGLE, True, SolrField.NAME, ['08 solr special (char)']),
    ('test-special-chars-name-"', '09 special " char"', SolrField.NAME_SINGLE, True, SolrField.NAME, ['09 solr special " char"']),
    ('test-special-chars-name-~', '10 special ~ char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['10 solr special ~ char']),
    ('test-special-chars-name-*', '11 special* char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['11 solr special* char']),
    ('test-special-chars-name-?', '12 special? char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['12 solr special? char']),
    ('test-special-chars-name-/', '13 special / char', SolrField.NAME_SINGLE, True, SolrField.NAME, ['13 solr special / char']),
    ('test-special-chars-name-X', 'special =&{}^%`#|<>,.@$;_chars', SolrField.NAME_SINGLE, True, SolrField.NAME, ['special =&{}^%`#|<>,.@$;_chars']),
])
def test_solr_query(app, test_name, query, query_field, base_fields, expected_field, expected):
    """Assert that solr query call works as expected."""
    # setup
    solr.init_app(app)
    solr.delete_all_docs()
    solr.create_or_replace_docs(SOLR_TEST_DOCS)
    time.sleep(1) # wait for solr to register update
    query = Solr.prep_query_str(query)
    search_params = Solr.build_split_query(query, [query_field], [SolrField.NAME_SINGLE])
    search_params['fl'] = solr.base_fields if base_fields else solr.party_fields
    # call select
    resp = solr.query(search_params, 0, 10)
    docs = resp['response']['docs']
    # test
    assert len(docs) == len(expected)
    for doc in docs:
        assert doc[expected_field] in expected
