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
from bor_api.services.bor_solr.fields import AddressField, EntityField, EntityRoleField
from bor_api.services.bor_solr.utils.query_builders import (PRE_CHILD_FILTER_CLAUSE, _create_clause, _find_synonym_terms,
                                                            build_base_query, build_child_query, build_facet, build_facet_query)


@pytest.mark.parametrize('test_name,field,term,expected,is_child', [
    ('test_basic_1', EntityField.IDENTIFIER_Q, 'BC1234', f'({EntityField.IDENTIFIER_Q.value}:"1234" AND {EntityField.IDENTIFIER_Q.value}:"BC")', False),
    ('test_basic_lowercase_1', EntityField.IDENTIFIER_Q, 'bc1234', f'({EntityField.IDENTIFIER_Q.value}:"1234" AND {EntityField.IDENTIFIER_Q.value}:"BC")', False),
    ('test_basic_2', EntityRoleField.RELATED_IDENTIFIER_Q, 'BC1234', f'({PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_IDENTIFIER_Q.value}:"1234" AND {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_IDENTIFIER_Q.value}:"BC")', True),
    ('test_basic_lowercase_2', EntityRoleField.RELATED_IDENTIFIER_Q, 'BC1234', f'({PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_IDENTIFIER_Q.value}:"1234" AND {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_IDENTIFIER_Q.value}:"BC")', True),
    ('test_other_types_1', EntityField.IDENTIFIER_Q, 'CP1234567', f'({EntityField.IDENTIFIER_Q.value}:"1234567" AND {EntityField.IDENTIFIER_Q.value}:"CP")', False),
    ('test_other_types_2', EntityField.IDENTIFIER_Q, 'S1234567', f'({EntityField.IDENTIFIER_Q.value}:"1234567" AND {EntityField.IDENTIFIER_Q.value}:"S")', False),
    ('test_other_types_3', EntityField.IDENTIFIER_Q, 'C1234567', f'({EntityField.IDENTIFIER_Q.value}:"1234567" AND {EntityField.IDENTIFIER_Q.value}:"C")', False),
    ('test_other_types_4', EntityField.IDENTIFIER_Q, 'ABCD1234567', f'({EntityField.IDENTIFIER_Q.value}:"1234567" AND {EntityField.IDENTIFIER_Q.value}:"ABCD")', False),
    ('test_number_only', EntityField.IDENTIFIER_Q, '1234567', f'{EntityField.IDENTIFIER_Q.value}:1234567', False),
    ('test_not_identifier_1', EntityField.IDENTIFIER_Q, 'not idenitifier 1234567', f'{EntityField.IDENTIFIER_Q.value}:not idenitifier 1234567', False),
    ('test_not_identifier_2', EntityField.IDENTIFIER_Q, '1234567notidentifier', f'{EntityField.IDENTIFIER_Q.value}:1234567notidentifier', False),
    ('test_not_identifier_3', EntityField.IDENTIFIER_Q, 'not1234567id', f'{EntityField.IDENTIFIER_Q.value}:not1234567id', False),
    ('test_not_identifier_4', EntityField.IDENTIFIER_Q, 'BC 1234567', f'{EntityField.IDENTIFIER_Q.value}:BC 1234567', False),
    ('test_legal_name_q', EntityField.LEGAL_NAME_Q, 'BC1234567', f'{EntityField.LEGAL_NAME_Q.value}:BC1234567', False),
    ('test_legal_name_agro_q', EntityField.LEGAL_NAME_AGRO_Q, 'BC1234567', f'{EntityField.LEGAL_NAME_AGRO_Q.value}:BC1234567', False),
    ('test_legal_name_single_q', EntityField.LEGAL_NAME_SINGLE_Q, 'BC1234567', f'{EntityField.LEGAL_NAME_SINGLE_Q.value}:BC1234567', False),
    ('test_bn_q', EntityField.BN_Q, 'BC1234567', f'{EntityField.BN_Q.value}:BC1234567', False),
])
def test_add_identifier(test_name, field: EntityField | EntityRoleField, term: str, expected: str, is_child: bool):
    """Assert the _create_clause function works as expected."""
    assert _create_clause(field.value, term, is_child) == expected


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

    assert _find_synonym_terms(start_term=term, start_term_index=term_index, terms=terms, field=AddressField.ADDRESS_SYN_Q) == expected
    assert _find_synonym_terms(start_term=term, start_term_index=term_index, terms=terms, field=EntityField.LEGAL_NAME_SYN_Q) == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_basic',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name)', 'filter': []}),
    ('test_basic_multi_fields_1',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {}, 'fuzzy': {}}, 
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name)', 'filter': []}
    ),
    ('test_basic_multi_fields_2',
     {'query': {'value':'name@email.com'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent', EntityField.EMAIL_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child'}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name@email.com OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name@email.com OR {EntityField.EMAIL_Q.value}:name@email.com)', 'filter': []}
    ),
    ('test_basic_multi_words',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd)', 'filter': []}),
    ('test_basic_multi_fields_words',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_nested_fields',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent', AddressField.ADDRESS_Q: 'child'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01 OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name01) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2nd OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name2nd)', 'filter': []}),
    ('test_nested_fields_multi',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent', AddressField.ADDRESS_Q: 'child', EntityRoleField.RELATED_NAME: 'child'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01 OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name01 OR {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_NAME.value}:name01) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2nd OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name2nd OR {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_NAME.value}:name2nd)', 'filter': []}),
    ('test_boost',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {EntityField.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name^5)', 'filter': []}),
    ('test_boost_multi_1',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {EntityField.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01^5) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd^5)', 'filter': []}),
    ('test_boost_multi_2',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {EntityField.LEGAL_NAME_Q: 5}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01^5 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd^5 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2nd)', 'filter': []}),
    ('test_boost_multi_3',
     {'query': {'value':'name01 name2nd'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {EntityField.LEGAL_NAME_Q: 5, EntityField.LEGAL_NAME_AGRO_Q: 3}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01^5 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01^3) AND ({EntityField.LEGAL_NAME_Q.value}:name2nd^5 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2nd^3)', 'filter': []}),
    ('test_fuzzy_short',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name OR {EntityField.LEGAL_NAME_Q.value}:name~1)', 'filter': []}),
    ('test_fuzzy_long',
     {'query': {'value':'namelong'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:namelong OR {EntityField.LEGAL_NAME_Q.value}:namelong~2)', 'filter': []}),
    ('test_fuzzy_term_too_short',
     {'query': {'value':'nam'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:nam)', 'filter': []}),
    ('test_fuzzy_multi_1',
     {'query': {'value':'nam short namelong'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:nam) AND ({EntityField.LEGAL_NAME_Q.value}:short OR {EntityField.LEGAL_NAME_Q.value}:short~1) AND ({EntityField.LEGAL_NAME_Q.value}:namelong OR {EntityField.LEGAL_NAME_Q.value}:namelong~2)', 'filter': []}),
    ('test_fuzzy_multi_2',
     {'query': {'value':'nam short namelong'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 2, 'long': 3}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:nam OR {EntityField.LEGAL_NAME_AGRO_Q.value}:nam) AND ({EntityField.LEGAL_NAME_Q.value}:short OR {EntityField.LEGAL_NAME_Q.value}:short~2 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:short) AND ({EntityField.LEGAL_NAME_Q.value}:namelong OR {EntityField.LEGAL_NAME_Q.value}:namelong~3 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:namelong)', 'filter': []}),
    ('test_fuzzy_multi_3',
     {'query': {'value':'name01 name2ndlong'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent'}, 'boost': {}, 'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}, EntityField.LEGAL_NAME_AGRO_Q: {'short': 3, 'long': 4}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name01 OR {EntityField.LEGAL_NAME_Q.value}:name01~1 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name01~3) AND ({EntityField.LEGAL_NAME_Q.value}:name2ndlong OR {EntityField.LEGAL_NAME_Q.value}:name2ndlong~2 OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2ndlong OR {EntityField.LEGAL_NAME_AGRO_Q.value}:name2ndlong~4)', 'filter': []}),
    ('test_filter',
     {'query': {'value':'name', AddressField.ADDRESS_Q.value: 'bc'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name)', 'filter': [f'{AddressField.ADDRESS_Q.value}:bc']}),
    ('test_filter_multi_1',
     {'query': {'value':'name', AddressField.ADDRESS_Q.value: 'bc ca'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name)', 'filter': [f'{AddressField.ADDRESS_Q.value}:bc', f'{AddressField.ADDRESS_Q.value}:ca']}),
    ('test_filter_multi_2',
     {'query': {'value':'name', AddressField.ADDRESS_Q.value: 'bc ca', EntityField.IDENTIFIER_Q.value: 'bc1234'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name)', 'filter': [f'{AddressField.ADDRESS_Q.value}:bc', f'{AddressField.ADDRESS_Q.value}:ca', f'({EntityField.IDENTIFIER_Q.value}:"1234" AND {EntityField.IDENTIFIER_Q.value}:"BC")']}),
    ('test_synonym_parent_1',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['name']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name OR ({EntityField.LEGAL_NAME_SYN_Q.value}:name))', 'filter': []}),
    ('test_synonym_parent_2',
     {'query': {'value':'synonym1 synonym2'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym1', 'synonym2']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:synonym1 OR ({EntityField.LEGAL_NAME_SYN_Q.value}:synonym1)) AND ({EntityField.LEGAL_NAME_Q.value}:synonym2 OR ({EntityField.LEGAL_NAME_SYN_Q.value}:synonym2))', 'filter': []}),
    ('test_synonym_parent_3',
     {'query': {'value':'synonym nonsynonym'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:synonym OR ({EntityField.LEGAL_NAME_SYN_Q.value}:synonym)) AND ({EntityField.LEGAL_NAME_Q.value}:nonsynonym)', 'filter': []}),
    ('test_synonym_parent_4',
     {'query': {'value':'nonsynonym synonym'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['synonym']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:nonsynonym) AND ({EntityField.LEGAL_NAME_Q.value}:synonym OR ({EntityField.LEGAL_NAME_SYN_Q.value}:synonym))', 'filter': []}),
    ('test_synonym_parent_5',
     {'query': {'value':'multi word synonym'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['multi word synonym']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:multi OR ({EntityField.LEGAL_NAME_SYN_Q.value}:multi word synonym)) AND ({EntityField.LEGAL_NAME_Q.value}:word OR ({EntityField.LEGAL_NAME_SYN_Q.value}:multi word synonym)) AND ({EntityField.LEGAL_NAME_Q.value}:synonym OR ({EntityField.LEGAL_NAME_SYN_Q.value}:multi word synonym))', 'filter': []}),
    ('test_synonym_parent_6',
     {'query': {'value':'partial synonym'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', 'test_prep': {SolrSynonymType.NAME: ['partial synonym not enough']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:partial) AND ({EntityField.LEGAL_NAME_Q.value}:synonym)', 'filter': []}),
    ('test_synonym_child_1',
     {'query': {'value':'canada'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['canada']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:canada OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:canada))', 'filter': []}),
    ('test_synonym_child_2',
     {'query': {'value':'name british columbia'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name) AND ({EntityField.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:british columbia)) AND ({EntityField.LEGAL_NAME_Q.value}:columbia OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:british columbia))', 'filter': []}),
    ('test_synonym_child_3_uses_longest_syn',
     {'query': {'value':'name british columbia'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia', 'british']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name) AND ({EntityField.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:british columbia)) AND ({EntityField.LEGAL_NAME_Q.value}:columbia OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:british columbia))', 'filter': []}),
    ('test_synonym_child_4',
     {'query': {'value':'name british notcolumbia'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['british columbia', 'british']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name) AND ({EntityField.LEGAL_NAME_Q.value}:british OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:british)) AND ({EntityField.LEGAL_NAME_Q.value}:notcolumbia)', 'filter': []}),
    ('test_synonym_all',
     {'query': {'value':'namesyn address synonym'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['address synonym', 'synonym'], SolrSynonymType.NAME: ['namesyn']}}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:namesyn OR ({EntityField.LEGAL_NAME_SYN_Q.value}:namesyn)) AND ({EntityField.LEGAL_NAME_Q.value}:address OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:address synonym)) AND ({EntityField.LEGAL_NAME_Q.value}:synonym OR ({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_SYN_Q.value}:address synonym))',
      'filter': []}
    ),
    ('test_synonym_none',
     {'query': {'value':'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child'}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name)', 'filter': []}),
    ('test_all',
     {'query': {'value':'name01 namelong', AddressField.ADDRESS_Q.value: 'bc ca', EntityField.INFO_Q.value: '1234'},
      'fields': {EntityField.LEGAL_NAME_Q: 'parent', EntityField.LEGAL_NAME_AGRO_Q: 'parent', AddressField.ADDRESS_Q: 'child'},
      'boost': {EntityField.LEGAL_NAME_Q: 5, EntityField.LEGAL_NAME_AGRO_Q: 3},
      'fuzzy': {EntityField.LEGAL_NAME_Q: {'short': 1, 'long': 2}, EntityField.LEGAL_NAME_AGRO_Q: {'short': 2, 'long': 3}, AddressField.ADDRESS_Q: {'short': 1, 'long': 1}},
      'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child', 'test_prep': {SolrSynonymType.ADDRESS: ['name01 namelong'], SolrSynonymType.NAME: ['name01']}}
     },
     {'query': "(legalName_q:name01^5 OR legalName_q:name01~1 OR legalName_stem_agro_q:name01^3 OR legalName_stem_agro_q:name01~2 OR {!parent which = '-_nest_path_:* entityType:*'}address_q:name01 OR {!parent which = '-_nest_path_:* entityType:*'}address_q:name01~1 OR (legalName_synonym_q:name01) OR ({!parent which = '-_nest_path_:* entityType:*'}address_synonym_q:name01 namelong)) AND (legalName_q:namelong^5 OR legalName_q:namelong~2 OR legalName_stem_agro_q:namelong^3 OR legalName_stem_agro_q:namelong~3 OR {!parent which = '-_nest_path_:* entityType:*'}address_q:namelong OR {!parent which = '-_nest_path_:* entityType:*'}address_q:namelong~1 OR ({!parent which = '-_nest_path_:* entityType:*'}address_synonym_q:name01 namelong))",
      'filter': [f'{AddressField.ADDRESS_Q.value}:bc', f'{AddressField.ADDRESS_Q.value}:ca', f'{EntityField.INFO_Q.value}:1234']
     }
    ),
    ('test_name_filter',
     {'query': {'value':'fullname', 'name_q': 'name'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent'}, 'boost': {}, 'fuzzy': {}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:fullname)', 'filter': ['name_q:name']}
    ),
    ('test_child_clause_1',
     {'query': {'value':'name child'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', AddressField.ADDRESS_Q: 'child'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child'}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name) AND ({EntityField.LEGAL_NAME_Q.value}:child OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:child)', 'filter': []}
    ),
    ('test_child_clause_2',
     {'query': {'value':'name@email.com'}, 'fields': {EntityField.LEGAL_NAME_Q: 'parent', AddressField.ADDRESS_Q: 'child', EntityRoleField.RELATED_EMAIL_Q: 'child'}, 'boost': {}, 'fuzzy': {}, 'syns': {EntityField.LEGAL_NAME_SYN_Q: 'parent', AddressField.ADDRESS_SYN_Q: 'child'}},
     {'query': f'({EntityField.LEGAL_NAME_Q.value}:name@email.com OR {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:name@email.com OR {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_EMAIL_Q.value}:name@email.com)', 'filter': []}
    )
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
                                  boost_fields=params['boost'],
                                  fuzzy_fields=params['fuzzy'],
                                  synonym_fields=params.get('syns', {}))
    assert base_query == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_basic',
     {AddressField.ADDRESS_Q.value: 'walaby'},
     f'({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:walaby)'),
    ('test_multi_1',
     {AddressField.ADDRESS_Q.value: 'walaby way'},
     f'({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:way)'),
    ('test_multi_2',
     {AddressField.ADDRESS_Q.value: 'walaby way', EntityRoleField.RELATED_NAME_Q.value: 'name1st name2nd'},
     f'({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:way AND {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_NAME_Q.value}:name1st AND {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_NAME_Q.value}:name2nd)'),
    ('test_multi_3',
     {AddressField.ADDRESS_Q.value: 'walaby way', EntityRoleField.RELATED_EMAIL_Q.value: '123@email.com'},
     f'({PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:walaby AND {PRE_CHILD_FILTER_CLAUSE}{AddressField.ADDRESS_Q.value}:way AND {PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_EMAIL_Q.value}:123@email.com)'),
])
def test_build_child_query(test_name, params, expected):
    """Assert that the build_child_query function works as expected."""
    assert build_child_query(params) == expected


@pytest.mark.parametrize('test_name,field,is_nested,expected', [
    ('test_parent', EntityField.LEGAL_TYPE, False,
     {EntityField.LEGAL_TYPE.value: {'type': 'terms', 'field': EntityField.LEGAL_TYPE.value}}),
    ('test_nested', EntityRoleField.RELATED_STATE, True,
     {EntityRoleField.RELATED_STATE.value: {'type': 'terms',
                                  'field': EntityRoleField.RELATED_STATE.value,
                                  'domain': {'blockChildren': '{!v=$parents}'},
                                  'facet': {'by_parent': 'uniqueBlock({!v=$parents})'}}})
])
def test_build_facet(test_name, field, is_nested, expected):
    """Assert that the build_facet function works as expected."""
    assert build_facet(field, is_nested) == expected


@pytest.mark.parametrize('test_name,params,expected', [
    ('test_parent',
     {'field': EntityField.LEGAL_TYPE, 'values': ['BC', 'CP'], 'is_nested': False},
     f'{EntityField.LEGAL_TYPE.value}:("BC" OR "CP")'),
    ('test_nested',
     {'field': EntityRoleField.ROLE_TYPE, 'values': ['DIRECTOR', 'INCORPORATOR'], 'is_nested': True},
     f'{PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.ROLE_TYPE.value}:"DIRECTOR" OR {EntityRoleField.ROLE_TYPE.value}: "INCORPORATOR"'),
])
def test_build_facet_query(test_name, params, expected):
    """Assert that the build_facet function works as expected."""
    assert build_facet_query(**params) == expected
