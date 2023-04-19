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
"""Tests to ensure that the Solr Service query builders work as expected."""
import pytest

from bor_api.services.solr import Solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils.query_builders import (PRE_CHILD_FILTER_CLAUSE, _add_identifier, build_base_query,
                                                        build_child_query, build_facet, build_facet_query)


@pytest.mark.parametrize('test_name,field,term,expected', [
    ('test_basic_1', Field.IDENTIFIER_Q, 'BC1234', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")'),
    ('test_basic_lowercase_1', Field.IDENTIFIER_Q, 'bc1234', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")'),
    ('test_basic_2', Field.RELATED_IDENTIFIER_Q, 'BC1234', f'({Field.RELATED_IDENTIFIER_Q.value}:"1234" AND {Field.RELATED_IDENTIFIER_Q.value}:"BC")'),
    ('test_basic_lowercase_2', Field.RELATED_IDENTIFIER_Q, 'BC1234', f'({Field.RELATED_IDENTIFIER_Q.value}:"1234" AND {Field.RELATED_IDENTIFIER_Q.value}:"BC")'),
    ('test_other_types_1', Field.IDENTIFIER_Q, 'CP1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"CP")'),
    ('test_other_types_2', Field.IDENTIFIER_Q, 'S1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"S")'),
    ('test_other_types_3', Field.IDENTIFIER_Q, 'C1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"C")'),
    ('test_other_types_4', Field.IDENTIFIER_Q, 'ABCD1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"ABCD")'),
    ('test_number_only', Field.IDENTIFIER_Q, '1234567', f'{Field.IDENTIFIER_Q.value}:1234567'),
    ('test_not_identifier_1', Field.IDENTIFIER_Q, 'not idenitifier 1234567', f'{Field.IDENTIFIER_Q.value}:not idenitifier 1234567'),
    ('test_not_identifier_2', Field.IDENTIFIER_Q, '1234567notidentifier', f'{Field.IDENTIFIER_Q.value}:1234567notidentifier'),
    ('test_not_identifier_3', Field.IDENTIFIER_Q, 'not1234567id', f'{Field.IDENTIFIER_Q.value}:not1234567id'),
    ('test_not_identifier_4', Field.IDENTIFIER_Q, 'BC 1234567', f'{Field.IDENTIFIER_Q.value}:BC 1234567'),
    ('test_legal_name_q', Field.LEGAL_NAME_Q, 'BC1234567', f'{Field.LEGAL_NAME_Q.value}:BC1234567'),
    ('test_legal_name_agro_q', Field.LEGAL_NAME_AGRO_Q, 'BC1234567', f'{Field.LEGAL_NAME_AGRO_Q.value}:BC1234567'),
    ('test_legal_name_single_q', Field.LEGAL_NAME_SINGLE_Q, 'BC1234567', f'{Field.LEGAL_NAME_SINGLE_Q.value}:BC1234567'),
    ('test_bn_q', Field.BN_Q, 'BC1234567', f'{Field.BN_Q.value}:BC1234567'),
])
def test_add_identifier(test_name, field: Field, term: str, expected: str):
    """Assert the _add_identifier function works as expected."""
    assert _add_identifier(field.value, term) == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_basic',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': []}),
    ('test_basic_multi_fields',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {}, 'fuzzy': {}}, 
     {'query': f'({Field.LEGAL_NAME_Q.value}:name OR {Field.LEGAL_NAME_AGRO_Q.value}:name)', 'filter': []}),
    ('test_basic_multi_words',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st) AND ({Field.LEGAL_NAME_Q.value}:name2nd)', 'filter': []}),
    ('test_basic_multi__fields_words',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_boost',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name^5)', 'filter': []}),
    ('test_boost_multi_1',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st^5) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5)', 'filter': []}),
    ('test_boost_multi_2',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_boost_multi_3',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {Field.LEGAL_NAME_Q: 5, Field.LEGAL_NAME_AGRO_Q: 3}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st^3) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd^3)', 'filter': []}),
    ('test_fuzzy',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: 2}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name OR {Field.LEGAL_NAME_Q.value}:name~2)', 'filter': []}),
    ('test_fuzzy_term_too_short',
     {'query': {'value':'nam'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: 2}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:nam)', 'filter': []}),
    ('test_fuzzy_multi_1',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: 2}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st OR {Field.LEGAL_NAME_Q.value}:name1st~2) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_Q.value}:name2nd~2)', 'filter': []}),
    ('test_fuzzy_multi_2',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: 2}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st OR {Field.LEGAL_NAME_Q.value}:name1st~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_Q.value}:name2nd~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_fuzzy_multi_3',
     {'query': {'value':'name1st name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: 2, Field.LEGAL_NAME_AGRO_Q:3}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st OR {Field.LEGAL_NAME_Q.value}:name1st~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st~3) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_Q.value}:name2nd~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd~3)', 'filter': []}),
    ('test_filter',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc']}),
    ('test_filter_multi_1',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc ca'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca']}),
    ('test_filter_multi_2',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc ca', Field.IDENTIFIER_Q.value: 'bc1234'}, 'fields': [Field.LEGAL_NAME_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")']}),
    ('test_all',
     {'query': {'value':'name1st name2nd', Field.ADDRESS_Q.value: 'bc ca', Field.IDENTIFIER_Q.value: 'bc1234'},
      'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q, Field.IDENTIFIER_Q],
      'boost': {Field.LEGAL_NAME_Q: 5, Field.LEGAL_NAME_AGRO_Q: 3},
      'fuzzy': {Field.LEGAL_NAME_Q: 2, Field.LEGAL_NAME_AGRO_Q:3}
     },
     {'query': f'({Field.LEGAL_NAME_Q.value}:name1st^5 OR {Field.LEGAL_NAME_Q.value}:name1st~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st^3 OR {Field.LEGAL_NAME_AGRO_Q.value}:name1st~3 OR {Field.IDENTIFIER_Q.value}:name1st) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5 OR {Field.LEGAL_NAME_Q.value}:name2nd~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd^3 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd~3 OR {Field.IDENTIFIER_Q.value}:name2nd)',
      'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")']
     }),
])
def test_build_base_query(test_name, params, expected):
    """Assert that the build_base_query function works as expected."""
    base_query = build_base_query(query=params['query'],
                                  fields=params['fields'],
                                  boost_fields=params['boost'],
                                  fuzzy_fields=params['fuzzy'])
    assert base_query == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_basic',
     {Field.ADDRESS_Q.value: 'walaby'},
     f'({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:walaby)'),
    ('test_multi_1',
     {Field.ADDRESS_Q.value: 'walaby way'},
     f'({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:way)'),
    ('test_multi_2',
     {Field.ADDRESS_Q.value: 'walaby way', Field.RELATED_NAME_Q.value: 'name1st name2nd'},
     f'({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:way AND {PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_NAME_Q.value}:name1st AND {PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_NAME_Q.value}:name2nd)'),
])
def test_build_child_query(test_name, params, expected):
    """Assert that the build_child_query function works as expected."""
    assert build_child_query(params) == expected


@pytest.mark.parametrize('test_name,field,is_nested,expected', [
    ('test_parent', Field.LEGAL_TYPE, False,
     {Field.LEGAL_TYPE.value: {'type': 'terms', 'field': Field.LEGAL_TYPE.value}}),
    ('test_nested', Field.RELATED_STATE, True,
     {Field.RELATED_STATE.value: {'type': 'terms',
                                  'field': Field.RELATED_STATE.value,
                                  'domain': {'blockChildren': '{!v=$parents}'},
                                  'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}})
])
def test_build_facet(test_name, field, is_nested, expected):
    """Assert that the build_facet function works as expected."""
    assert build_facet(field, is_nested) == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_parent',
     {'field': Field.LEGAL_TYPE, 'values': ['BC', 'CP'], 'is_nested': False},
     f'{Field.LEGAL_TYPE.value}:("BC" OR "CP")'),
    ('test_nested',
     {'field': Field.ROLE_TYPE, 'values': ['DIRECTOR', 'INCORPORATOR'], 'is_nested': True},
     f'{PRE_CHILD_FILTER_CLAUSE}{Field.ROLE_TYPE.value}:"DIRECTOR" OR {Field.ROLE_TYPE.value}: "INCORPORATOR"'),
])
def test_build_facet_query(test_name, params, expected):
    """Assert that the build_facet function works as expected."""
    assert build_facet_query(**params) == expected
