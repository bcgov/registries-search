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
"""Tests to assure the Solr Services."""
from bor_api.services.bor_solr.doc_models import Address, DateRange, Entity, EntityRole


def create_entity(name: str,
                  alternate_name: str = None,
                  addresses: list[Address] = None,
                  bn: str = None,
                  tax_number: str = None,
                  email: str = None,
                  entity_type: str = 'PERSON',
                  entity_id: str = 'LEAR1234567',
                  legal_type: str = None,
                  nationalities: list[str] = None,
                  roles: list[EntityRole] = None,
                  state: str = None) -> Entity:
    """Create a base entity doc."""
    return Entity(
        alternateName=alternate_name,
        bn=bn,
        taxNumber=tax_number,
        email=email,
        entityAddresses=addresses,
        entityType=entity_type,
        id=entity_id,
        identifier=None if entity_type == 'PERSON' else entity_id,
        legalName=name,
        legalType=legal_type,
        nationalities=nationalities,
        roles=roles,
        state=state
    )

def factory_entity_default(name: str = 'Entity Default', entity_type: str = 'PERSON'):
    """Create a default Entity with addresses and roles."""
    address = Address(
        addressType='DELIVERY',
        addressCity='City',
        addressCountry='Country',
        addressRegion='Region',
        postalCode='V8P 2T3',
        streetAddress='Street'
    )
    role = EntityRole(
        id='LEAR1234567/roles0',
        relatedEmail='default@email.com',
        relatedEntityType='BUSINESS',
        relatedIdentifier='BC1234567',
        relatedLegalType='BEN',
        relatedName='Related Name',
        relatedState='ACTIVE',
        roleDates=[DateRange(start='2021-03-05T21:01:45Z', end=None)],
        roleType='DIRECTOR',
    )
    if entity_type == 'BUSINESS':
        role.roleType = 'INCORPORATOR'
        return create_entity(
            name=name,
            email='test@email.com',
            entity_type=entity_type,
            addresses=[address],
            roles=[role],
            entity_id='BC0234567',
            legal_type='BEN',
            state='ACTIVE'
        )
    
    return create_entity(name=name, entity_type=entity_type, addresses=[address], roles=[role])
