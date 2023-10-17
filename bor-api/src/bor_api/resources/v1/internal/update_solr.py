# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoint for updating/adding entity records in solr."""
import re
from dataclasses import asdict
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

from bor_api.enums import SolrDocEventStatus, SolrDocEventType, SolrSynonymType
from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import SolrDoc, SolrDocEvent, SolrSynonymList, User
from bor_api.services import SYSTEM_ROLE, bor_solr, jwt
from bor_api.services.solr.bor_solr_updates import resync_bor_solr, update_bor_solr
from bor_api.services.solr.solr_docs import Address, DateRange, Entity, EntityRole
from bor_api.services.solr.utils import get_synonyms
from bor_api.utils.request_validators import validate_solr_update_request


bp = Blueprint('UPDATE', __name__, url_prefix='/solr/update')  # pylint: disable=invalid-name


@bp.put('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def update_entity():
    """Add/Update entity in BOR."""
    try:
        request_json: dict = request.json
        errors = validate_solr_update_request(request_json)
        if errors:
            return bad_request_response('Invalid payload.', errors)

        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        entities = _parse_entities(request_json)
        for entity in entities:
            # commit each entity. Ensures other flows (i.e. resync) will use the current data
            solr_doc = SolrDoc(doc=asdict(entity), entity_id=entity.id, _submitter_id=user.id).save()
            SolrDocEvent(event_type=SolrDocEventType.UPDATE, solr_doc_id=solr_doc.id).save()
            # SOLR update will be triggered by job (does a frequent bulk update to solr)

        return jsonify({'message': 'Update accepted.'}), HTTPStatus.ACCEPTED

    except Exception as exception:  # noqa: B902
        return exception_response(exception)


@bp.put('/synonyms')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def update_synonyms():
    """Add/trigger update to synonyms lists."""
    try:
        synonyms = request.json
        if not synonyms:
            synonyms = get_synonyms()

        errors = [key for key in synonyms if key not in [SolrSynonymType.ADDRESS, SolrSynonymType.NAME]]
        if errors:
            return bad_request_response(f"Invalid synonym type(s): {','.join(errors)}")

        # update solr synonym file
        if SolrSynonymType.ADDRESS in synonyms:
            bor_solr.create_or_update_synonyms(SolrSynonymType.ADDRESS, synonyms[SolrSynonymType.ADDRESS])
        if SolrSynonymType.NAME in synonyms:
            bor_solr.create_or_update_synonyms(SolrSynonymType.NAME, synonyms[SolrSynonymType.NAME])
        # reload the solr core (so it will register any changes)
        bor_solr.reload_core()
        # update db synonym lists
        for synonym_type in synonyms:
            SolrSynonymList.create_or_replace_all(synonyms=synonyms[synonym_type], synonym_type=synonym_type)

        return jsonify({'message': 'Update successful'}), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)


@bp.post('/resync')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def resync_solr():
    """Resync solr docs from the given date or identifiers given."""
    try:
        request_json = request.json
        from_datetime = datetime.utcnow()
        minutes_offset = request_json.get('minutesOffset', None)
        identifiers_to_resync = request_json.get('identifiers', None)
        if not minutes_offset and not identifiers_to_resync:
            return bad_request_response('Missing required field "minutesOffset" or "identifiers".')
        try:
            minutes_offset = float(minutes_offset)
        except:  # pylint: disable=bare-except # noqa F841;
            if not identifiers_to_resync:
                return bad_request_response('Invalid value for field "minutesOffset". Expecting a number.')

        if minutes_offset:
            # get all updates since the from_datetime
            resync_date = from_datetime - timedelta(minutes=minutes_offset)
            identifiers_to_resync = SolrDoc.get_updated_entity_ids_after_date(resync_date)

        if identifiers_to_resync:
            current_app.logger.debug(f'Resyncing: {identifiers_to_resync}')
            resync_bor_solr(identifiers_to_resync)
        else:
            current_app.logger.debug('No records to resync.')

        return jsonify({'message': 'Resync successful.'}), HTTPStatus.CREATED

    except Exception as exception:  # noqa: B902
        return exception_response(exception)


@bp.get('/sync')
@cross_origin(origin='*')
def sync_solr():
    """Sync docs in the DB that haven't been applied to SOLR yet."""
    try:
        pending_update_events = SolrDocEvent.get_events_by_status(statuses=[SolrDocEventStatus.PENDING,
                                                                            SolrDocEventStatus.ERROR],
                                                                  event_type=SolrDocEventType.UPDATE)

        pending_update_events = pending_update_events[:current_app.config.get('MAX_BATCH_UPDATE_NUM')]
        identifiers_to_sync = [(SolrDoc.get_by_id(event.solr_doc_id)).entity_id for event in pending_update_events]
        # only update up to a certain amount at a time

        current_app.logger.debug(f'Syncing: {identifiers_to_sync}')
        if identifiers_to_sync:
            update_bor_solr(identifiers_to_sync, pending_update_events)

        return jsonify({'message': 'Sync successful.'}), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)


def _parse_entities(request_json: dict) -> list[Entity]:
    """Return the entity docs for the given data."""
    def needs_bc_prefix(identifier: str, legal_type: str) -> bool:
        """Return if the identifier should have the BC prefix or not."""
        numbers_only_rgx = r'^[0-9]+$'
        # TODO: get legal types from shared enum
        return legal_type in ['BEN', 'BC', 'CC', 'ULC'] and re.search(numbers_only_rgx, identifier)

    def get_delivery_address(address_info: dict) -> Address:
        """Return the delivery address as an Address doc."""
        return Address(addressType=address_info.get('addressType', 'DELIVERY') or 'DELIVERY',
                       addressCity=address_info.get('addressCity', '') or '',
                       addressCountry=address_info.get('addressCountry', '') or '',
                       addressRegion=address_info.get('addressRegion', '') or '',
                       postalCode=address_info.get('postalCode', '') or '',
                       streetAddress=address_info.get('streetAddress', '') or '')

    def get_party_name(officer: dict[str, str]) -> str:
        """Return the parsed name of the party in the given doc info."""
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

    entities = []

    address_info = request_json.get('businessAddresses', {}).get('registeredOffice', None)
    if not address_info:
        address_info = request_json.get('businessAddresses', {}).get('businessOffice', None)
    business_info = request_json['business']
    party_info = request_json.get('parties', [])

    # add new business doc
    business_address = get_delivery_address(address_info['deliveryAddress']) if address_info else None
    identifier = business_info['identifier']
    if needs_bc_prefix(identifier, business_info['legalType']):
        # set prefix to BC
        identifier = f'BC{identifier}'
    business = Entity(entityAddresses=[business_address] if business_address else [],
                      entityType='BUSINESS',
                      id=identifier,
                      identifier=identifier,
                      legalName=business_info['legalName'],
                      legalType=business_info['legalType'],
                      state=business_info['state'],
                      bn=business_info.get('taxId'),
                      email=business_info.get('email'))
    entities.append(business)
    for party in party_info:
        address = get_delivery_address(party['deliveryAddress']) if party.get('deliveryAddress') else None
        name = get_party_name(party['officer'])
        entity_type = 'PERSON' if party['officer']['partyType'] == 'person' else 'BUSINESS'

        # NOTE: business parties are ignored for now -- waiting for LEAR update
        party_id = f"{party['source']}{party['officer']['id']}"
        # add a doc for each role
        for role in party.get('roles'):
            entities.append(Entity(entityAddresses=[address] if address else None,
                                   entityType=entity_type,
                                   id=f"{party_id}{business.identifier}{role['roleType'].replace(' ', '_')}".upper(),
                                   legalName=name,
                                   roles=[EntityRole(relatedEntityType='BUSINESS',
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
