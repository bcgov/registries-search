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
"""Test-Suite to ensure that the Solr Service is working as expected for updates/deletes/searches."""
import time
from dataclasses import asdict
from http import HTTPStatus

import pytest
from flask import Flask

from bor_api.services import bor_solr
from bor_api.services.solr import Solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.utils import parse_facets

from tests import integration_solr
from tests.unit.utils import create_solr_doc


@pytest.mark.parametrize('test_name,identifier,state,name,legal_type,bn', [
    ('test-1', 'CP1', 'ACTIVE', 'BASIC TEST 1', 'CP', '12345'),
])
def test_solr_doc(test_name, identifier, state, name, legal_type, bn):
    """Assert that solr doc class works as expected."""
    new_doc = create_solr_doc(name=name,
                              identifier=identifier,
                              state=state,
                              legal_type=legal_type,
                              bn=bn)
    assert new_doc
    json = asdict(new_doc)
    assert json
    assert json.get(Field.IDENTIFIER.value) == identifier
    assert json.get(Field.STATE.value) == state
    assert json.get(Field.LEGAL_TYPE.value) == legal_type
    assert json.get(Field.BN.value) == bn
    assert json.get(Field.LEGAL_NAME.value) == name


# will need to be altered once new solr config is complete
# @integration_solr
# @pytest.mark.parametrize('test_name,identifier,state,name,legal_type,bn', [
#     ('test-1', 'CP1234577', 'ACTIVE', 'BASIC TEST 1', 'CP', '12345'),
# ])
# def test_solr_create_delete(app, test_name, identifier, state, name, legal_type, bn):
#     """Assert that solr docs can be updates/searched/deleted."""
#     bor_solr.init_app(app)
#     bor_solr.delete_all_docs()
#     # add new doc
#     new_doc = create_solr_doc(identifier, name, state, legal_type, bn)
#     added = bor_solr.create_or_replace_docs([new_doc])
#     assert added.status_code == HTTPStatus.OK
#     time.sleep(2)  # takes up to 1 second for solr to register update
#     # search new doc
#     params = {'q': f'{Field.IDENTIFIER_Q.value}:{identifier}', 'fl': bor_solr.base_fields}
#     resp = bor_solr.query(params, 0, 10)
#     docs = resp['response']['docs']
#     assert len(docs) == 1
#     assert docs[0][Field.IDENTIFIER_Q.value] == identifier
#     assert docs[0][Field.BN_Q.value] == bn
#     assert docs[0][Field.LEGAL_NAME.value] == name
#     assert docs[0][Field.STATE.value] == state
#     assert docs[0][Field.LEGAL_TYPE.value] == legal_type
#     # delete doc
#     deleted = bor_solr.delete_docs([identifier])
#     assert deleted.status_code == HTTPStatus.OK
#     time.sleep(1)  # takes up to 1 second for solr to register update
#     # test search returns nothing
#     params = {'q': f'{Field.IDENTIFIER_Q.value}:{identifier}', 'fl': bor_solr.base_fields}
#     resp = bor_solr.query(params, 0, 10)
#     docs = resp['response']['docs']
#     assert len(docs) == 0


# @pytest.mark.parametrize('test_name,params,expected', [
#     ('test-basic-basic', {'query': 'name', 'fields': [Field.NAME_Q.value], 'wild': []}, {'q': f'({Field.NAME_Q.value}:name)', 'fq': ''}),
#     ('test-basic-basic-wild', {'query': 'name', 'fields': [Field.NAME_Q.value], 'wild': [Field.NAME_Q.value]}, {'q': f'({Field.NAME_Q.value}:name*)', 'fq': ''}),
#     ('test-basic-multi', {'query': 'name', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': []}, {'q': f'({Field.NAME_Q.value}:name OR {Field.NAME_AGRO_Q.value}:name)', 'fq': ''}),
#     ('test-basic-multi-wild-1', {'query': 'name', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_Q.value]}, {'q': f'({Field.NAME_Q.value}:name* OR {Field.NAME_AGRO_Q.value}:name)', 'fq': ''}),
#     ('test-basic-multi-wild-2', {'query': 'name', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_AGRO_Q.value]}, {'q': f'({Field.NAME_Q.value}:name OR {Field.NAME_AGRO_Q.value}:name*)', 'fq': ''}),
#     ('test-basic-multi-wild-3', {'query': 'name', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value]}, {'q': f'({Field.NAME_Q.value}:name* OR {Field.NAME_AGRO_Q.value}:name*)', 'fq': ''}),
#     ('test-multi-basic', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value], 'wild': []}, {'q': f'({Field.NAME_Q.value}:name1)', 'fq': f'({Field.NAME_Q.value}:name2) AND ({Field.NAME_Q.value}:name3)'}),
#     ('test-multi-basic-wild', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value], 'wild': [Field.NAME_Q.value]}, {'q': f'({Field.NAME_Q.value}:name1*)', 'fq': f'({Field.NAME_Q.value}:name2*) AND ({Field.NAME_Q.value}:name3*)'}),
#     ('test-multi-multi', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': []}, {'q': f'({Field.NAME_Q.value}:name1 OR {Field.NAME_AGRO_Q.value}:name1)', 'fq': f'({Field.NAME_Q.value}:name2 OR {Field.NAME_AGRO_Q.value}:name2) AND ({Field.NAME_Q.value}:name3 OR {Field.NAME_AGRO_Q.value}:name3)'}),
#     ('test-multi-multi-wild-1', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_Q.value]}, {'q': f'({Field.NAME_Q.value}:name1* OR {Field.NAME_AGRO_Q.value}:name1)', 'fq': f'({Field.NAME_Q.value}:name2* OR {Field.NAME_AGRO_Q.value}:name2) AND ({Field.NAME_Q.value}:name3* OR {Field.NAME_AGRO_Q.value}:name3)'}),
#     ('test-multi-multi-wild-2', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_AGRO_Q.value]}, {'q': f'({Field.NAME_Q.value}:name1 OR {Field.NAME_AGRO_Q.value}:name1*)', 'fq': f'({Field.NAME_Q.value}:name2 OR {Field.NAME_AGRO_Q.value}:name2*) AND ({Field.NAME_Q.value}:name3 OR {Field.NAME_AGRO_Q.value}:name3*)'}),
#     ('test-multi-multi-wild-3', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value], 'wild': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value]}, {'q': f'({Field.NAME_Q.value}:name1* OR {Field.NAME_AGRO_Q.value}:name1*)', 'fq': f'({Field.NAME_Q.value}:name2* OR {Field.NAME_AGRO_Q.value}:name2*) AND ({Field.NAME_Q.value}:name3* OR {Field.NAME_AGRO_Q.value}:name3*)'}),
#     ('test-complex-1', {'query': 'name1 name2 name3', 'fields': [Field.NAME_Q.value, Field.NAME_AGRO_Q.value, Field.IDENTIFIER_Q.value, Field.BN_Q.value], 'wild': [Field.IDENTIFIER_Q.value, Field.BN_Q.value]}, {'q': f'({Field.NAME_Q.value}:name1 OR {Field.NAME_AGRO_Q.value}:name1 OR ({Field.IDENTIFIER_Q.value}:"1" AND {Field.IDENTIFIER_Q.value}:"NAME") OR {Field.BN_Q.value}:name1*)', 'fq': f'({Field.NAME_Q.value}:name2 OR {Field.NAME_AGRO_Q.value}:name2 OR {Field.IDENTIFIER_Q.value}:name2* OR {Field.BN_Q.value}:name2*) AND ({Field.NAME_Q.value}:name3 OR {Field.NAME_AGRO_Q.value}:name3 OR {Field.IDENTIFIER_Q.value}:name3* OR {Field.BN_Q.value}:name3*)'}),
# ])
# def test_build_split_query(test_name, params, expected):
#     """Assert that the build_base_query function works as expected."""
#     split_query = Solr.build_base_query({'value': params['query']}, params['fields'], params['wild'])
#     assert split_query == expected


@pytest.mark.parametrize('test_name,facet_data,expected', [
    ('test-1',
     {'facets': {Field.LEGAL_TYPE.value: {'buckets': [{'val': 'BEN', 'count': 23}, {'val': 'CP', 'count': 10}, {'val': 'SP', 'count': 102}]}, Field.STATE.value: {'buckets': [{'val': 'ACTIVE', 'count': 23}, {'val': 'HISTORICAL', 'count': 10}]}}},
     {'fields': {Field.LEGAL_TYPE.value: [{'value': 'BEN', 'count': 23}, {'value': 'CP', 'count': 10}, {'value': 'SP', 'count': 102}], Field.STATE.value: [{'value': 'ACTIVE', 'count': 23}, {'value': 'HISTORICAL', 'count': 10}]}}),
])
def test_parse_facets(test_name, facet_data, expected):
    """Assert the parse facets function works as expected."""
    facet_info = parse_facets(facet_data)
    assert facet_info == expected
