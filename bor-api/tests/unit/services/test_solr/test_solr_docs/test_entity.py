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

from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.solr_docs import Entity

from tests.unit.utils.solr_helpers import factory_entity_default


@pytest.mark.parametrize('test_name,name,entity_type', [
    ('test_person', 'Tester', 'PERSON'),
    ('test_business', 'Test Inc.', 'BUSINESS')
])
def test_entity_doc(test_name, name, entity_type):
    """Assert the Entity solr doc class works as expected."""
    entity = factory_entity_default(name=name, entity_type=entity_type)
    assert entity
    if entity_type == 'PERSON':
        assert entity.identifier_q == None
    else:
        assert entity.identifier_q == entity.identifier

    json = asdict(entity)
    assert json
    assert json.get(Field.LEGAL_NAME.value) == name
    assert json.get(Field.ENTITY_TYPE.value) == entity_type
    assert json.get(Field.ENTITY_ADDRESSES.value)
    assert json.get(Field.ROLES.value)
    
    if entity_type == 'BUSINESS':
        assert json.get(Field.IDENTIFIER.value)
        assert json.get(Field.LEGAL_TYPE.value)
        assert json.get(Field.STATE.value)


def test_entity_doc_invalid():
    """Assert the Entity solr doc class does not initialize when required fields are missing."""
    # assert minimum valid case
    assert Entity(entityAddresses=[], entityType='PERSON', legalName='name', identifier='LEAR123456')
    # legal name missing
    with pytest.raises(TypeError):
        Entity(entityType='PERSON')
    # entity type missing
    with pytest.raises(TypeError):
        Entity(legalName='name')
