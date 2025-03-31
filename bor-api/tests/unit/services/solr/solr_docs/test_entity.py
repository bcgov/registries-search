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
"""Tests to ensure that the Entity Solr Doc works as expected."""
from dataclasses import asdict

import pytest

from bor_api.services.bor_solr.fields import EntityField
from bor_api.services.bor_solr.doc_models import Entity

from tests.unit.test_utils.solr_helpers import factory_entity_default


@pytest.mark.parametrize(
    "test_name,name,entity_type", [("test_person", "Tester", "PERSON"), ("test_business", "Test Inc.", "BUSINESS")]
)
def test_entity_doc(test_name, name, entity_type):
    """Assert the Entity solr doc class works as expected."""
    entity = factory_entity_default(name=name, entity_type=entity_type)
    assert entity
    if entity_type == "PERSON":
        assert entity.identifier == None
    else:
        assert entity.identifier == entity.identifier

    json = asdict(entity)
    assert json
    assert json.get(EntityField.LEGAL_NAME.value) == name
    assert json.get(EntityField.ENTITY_TYPE.value) == entity_type
    assert json.get(EntityField.ENTITY_ADDRESSES.value)
    assert json.get(EntityField.ROLES.value)

    if entity_type == "BUSINESS":
        assert json.get(EntityField.IDENTIFIER.value)
        assert json.get(EntityField.LEGAL_TYPE.value)
        assert json.get(EntityField.STATE.value)


def test_entity_doc_invalid():
    """Assert the Entity solr doc class does not initialize when required fields are missing."""
    # assert minimum valid case
    assert Entity(entityAddresses=[], entityType="PERSON", legalName="name", id="LEAR123456")
    # legal name missing
    with pytest.raises(TypeError):
        Entity(entityAddresses=[], entityType="PERSON", id="1")
    # entity type missing
    with pytest.raises(TypeError):
        Entity(entityAddresses=[], legalName="name", id="1")
    # entity id missing
    with pytest.raises(TypeError):
        Entity(entityAddresses=[], entityType="PERSON", legalName="name")
