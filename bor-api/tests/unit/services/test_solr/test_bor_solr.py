# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE_2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests to ensure that the Solr Service BOR class is working as expected."""
import time
from http import HTTPStatus

import pytest
import requests_mock
from datetime import datetime, timedelta

from bor_api.exceptions import SolrException
from bor_api.services import bor_solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field

from tests import integration_solr
from tests.unit.utils import SOLR_TEST_DOCS, create_entity, factory_entity_default


@integration_solr
def test_create_update_delete_query(app):
    """Assert that solr docs can be created/updated/searched/deleted."""
    # init
    bor_solr.init_app(app)
    bor_solr.delete_all_docs()
    # add new entity
    name='test'
    new_entity = factory_entity_default(name=name)
    added = bor_solr.create_or_replace_docs([new_entity])
    assert added.status_code == HTTPStatus.OK
    time.sleep(2)  # takes up to 1 second for solr to register update

    # search new doc
    params = {'query': f'{Field.LEGAL_NAME_Q.value}:{name}', 'fields': bor_solr.entity_fields + ['identifier']}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 1
    assert docs[0][Field.LEGAL_NAME.value] == name
    assert docs[0][Field.IDENTIFIER.value]

    # delete doc
    deleted = bor_solr.delete_docs([docs[0][Field.IDENTIFIER.value]])
    assert deleted.status_code == HTTPStatus.OK
    time.sleep(1)  # takes up to 1 second for solr to register update

    # test search returns nothing
    params = {'query': f'{Field.LEGAL_NAME_Q.value}:{name}', 'fields': bor_solr.entity_fields}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 0

    # add multiple
    name1='test1'
    name2='test2'
    entity_1 = factory_entity_default(name=name1)
    new_entities = [entity_1, factory_entity_default(name=name2, entity_type='BUSINESS')]
    added = bor_solr.create_or_replace_docs(new_entities)
    assert added.status_code == HTTPStatus.OK
    time.sleep(2)  # takes up to 1 second for solr to register update

    # search new docs
    params = {'query': f'{Field.LEGAL_NAME_SINGLE_Q.value}:test', 'fields': bor_solr.entity_fields + ['identifier']}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 2
    assert docs[0][Field.LEGAL_NAME.value] in [name1, name2]
    assert docs[0][Field.IDENTIFIER.value]
    assert docs[1][Field.LEGAL_NAME.value] in [name1, name2]
    assert docs[1][Field.IDENTIFIER.value]

    # replace entity_1
    new_name = 'bla'
    updated_entity = create_entity(name=new_name)
    # verify identifier is the same
    assert updated_entity.identifier == entity_1.identifier
    replaced = bor_solr.create_or_replace_docs([updated_entity])
    assert replaced.status_code == HTTPStatus.OK
    time.sleep(2)

    # search entity_1 -- should not be there
    params = {'query': f'{Field.LEGAL_NAME_SINGLE_Q.value}:{entity_1.legalName}', 'fields': bor_solr.entity_fields + ['identifier']}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 0

    # search updated_entity -- should be there
    params = {'query': f'{Field.LEGAL_NAME_SINGLE_Q.value}:{updated_entity.legalName}', 'fields': bor_solr.entity_fields + ['identifier']}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 1

    # assert delete 1
    deleted = bor_solr.delete_docs([updated_entity.identifier])
    assert deleted.status_code == HTTPStatus.OK
    time.sleep(1)  # takes up to 1 second for solr to register update

    # test search returns the other one only
    params = {'query': f'{Field.LEGAL_NAME_Q.value}:*', 'fields': bor_solr.entity_fields + ['identifier']}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 1
    assert docs[0][Field.IDENTIFIER.value] != updated_entity.identifier

    # add back in for next test
    added = bor_solr.create_or_replace_docs([updated_entity])
    assert added.status_code == HTTPStatus.OK

    # assert delete all
    bor_solr.delete_all_docs()
    time.sleep(1)
    params = {'query': '*:*', 'fields': bor_solr.entity_fields}
    resp = bor_solr.query(params, 0, 10)
    docs = resp['response']['docs']
    assert len(docs) == 0


@pytest.mark.parametrize('test_name,env_start_weekday,env_start_day,env_start_time,env_length,expected', [
    ('test_nothing_set', '', '', '', '', False),
    ('test_weekday_time_no_length', datetime.utcnow().weekday(), '', datetime.utcnow(), 0, False),
    ('test_weekday_time_true', datetime.utcnow().weekday(), '', datetime.utcnow(), 5, True),
    ('test_day_time_no_length', '', datetime.utcnow().strftime('%d'), datetime.utcnow(), 0, False),
    ('test_day_time_true', '', datetime.utcnow().strftime('%d'), datetime.utcnow(), 5, True),
    ('test_weekday_length_not_enough', datetime.utcnow().weekday(), '', datetime.utcnow() - timedelta(minutes=5), 4, False),
    ('test_day_length_not_enough', '', datetime.utcnow().strftime('%d'), datetime.utcnow() - timedelta(minutes=5), 4, False),
])
def test_is_reindexing(app, test_name, env_start_weekday, env_start_day, env_start_time, env_length, expected):
    """Assert the _is_reindexing function works as expected."""
    if env_start_time:
        env_start_time = f'{env_start_time.hour:02}:{env_start_time.minute:02}:{env_start_time.second:02}+0000'

    app.config.update(SOLR_REINDEX_WEEKDAY=env_start_weekday)
    app.config.update(SOLR_REINDEX_DAY=env_start_day)
    app.config.update(SOLR_REINDEX_START_TIME=env_start_time)
    app.config.update(SOLR_REINDEX_LENGTH=env_length)

    bor_solr.init_app(app)

    assert bor_solr.is_reindexing() == expected


@pytest.mark.parametrize('test_name,method,params,json_data,xml_data', [
    ('test_GET_basic', 'GET', None, None, None),
    ('test_GET_params', 'GET', {'param1': 'la', 'param2': 'blip'}, None, None),
    ('test_POST_json', 'POST', None, {'test': {'json': 'is fun'}}, None),
    ('test_POST_xml', 'POST', None, None, '<delete><query>test:test</query></delete>'),
])
def test_call_solr(app, session, test_name, method, params, json_data, xml_data):
    """Assert that the call solr method creates the desired request."""
    query = '{url}/{core}/test'
    solr_url = app.config.get('SOLR_SVC_URL')
    expected_url = query.format(url=solr_url, core='bor')

    with requests_mock.mock() as m:
        if method == 'GET':
            m.get(expected_url)
        else:
            m.post(expected_url)
        
        bor_solr.call_solr(method, query, params, json_data, xml_data)
        
        # check call to solr mock
        assert m.called == True
        assert m.call_count == 1
        assert m.request_history[0].method == method
        assert expected_url in m.request_history[0].url
        if params:
            param_str = '&'.join([f'{x}={params[x]}' for x in params])
            assert param_str in m.request_history[0].url
        if json_data:
            assert m.request_history[0].json() == json_data
        elif xml_data:
            assert m.request_history[0].text == xml_data
