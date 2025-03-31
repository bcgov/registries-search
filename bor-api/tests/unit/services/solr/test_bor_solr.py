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

from bor_api.services import solr
from bor_api.services.bor_solr.fields import EntityField, EntityRoleField
from bor_api.services.bor_solr.utils.query_builders import PRE_CHILD_FILTER_CLAUSE

from tests import integration_solr
from tests.unit.test_utils import TEST_PERSONS, create_entity, factory_entity_default


@integration_solr
def test_create_update_delete_query(app):
    """Assert that solr docs can be created/updated/searched/deleted and cores can be backed up / restored."""
    # init
    solr.init_app(app)
    solr.delete_all_docs()
    time.sleep(2)
    # add new entity
    name = "test"
    new_entity = factory_entity_default(name=name)
    added = solr.create_or_replace_docs([new_entity])
    assert added.status_code == HTTPStatus.OK
    time.sleep(20)  # long wait necessary due to backup tests

    # search new doc
    params = {
        "query": f"{EntityField.LEGAL_NAME_Q.value}:{name}",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 1
    assert docs[0][EntityField.LEGAL_NAME.value] == name
    assert docs[0][EntityField.UNIQUE_KEY.value]

    # create backup
    backup = solr.replication(command="backup")
    assert backup.status_code == HTTPStatus.OK
    time.sleep(1)
    # delete doc
    deleted = solr.delete_docs([docs[0][EntityField.UNIQUE_KEY.value]])
    assert deleted.status_code == HTTPStatus.OK
    time.sleep(5)  # takes up to 1 second for solr to register update

    # test search returns nothing
    params = {"query": f"{EntityField.LEGAL_NAME_Q.value}:{name}", "fields": [EntityField.LEGAL_NAME.value]}
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 0

    # test restore
    restore = solr.replication(command="restore")
    assert restore.status_code == HTTPStatus.OK
    time.sleep(1)
    # get restore status
    restore_status = solr.replication(command="restorestatus")
    assert restore_status.status_code == HTTPStatus.OK
    assert (restore_status.json())["restorestatus"]["status"] == "success"

    # test search returns doc again
    params = {
        "query": f"{EntityField.LEGAL_NAME_Q.value}:{name}",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 1
    assert docs[0][EntityField.LEGAL_NAME.value] == name
    assert docs[0][EntityField.UNIQUE_KEY.value]

    # delete doc again
    solr.delete_all_docs()
    time.sleep(1)

    # add multiple
    name1 = "test1"
    name2 = "test2"
    entity_1 = factory_entity_default(name=name1)
    new_entities = [entity_1, factory_entity_default(name=name2, entity_type="BUSINESS")]
    added = solr.create_or_replace_docs(new_entities)
    assert added.status_code == HTTPStatus.OK
    time.sleep(2)  # takes up to 1 second for solr to register update

    # search new docs
    params = {
        "query": f"{EntityField.LEGAL_NAME_SINGLE_Q.value}:test",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 2
    assert docs[0][EntityField.LEGAL_NAME.value] in [name1, name2]
    assert docs[0][EntityField.UNIQUE_KEY.value]
    assert docs[1][EntityField.LEGAL_NAME.value] in [name1, name2]
    assert docs[1][EntityField.UNIQUE_KEY.value]

    # replace entity_1
    updated_entity = TEST_PERSONS[8]
    # Test is expecting this entity to have an email and that the email is in the info_q
    assert updated_entity.email and updated_entity.email in updated_entity.info_q
    new_name = "bla"
    updated_entity.legalName = new_name
    updated_entity.name_q = new_name
    updated_entity.id = entity_1.id
    # verify identifier is the same
    assert updated_entity.id == entity_1.id
    replaced = solr.create_or_replace_docs([updated_entity])
    assert replaced.status_code == HTTPStatus.OK
    time.sleep(2)

    # search entity_1 -- should not be there
    params = {
        "query": f"{EntityField.LEGAL_NAME_SINGLE_Q.value}:{entity_1.legalName}",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 0

    # search updated_entity -- should be there
    params = {
        "query": f"{EntityField.LEGAL_NAME_SINGLE_Q.value}:{updated_entity.legalName}",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 1

    # partial atomic update
    new_bn = "1"
    new_email = "changed@change.com"
    new_legal_type = "TST"
    new_name = "Partial atomic update test"
    new_state = "CHANGE"

    partial_update = {
        "_root_": updated_entity.id,
        "id": updated_entity.roles[0].id,
        "relatedBN": {"set": new_bn},
        "relatedEmail": {"set": new_email},
        "relatedLegalType": {"set": new_legal_type},
        "relatedName": {"set": new_name},
        "relatedState": {"set": new_state},
    }
    partial = solr.create_or_replace_docs(raw_docs=[partial_update])
    assert partial.status_code == HTTPStatus.OK
    time.sleep(2)
    # search updated entity (should still be searchable by all query fields after partial update)
    info_q_clause = f"{EntityField.INFO_Q.value}:{updated_entity.email}"
    name_q_clause = f"{EntityField.NAME_Q.value}:{updated_entity.legalName}"
    related_q_clause = (
        f"{PRE_CHILD_FILTER_CLAUSE}{EntityRoleField.RELATED_Q.value}:{updated_entity.roles[0].relatedIdentifier}"
    )

    params = {
        "query": f"{info_q_clause} AND {name_q_clause} AND {related_q_clause}",
        "fields": [
            EntityField.UNIQUE_KEY.value,
            EntityField.ROLES.value,
            EntityRoleField.RELATED_BN.value,
            EntityRoleField.RELATED_EMAIL.value,
            EntityRoleField.RELATED_LEGAL_TYPE.value,
            EntityRoleField.RELATED_NAME.value,
            EntityRoleField.RELATED_STATE.value,
            "[child]",
        ],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 1
    assert docs[0]["id"] == updated_entity.id
    for field in partial_update:
        if field not in ["_root_", "id"]:
            assert partial_update[field]["set"] == docs[0]["roles"][0][field]

    # assert delete 1
    deleted = solr.delete_docs([updated_entity.id])
    assert deleted.status_code == HTTPStatus.OK
    time.sleep(2)  # takes up to 1 second for solr to register update

    # test search returns the other one only
    params = {
        "query": f"{EntityField.LEGAL_NAME_Q.value}:*",
        "fields": [EntityField.LEGAL_NAME.value, EntityField.UNIQUE_KEY.value],
    }
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 1
    assert docs[0][EntityField.UNIQUE_KEY.value] != updated_entity.identifier

    # add back in for next test
    added = solr.create_or_replace_docs([updated_entity])
    assert added.status_code == HTTPStatus.OK

    # assert delete all
    solr.delete_all_docs()
    time.sleep(1)
    params = {"query": "*:*", "fields": [EntityField.LEGAL_NAME.value]}
    resp = solr.query(params, 0, 10)
    docs = resp["response"]["docs"]
    assert len(docs) == 0


@pytest.mark.parametrize(
    "test_name,method,params,json_data,xml_data",
    [
        ("test_GET_basic", "GET", None, None, None),
        ("test_GET_params", "GET", {"param1": "la", "param2": "blip"}, None, None),
        ("test_POST_json", "POST", None, {"test": {"json": "is fun"}}, None),
        ("test_POST_xml", "POST", None, None, "<delete><query>test:test</query></delete>"),
    ],
)
def test_call_solr(app, session, test_name, method, params, json_data, xml_data):
    """Assert that the call solr method creates the desired request."""
    query = "{url}/{core}/test"
    solr_url = app.config.get("SOLR_SVC_LEADER_URL")
    expected_url = query.format(url=solr_url, core="bor")

    with requests_mock.mock() as m:
        if method == "GET":
            m.get(expected_url)
        else:
            m.post(expected_url)

        solr.call_solr(method, query, params, json_data, xml_data)

        # check call to solr mock
        assert m.called == True
        assert m.call_count == 1
        assert m.request_history[0].method == method
        assert expected_url in m.request_history[0].url
        if params:
            param_str = "&".join([f"{x}={params[x]}" for x in params])
            assert param_str in m.request_history[0].url
        if json_data:
            assert m.request_history[0].json() == json_data
        elif xml_data:
            assert m.request_history[0].text == xml_data
