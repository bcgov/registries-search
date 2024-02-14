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
"""Tests to ensure that the Entity Role Solr Doc works as expected."""
from dataclasses import asdict

import pytest

from bor_api.services.bor_solr.fields import EntityRoleField
from bor_api.services.bor_solr.doc_models import DateRange, EntityRole


@pytest.mark.parametrize('test_name,rel_e_type,rel_identifier,rel_l_type,rel_name,rel_state,dates,role_type,rel_bn', [
    ('test_1', 'BUSINESS', 'BC1234567', 'BEN', 'Test Business', 'ACTIVE',
     [DateRange('2012-11-13T20:20:20Z', '2015-11-13T20:20:20Z'),DateRange('2022-11-13T20:20:20Z', None)],
     'DIRECTOR','123456789BC0001'),
])
def test_entity_role_doc(test_name, rel_e_type, rel_identifier, rel_l_type,
                     rel_name, rel_state, dates, role_type, rel_bn):
    """Assert the Entity Role solr doc class works as expected."""
    entity_role = EntityRole(
        relatedEntityType=rel_e_type,
        relatedIdentifier=rel_identifier,
        relatedLegalType=rel_l_type,
        relatedName=rel_name,
        relatedState=rel_state,
        roleDates=dates,
        roleType=role_type,
    )
    assert entity_role
    entity_role.relatedBN = rel_bn

    json = asdict(entity_role)
    assert json
    assert json.get(EntityRoleField.RELATED_ENTITY_TYPE.value) == rel_e_type
    assert json.get(EntityRoleField.RELATED_IDENTIFIER.value) == rel_identifier
    assert json.get(EntityRoleField.RELATED_LEGAL_TYPE.value) == rel_l_type
    assert json.get(EntityRoleField.RELATED_NAME.value) == rel_name
    assert json.get(EntityRoleField.RELATED_STATE.value) == rel_state
    assert json.get(EntityRoleField.ROLE_TYPE.value) == role_type
    assert json.get(EntityRoleField.RELATED_BN.value) == rel_bn

    role_dates = json.get(EntityRoleField.ROLE_DATES.value)
    assert len(role_dates) == len(dates)

    for role_date in role_dates:
        assert 'start' in role_date
        assert 'end' in role_date



@pytest.mark.parametrize('test_name,rel_e_type,rel_identifier,rel_l_type,rel_name,rel_state,dates,role_type', [
    ('test_1', 'BUSINESS', 'BC1234567', 'BEN', 'Test Business', 'ACTIVE',
     [DateRange('2012-11-13T20:20:20Z', '2015-11-13T20:20:20Z'), DateRange('2022-11-13T20:20:20Z', None)],
     'DIRECTOR'),
])
def test_entity_role_doc_invalid(test_name, rel_e_type, rel_identifier, rel_l_type,
                     rel_name, rel_state, dates, role_type):
    """Assert the Entity Role solr doc does not initialize when required fields are missing."""
    # relatedEntityType missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedIdentifier=rel_identifier,
            relatedLegalType=rel_l_type,
            relatedName=rel_name,
            relatedState=rel_state,
            roleDates=dates,
            roleType=role_type
        )
    # relatedIdentifier missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedLegalType=rel_l_type,
            relatedName=rel_name,
            relatedState=rel_state,
            roleDates=dates,
            roleType=role_type
        )
    # relatedLegalType missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedIdentifier=rel_identifier,
            relatedName=rel_name,
            relatedState=rel_state,
            roleDates=dates,
            roleType=role_type
        )
    # relatedName missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedIdentifier=rel_identifier,
            relatedLegalType=rel_l_type,
            relatedState=rel_state,
            roleDates=dates,
            roleType=role_type
        )
    # relatedState missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedIdentifier=rel_identifier,
            relatedLegalType=rel_l_type,
            relatedName=rel_name,
            roleDates=dates,
            roleType=role_type
        )
    # roleDates missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedIdentifier=rel_identifier,
            relatedLegalType=rel_l_type,
            relatedName=rel_name,
            relatedState=rel_state,
            roleType=role_type
        )
    # roleType missing
    with pytest.raises(TypeError):
        EntityRole(
            relatedEntityType=rel_e_type,
            relatedIdentifier=rel_identifier,
            relatedLegalType=rel_l_type,
            relatedName=rel_name,
            relatedState=rel_state,
            roleDates=dates
        )
