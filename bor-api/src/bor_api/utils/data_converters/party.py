# Copyright © 2024 Province of British Columbia
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
"""Data conversion methods for party."""
from bor_api.services.bor_solr.doc_models import DateRange, Entity, EntityRole, Interest

from .address import get_btr_address, get_lear_address


def get_lear_party_name(officer: dict[str, str]) -> str:
    """Return the parsed name of the party from LEAR party officer format."""
    if officer.get('organizationName'):
        return officer['organizationName'].strip()
    person_name = ''
    if officer.get('firstName'):
        person_name += officer['firstName'].strip()
    if officer.get('middleInitial'):
        person_name += ' ' + officer['middleInitial'].strip()
    if officer.get('lastName'):
        person_name += ' ' + officer['lastName'].strip()
    return person_name.strip()


def get_lear_party(party_info: dict, business: Entity) -> list[Entity]:
    """Return the party from LEAR format as a list of Entity docs (1 per role)."""
    address = None
    if delivery_address_info := party_info.get('deliveryAddress'):
        address = get_lear_address(delivery_address_info, 'DELIVERY')

    name = get_lear_party_name(party_info['officer'])
    # NOTE: business parties are being ignored for now
    entity_type = 'PERSON' if party_info['officer']['partyType'] == 'person' else 'BUSINESS'

    base_party_id = f"{party_info['source']}{party_info['officer']['id']}"
    # add a doc for each role
    entities = []
    # NOTE: if the id is not unique then multiple roles will be added under the same entity in solr
    for count, role in enumerate(party_info.get('roles', [])):
        entity_id = f"{base_party_id}{business.identifier}{role['roleType'].replace(' ', '_')}{count}".upper()
        entities.append(Entity(entityAddresses=[address] if address else None,
                               entityType=entity_type,
                               id=entity_id,
                               legalName=name,
                               roles=[EntityRole(id=entity_id + '/roles0',
                                                 relatedEntityType='BUSINESS',
                                                 relatedIdentifier=business.identifier,
                                                 relatedLegalType=business.legalType,
                                                 relatedName=business.legalName,
                                                 relatedState=business.state,
                                                 roleDates=[DateRange(start=role['appointmentDate'],
                                                                      end=role.get('cessationDate', None))],
                                                 roleType=role['roleType'],
                                                 relatedBN=business.bn,
                                                 relatedEmail=business.email)]))

    return entities


def get_btr_owner(owner_info: dict, business: Entity):
    """Return the owner info as an Entity."""
    interests = []
    for interest_info in owner_info.get('interests', []):
        interests.append(Interest(details=interest_info.get('details'),
                                  directOrIndirect=interest_info.get('directOrIndirect') or None,
                                  interestType=interest_info.get('type') or None,
                                  sharesExact=interest_info.get('share', {}).get('exact') or None,
                                  sharesMax=interest_info.get('share', {}).get('maximum') or None,
                                  sharesMin=interest_info.get('share', {}).get('minimum') or None))

    party: dict = owner_info['interestedParty']
    names_dict = {}
    for name in party.get('names'):
        if name_type := name.get('type'):  # expecting this to be 'individual' or 'alternative'
            names_dict[name_type] = name.get('fullName')

    tax_number = None
    for identifier in party.get('identifiers', []):
        # TODO: support other tax numbers?
        if identifier['scheme'] == 'CAN-TAXID':
            tax_number = identifier['id']

    address = None
    if (addresses := party.get('addresses')) and len(addresses) > 0:
        address = get_btr_address(addresses[0], 'RESIDENCE')

    entity_id = party['describedByPersonStatement']
    role_id = entity_id + business.identifier + 'SIGNIFICANT_INDIVIDUAL'
    return Entity(id=entity_id,
                  entityAddresses=[address] if address else None,
                  entityType='PERSON',
                  externalInfluence=party.get('externalInfluence'),
                  legalName=names_dict.get('individual'),
                  alternateName=names_dict.get('alternative'),
                  birthDate=party.get('birthDate'),
                  isPermanentResident=party.get('isPermanentResidentCa'),
                  nationalities=[country.get('code') for country in party.get('nationalities', [])],
                  taxNumber=tax_number,
                  taxResidencies=[country.get('code') for country in party.get('taxResidencies', [])],
                  email=party.get('email'),
                  roles=[EntityRole(id=role_id,
                                    relatedEntityType='BUSINESS',
                                    relatedIdentifier=business.identifier,
                                    relatedLegalType=business.legalType or 'N/A',
                                    relatedName=business.legalName,
                                    relatedState=business.state or 'N/A',
                                    roleDates=[DateRange(start=party['statementDate'],
                                                         end=party.get('statementEndDate', None))],
                                    roleType='SIGNIFICANT INDIVIDUAL',
                                    relatedBN=business.bn,
                                    relatedEmail=business.email,
                                    relatedInterests=interests)])
