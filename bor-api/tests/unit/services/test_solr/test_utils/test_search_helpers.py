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
"""Tests to ensure that the Solr Service search helpers work as expected."""
from dataclasses import asdict

import pytest
from unittest import mock

from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils import SearchParams, entities_search
from bor_api.services.solr.utils.query_builders import PRE_CHILD_FILTER_CLAUSE
from bor_api.services.solr.utils.search_helpers import _add_category_filters

from tests.unit.utils import SOLR_TEST_DOCS


BASIC_PAYLOAD = expected_payload = {
    'query': '(legalName_q:name^2 OR legalName_q:name~2 OR legalName_agro_q:name^2 OR legalName_agro_q:name~2 OR legalName_single_term:name^2 OR legalName_single_term:name~2 OR identifier_q:name OR bn_q:name^2 OR bn_q:name~1 OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:name~1)) OR (legalName_q:"name"~5^5) OR (legalName_agro_q:"name"~10^3) OR (legalName_agro_q:"name"^2)',
    'filter': [],
    'queries': {'parents': 'entityType:*', 'parentFilters': ''},
    'facet': {'entityType': {'type': 'terms', 'field': 'entityType'},
                'legalType': {'type': 'terms', 'field': 'legalType'},
                'state': {'type': 'terms', 'field': 'state'},
                'relatedEntityType': {'type': 'terms', 'field': 'relatedEntityType',
                                    'domain': {'blockChildren': '{!v=$parents}'},
                                    'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}},
                'relatedLegalType': {'type': 'terms',
                                    'field': 'relatedLegalType',
                                    'domain': {'blockChildren': '{!v=$parents}'},
                                    'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}},
                'relatedState': {'type': 'terms',
                                'field': 'relatedState',
                                'domain': {'blockChildren': '{!v=$parents}'},
                                'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}},
                'roleType': {'type': 'terms',
                            'field': 'roleType',
                            'domain': {'blockChildren': '{!v=$parents}'},
                            'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}},
    'fields': ['bn', 'bnSP', 'entityAddresses', 'entityType', 'identifier_q', 'legalName', 'legalType', 'operatingName', 'roles', 'state', 'score', '[child]', 'addressCity', 'addressCountry', 'addressRegion', 'addressType', 'postalCode', 'streetAddress', 'active', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleDates', 'roleType', 'start', 'end']}

COMPLEX_PAYLOAD = {
    'query': '(legalName_q:name1^2 OR legalName_q:name1~2 OR legalName_agro_q:name1^2 OR legalName_agro_q:name1~2 OR legalName_single_term:name1^2 OR legalName_single_term:name1~2 OR (identifier_q:"1" AND legalType:"NAME") OR bn_q:name1^2 OR bn_q:name1~1 OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:name1~1)) AND (legalName_q:name2^2 OR legalName_q:name2~2 OR legalName_agro_q:name2^2 OR legalName_agro_q:name2~2 OR legalName_single_term:name2^2 OR legalName_single_term:name2~2 OR (identifier_q:"2" AND legalType:"NAME") OR bn_q:name2^2 OR bn_q:name2~1 OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:name2~1)) AND (legalName_q:name3^2 OR legalName_q:name3~2 OR legalName_agro_q:name3^2 OR legalName_agro_q:name3~2 OR legalName_single_term:name3^2 OR legalName_single_term:name3~2 OR (identifier_q:"3" AND legalType:"NAME") OR bn_q:name3^2 OR bn_q:name3~1 OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:name3~1)) OR (legalName_q:"name1 name2 name3"~5^5) OR (legalName_agro_q:"name1 name2 name3"~10^3) OR (legalName_agro_q:"name1"^2)',
    'filter': ['(identifier_q:"12345" AND legalType:"BC")', 'legalName_single_term:Test', 'state:("ACTIVE" OR "HISTORICAL")', 'entityType:("PERSON" OR "BUSINESS")', '({!parent which = \'-_nest_path_:* entityType:*\'}address_q:vancouver AND {!parent which = \'-_nest_path_:* entityType:*\'}address_q:bc AND {!parent which = \'-_nest_path_:* entityType:*\'}relatedBN_q:123 AND ({!parent which = \'-_nest_path_:* entityType:*\'}related_q:"0012345" AND {!parent which = \'-_nest_path_:* entityType:*\'}relatedLegalType:"S") AND {!parent which = \'-_nest_path_:* entityType:*\'}related_q:name)', '{!parent which = \'-_nest_path_:* entityType:*\'}addressCity:"NORTH VANCOUVER" OR addressCity: "VICTORIA"', '{!parent which = \'-_nest_path_:* entityType:*\'}relatedState:"ACTIVE"', "{!parent which = '-_nest_path_:* entityType:*'}start:[2022-03-21 TO *] OR end:[2022-03-21 TO *] OR active: true"],
    'queries': {'parents': 'entityType:*', 'parentFilters': '(identifier_q:"12345" AND legalType:"BC") AND legalName_single_term:Test'},
    'facet': {'entityType': {'type': 'terms', 'field': 'entityType'}, 'legalType': {'type': 'terms', 'field': 'legalType'}, 'state': {'type': 'terms', 'field': 'state'}, 'relatedEntityType': {'type': 'terms', 'field': 'relatedEntityType', 'domain': {'blockChildren': '{!v=$parents}'}, 'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}, 'relatedLegalType': {'type': 'terms', 'field': 'relatedLegalType', 'domain': {'blockChildren': '{!v=$parents}'}, 'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}, 'relatedState': {'type': 'terms', 'field': 'relatedState', 'domain': {'blockChildren': '{!v=$parents}'}, 'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}, 'roleType': {'type': 'terms', 'field': 'roleType', 'domain': {'blockChildren': '{!v=$parents}'}, 'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}},
    'fields': ['bn', 'bnSP', 'entityAddresses', 'entityType', 'identifier_q', 'legalName', 'legalType', 'operatingName', 'roles', 'state', 'score', '[child]', 'addressCity', 'addressCountry', 'addressRegion', 'addressType', 'postalCode', 'streetAddress', 'active', 'relatedBN', 'relatedEntityType', 'relatedIdentifier', 'relatedName', 'relatedState', 'roleDates', 'roleType', 'start', 'end']}


def test_add_category_filters():
    """Assert that the _add_category_filters function works as expected."""
    solr_payload = {'query': 'field:search', 'filter': []}
    # add parent category
    _add_category_filters(solr_payload=solr_payload, categories={Field.LEGAL_TYPE: ['bc','SP']}, is_nested=False)

    assert solr_payload['filter'] == [f'{Field.LEGAL_TYPE.value}:("BC" OR "SP")']

    # add child category
    _add_category_filters(solr_payload=solr_payload, categories={Field.RELATED_LEGAL_TYPE: ['bc','SP']}, is_nested=True)

    assert solr_payload['filter'] == [f'{Field.LEGAL_TYPE.value}:("BC" OR "SP")',
                                      f'{PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_LEGAL_TYPE.value}:"BC" OR {Field.RELATED_LEGAL_TYPE.value}: "SP"']


@pytest.mark.parametrize('test_name,query,categories,child_query,child_categories,child_date_ranges', [
    ('test_basic', {'value': 'name'}, {}, {}, {}, {}),
    ('test_complex',
     {'value': 'name1 name2 name3', Field.IDENTIFIER_Q.value: 'BC12345', Field.LEGAL_NAME_SINGLE_Q.value: 'Test'},
     {Field.STATE: ['ACTIVE', 'HISTORICAL'], Field.ENTITY_TYPE: ['PERSON','BUSINESS']},
     {Field.ADDRESS_Q.value: 'vancouver bc', Field.RELATED_BN_Q: '123'},
     {Field.ADDRESS_CITY: ['North Vancouver', 'Victoria'], Field.RELATED_STATE: ['ACTIVE']},
     {Field.START: '2022-03-21', Field.END: '*'}),
])
def test_entities_search(app, requests_mock, test_name, query, categories,
                         child_query, child_categories, child_date_ranges):
    """Assert that the entity_search function parses params and calls solr."""
    # setup solr mock
    docs = [asdict(x) for x in SOLR_TEST_DOCS[:5]]
    num_found = 5
    start = 0
    requests_mock.post(f"{app.config.get('SOLR_SVC_URL')}/bor/query", json={'response': {'docs': docs, 'numFound': num_found, 'start': start}})
    # call select
    params = SearchParams(query=query,
                          rows=10,
                          start=0,
                          categories=categories,
                          child_query=child_query,
                          child_categories=child_categories,
                          child_date_ranges=child_date_ranges)
    results = entities_search(params)
    # test it returned the mock successfully
    assert results['response']['docs'] == docs
    assert results['response']['numFound'] == num_found
    assert results['response']['start'] == start


@pytest.mark.parametrize('test_name,query,categories,child_query,child_categories,child_date_ranges,expected', [
    ('test_basic', {'value': 'name'}, {}, {}, {}, {}, BASIC_PAYLOAD),
    ('test_complex',
     {'value': 'name1 name2 name3', Field.IDENTIFIER_Q.value: 'BC12345', Field.LEGAL_NAME_SINGLE_Q.value: 'Test'},
     {Field.STATE: ['ACTIVE', 'HISTORICAL'], Field.ENTITY_TYPE: ['PERSON','BUSINESS']},
     {Field.ADDRESS_Q.value: 'vancouver bc', Field.RELATED_BN_Q.value: '123', Field.RELATED_Q.value: 'S0012345 name'},
     {Field.ADDRESS_CITY: ['North Vancouver', 'Victoria'], Field.RELATED_STATE: ['ACTIVE']},
     {Field.START: '2022-03-21', Field.END: '*'},
     COMPLEX_PAYLOAD),
])
@mock.patch('bor_api.services.solr.Solr.query')
def test_entities_search_deep(mocked, test_name, query, categories,
                         child_query, child_categories, child_date_ranges, expected):
    """Assert that the entity_search function parses params correctly."""
    def mock_solr(*args, **kwargs):
        return []
    mocked.side_effect = mock_solr
    # call select
    params = SearchParams(query=query,
                          rows=10,
                          start=0,
                          categories=categories,
                          child_query=child_query,
                          child_categories=child_categories,
                          child_date_ranges=child_date_ranges)
    results = entities_search(params)
    # test it returned the mock successfully
    assert results == []
    # test it created the correct payload
    mocked.assert_called_with(expected,0,10)
