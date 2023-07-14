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

from bor_api.enums import SolrSynonymType
from bor_api.models import SolrSynonymList
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils.query_builders import (PRE_CHILD_FILTER_CLAUSE, _add_identifier, _find_synonym_terms,
                                                        build_base_query, build_child_query, build_facet, build_facet_query)


@pytest.mark.parametrize('test_name,field,term,expected,is_child', [
    ('test_basic_1', Field.IDENTIFIER_Q, 'BC1234', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")', False),
    ('test_basic_lowercase_1', Field.IDENTIFIER_Q, 'bc1234', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")', False),
    ('test_basic_2', Field.RELATED_IDENTIFIER_Q, 'BC1234', f'({PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_IDENTIFIER_Q.value}:"1234" AND {PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_IDENTIFIER_Q.value}:"BC")', True),
    ('test_basic_lowercase_2', Field.RELATED_IDENTIFIER_Q, 'BC1234', f'({PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_IDENTIFIER_Q.value}:"1234" AND {PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_IDENTIFIER_Q.value}:"BC")', True),
    ('test_other_types_1', Field.IDENTIFIER_Q, 'CP1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"CP")', False),
    ('test_other_types_2', Field.IDENTIFIER_Q, 'S1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"S")', False),
    ('test_other_types_3', Field.IDENTIFIER_Q, 'C1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"C")', False),
    ('test_other_types_4', Field.IDENTIFIER_Q, 'ABCD1234567', f'({Field.IDENTIFIER_Q.value}:"1234567" AND {Field.IDENTIFIER_Q.value}:"ABCD")', False),
    ('test_number_only', Field.IDENTIFIER_Q, '1234567', f'{Field.IDENTIFIER_Q.value}:1234567', False),
    ('test_not_identifier_1', Field.IDENTIFIER_Q, 'not idenitifier 1234567', f'{Field.IDENTIFIER_Q.value}:not idenitifier 1234567', False),
    ('test_not_identifier_2', Field.IDENTIFIER_Q, '1234567notidentifier', f'{Field.IDENTIFIER_Q.value}:1234567notidentifier', False),
    ('test_not_identifier_3', Field.IDENTIFIER_Q, 'not1234567id', f'{Field.IDENTIFIER_Q.value}:not1234567id', False),
    ('test_not_identifier_4', Field.IDENTIFIER_Q, 'BC 1234567', f'{Field.IDENTIFIER_Q.value}:BC 1234567', False),
    ('test_legal_name_q', Field.LEGAL_NAME_Q, 'BC1234567', f'{Field.LEGAL_NAME_Q.value}:BC1234567', False),
    ('test_legal_name_agro_q', Field.LEGAL_NAME_AGRO_Q, 'BC1234567', f'{Field.LEGAL_NAME_AGRO_Q.value}:BC1234567', False),
    ('test_legal_name_single_q', Field.LEGAL_NAME_SINGLE_Q, 'BC1234567', f'{Field.LEGAL_NAME_SINGLE_Q.value}:BC1234567', False),
    ('test_bn_q', Field.BN_Q, 'BC1234567', f'{Field.BN_Q.value}:BC1234567', False),
])
def test_add_identifier(test_name, field: Field, term: str, expected: str, is_child: bool):
    """Assert the _add_identifier function works as expected."""
    assert _add_identifier(field.value, term, is_child) == expected


@pytest.mark.parametrize('test_name,term,term_index,terms,expected,test_prep', [
    ('test_1', 'synonym', 0, ['synonym'], ['synonym'], ['synonym']),
    ('test_2', 'synonym', 1, ['first', 'synonym', 'third'], [], ['synonym multi']),
    ('test_3', 'synonym', 1, ['first', 'synonym', 'multi'], ['synonym', 'multi'], ['synonym multi']),
    ('test_4', 'secondsynterm', 2, ['first', 'synonym', 'secondsynterm'], [], ['synonym secondsynterm']),
    ('test_5', 'synonym', 1, ['first', 'synonym', 'multi', 'longer'], ['synonym', 'multi', 'longer'], ['synonym multi', 'synonym multi longer']),
])
def test_find_synonym_terms(session, test_name, term: str, term_index: int, terms: list[str], expected: str, test_prep: list[str]):
    """Assert the _find_synonym_terms function works as expected."""
    for syn in test_prep:
        SolrSynonymList(synonym=syn, synonym_list=['bla', syn], synonym_type=SolrSynonymType.ADDRESS).save()
        SolrSynonymList(synonym=syn, synonym_list=['bla', syn], synonym_type=SolrSynonymType.NAME).save()

    assert _find_synonym_terms(start_term=term, start_term_index=term_index, terms=terms, field=Field.ADDRESS_SYN_Q) == expected
    assert _find_synonym_terms(start_term=term, start_term_index=term_index, terms=terms, field=Field.LEGAL_NAME_SYN_Q) == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_basic',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': []}),
    ('test_basic_multi_fields',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}}, 
     {'query': f'({Field.LEGAL_NAME_Q.value}:name OR {Field.LEGAL_NAME_AGRO_Q.value}:name)', 'filter': []}),
    ('test_basic_multi_words',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01) AND ({Field.LEGAL_NAME_Q.value}:name2nd)', 'filter': []}),
    ('test_basic_multi_fields_words',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_nested_fields',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [Field.ADDRESS_Q], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01 OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:name01)) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:name2nd))', 'filter': []}),
    ('test_nested_fields_multi',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [Field.ADDRESS_Q, Field.RELATED_NAME], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01 OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:name01) OR ({PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_NAME.value}:name01)) AND ({Field.LEGAL_NAME_Q.value}:name2nd OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:name2nd) OR ({PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_NAME.value}:name2nd))', 'filter': []}),
    ('test_boost',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name^5)', 'filter': []}),
    ('test_boost_multi_1',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01^5) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5)', 'filter': []}),
    ('test_boost_multi_2',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {Field.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_boost_multi_3',
     {'query': {'value':'name01 name2nd'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {Field.LEGAL_NAME_Q: 5, Field.LEGAL_NAME_AGRO_Q: 3}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01^3) AND ({Field.LEGAL_NAME_Q.value}:name2nd^5 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2nd^3)', 'filter': []}),
    ('test_fuzzy_short',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name OR {Field.LEGAL_NAME_Q.value}:name~1)', 'filter': []}),
    ('test_fuzzy_long',
     {'query': {'value':'namelong'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:namelong OR {Field.LEGAL_NAME_Q.value}:namelong~2)', 'filter': []}),
    ('test_fuzzy_term_too_short',
     {'query': {'value':'nam'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:nam)', 'filter': []}),
    ('test_fuzzy_multi_1',
     {'query': {'value':'nam short namelong'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:nam) AND ({Field.LEGAL_NAME_Q.value}:short OR {Field.LEGAL_NAME_Q.value}:short~1) AND ({Field.LEGAL_NAME_Q.value}:namelong OR {Field.LEGAL_NAME_Q.value}:namelong~2)', 'filter': []}),
    ('test_fuzzy_multi_2',
     {'query': {'value':'nam short namelong'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 2, 'long': 3}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:nam OR {Field.LEGAL_NAME_AGRO_Q.value}:nam) AND ({Field.LEGAL_NAME_Q.value}:short OR {Field.LEGAL_NAME_Q.value}:short~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:short) AND ({Field.LEGAL_NAME_Q.value}:namelong OR {Field.LEGAL_NAME_Q.value}:namelong~3 OR {Field.LEGAL_NAME_AGRO_Q.value}:namelong)', 'filter': []}),
    ('test_fuzzy_multi_3',
     {'query': {'value':'name01 name2ndlong'}, 'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}, Field.LEGAL_NAME_AGRO_Q: {'short': 3, 'long': 4}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name01 OR {Field.LEGAL_NAME_Q.value}:name01~1 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01 OR {Field.LEGAL_NAME_AGRO_Q.value}:name01~3) AND ({Field.LEGAL_NAME_Q.value}:name2ndlong OR {Field.LEGAL_NAME_Q.value}:name2ndlong~2 OR {Field.LEGAL_NAME_AGRO_Q.value}:name2ndlong OR {Field.LEGAL_NAME_AGRO_Q.value}:name2ndlong~4)', 'filter': []}),
    ('test_filter',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc']}),
    ('test_filter_multi_1',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc ca'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca']}),
    ('test_filter_multi_2',
     {'query': {'value':'name', Field.ADDRESS_Q.value: 'bc ca', Field.IDENTIFIER_Q.value: 'bc1234'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")']}),
    ('test_synonym_parent_1',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['name']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name OR ({Field.LEGAL_NAME_SYN_Q.value}:name))', 'filter': []}),
    ('test_synonym_parent_2',
     {'query': {'value':'synonym1 synonym2'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym1', 'synonym2']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:synonym1 OR ({Field.LEGAL_NAME_SYN_Q.value}:synonym1)) AND ({Field.LEGAL_NAME_Q.value}:synonym2 OR ({Field.LEGAL_NAME_SYN_Q.value}:synonym2))', 'filter': []}),
    ('test_synonym_parent_3',
     {'query': {'value':'synonym nonsynonym'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:synonym OR ({Field.LEGAL_NAME_SYN_Q.value}:synonym)) AND ({Field.LEGAL_NAME_Q.value}:nonsynonym)', 'filter': []}),
    ('test_synonym_parent_4',
     {'query': {'value':'nonsynonym synonym'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:nonsynonym) AND ({Field.LEGAL_NAME_Q.value}:synonym OR ({Field.LEGAL_NAME_SYN_Q.value}:synonym))', 'filter': []}),
    ('test_synonym_parent_5',
     {'query': {'value':'multi word synonym'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['multi word synonym']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:multi OR ({Field.LEGAL_NAME_SYN_Q.value}:multi word synonym)) AND ({Field.LEGAL_NAME_Q.value}:word OR ({Field.LEGAL_NAME_SYN_Q.value}:multi word synonym)) AND ({Field.LEGAL_NAME_Q.value}:synonym OR ({Field.LEGAL_NAME_SYN_Q.value}:multi word synonym))', 'filter': []}),
    ('test_synonym_parent_6',
     {'query': {'value':'partial synonym'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['partial synonym not enough']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:partial) AND ({Field.LEGAL_NAME_Q.value}:synonym)', 'filter': []}),
    ('test_synonym_child_1',
     {'query': {'value':'canada'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['canada']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:canada OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:canada))', 'filter': []}),
    ('test_synonym_child_2',
     {'query': {'value':'name british columbia'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name) AND ({Field.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:british columbia)) AND ({Field.LEGAL_NAME_Q.value}:columbia OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:british columbia))', 'filter': []}),
    ('test_synonym_child_3_uses_longest_syn',
     {'query': {'value':'name british columbia'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia', 'british']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name) AND ({Field.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:british columbia)) AND ({Field.LEGAL_NAME_Q.value}:columbia OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:british columbia))', 'filter': []}),
    ('test_synonym_child_4',
     {'query': {'value':'name british notcolumbia'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia', 'british']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name) AND ({Field.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:british)) AND ({Field.LEGAL_NAME_Q.value}:notcolumbia)', 'filter': []}),
    ('test_synonym_all',
     {'query': {'value':'namesyn address synonym'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['address synonym', 'synonym'], SolrSynonymType.NAME: ['namesyn']}}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:namesyn OR ({Field.LEGAL_NAME_SYN_Q.value}:namesyn)) AND ({Field.LEGAL_NAME_Q.value}:address OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:address synonym)) AND ({Field.LEGAL_NAME_Q.value}:synonym OR ({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_SYN_Q.value}:address synonym))', 'filter': []}),
    ('test_synonym_none',
     {'query': {'value':'name'}, 'fields': [Field.LEGAL_NAME_Q], 'nested_fields': [], 'boost': {}, 'fuzzy': {}, 'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', Field.ADDRESS_SYN_Q: 'child'}},
     {'query': f'({Field.LEGAL_NAME_Q.value}:name)', 'filter': []}),
    ('test_all',
     {'query': {'value':'name01 namelong', Field.ADDRESS_Q.value: 'bc ca', Field.IDENTIFIER_Q.value: 'bc1234'},
      'fields': [Field.LEGAL_NAME_Q, Field.LEGAL_NAME_AGRO_Q, Field.IDENTIFIER_Q],
      'nested_fields': [Field.ADDRESS_Q, Field.RELATED_NAME],
      'boost': {Field.LEGAL_NAME_Q: 5, Field.LEGAL_NAME_AGRO_Q: 3},
      'fuzzy': {Field.LEGAL_NAME_Q: {'short': 1, 'long': 2}, Field.LEGAL_NAME_AGRO_Q: {'short': 2, 'long': 3}, Field.ADDRESS_Q: {'short': 1, 'long': 1}},
      'syns': {Field.LEGAL_NAME_SYN_Q: 'parent', Field.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['name01 namelong'], SolrSynonymType.NAME: ['name01']}}
     },
     {'query': '(legalName_q:name01^5 OR legalName_q:name01~1 OR legalName_stem_agro_q:name01^3 OR legalName_stem_agro_q:name01~2 OR (identifier_q:"01" AND identifier_q:"NAME") OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:name01~1) OR ({!parent which = \'-_nest_path_:* entityType:*\'}relatedName:name01) OR (legalName_synonym_q:name01) OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_synonym_q:name01 namelong)) AND (legalName_q:namelong^5 OR legalName_q:namelong~2 OR legalName_stem_agro_q:namelong^3 OR legalName_stem_agro_q:namelong~3 OR identifier_q:namelong OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_q:namelong~1) OR ({!parent which = \'-_nest_path_:* entityType:*\'}relatedName:namelong) OR ({!parent which = \'-_nest_path_:* entityType:*\'}address_synonym_q:name01 namelong))', 'filter': ['address_q:bc', 'address_q:ca', '(identifier_q:"1234" AND identifier_q:"BC")'],
      'filter': [f'{Field.ADDRESS_Q.value}:bc', f'{Field.ADDRESS_Q.value}:ca', f'({Field.IDENTIFIER_Q.value}:"1234" AND {Field.IDENTIFIER_Q.value}:"BC")']
     }),
])
def test_build_base_query(app, session, test_name, params, expected):
    """Assert that the build_base_query function works as expected."""
    test_prep = params.get('syns', {}).get('test_prep', {})
    for syn_type in test_prep:
        for syn in test_prep[syn_type]:
            SolrSynonymList(synonym=syn, synonym_list=['bla', syn], synonym_type=syn_type).save()
    if test_prep:
        del params['syns']['test_prep']
    base_query = build_base_query(query=params['query'],
                                  fields=params['fields'],
                                  nested_fields=params['nested_fields'],
                                  boost_fields=params['boost'],
                                  fuzzy_fields=params['fuzzy'],
                                  synonym_fields=params.get('syns', {}))
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
    ('test_multi_3',
     {Field.ADDRESS_Q.value: 'walaby way', Field.RELATED_EMAIL_Q.value: '123@email.com'},
     f'({PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{Field.ADDRESS_Q.value}:way AND {PRE_CHILD_FILTER_CLAUSE}{Field.RELATED_EMAIL_Q.value}:123@email.com)'),
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
