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
"""API endpoint for updating/adding business record in solr."""
import re
from dataclasses import asdict
from datetime import datetime, timedelta
from http import HTTPStatus
from time import sleep

from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

from bor_api.enums import SolrDocEventType
from bor_api.exceptions import SolrException, bad_request_response, exception_response
from bor_api.models import SolrDoc, User
from bor_api.services import SYSTEM_ROLE, jwt
from bor_api.services.solr.bor_solr_updates import update_bor_solr
from bor_api.services.solr.solr_docs import Address, DateRange, Entity, EntityRole
from bor_api.utils.request_validators import validate_solr_update_request


bp = Blueprint('UPDATE', __name__, url_prefix='/solr/update')  # pylint: disable=invalid-name


@bp.put('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def update_solr():
    """Add/Update business in solr."""
    try:
        request_json: dict = request.json
        errors = validate_solr_update_request(request_json)
        if errors:
            return bad_request_response('Invalid payload.', errors)

        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        entities = _parse_entities(request_json)
        for entity in entities:
            # commit each entity. Ensures other flows (i.e. resync) will use the current data
            SolrDoc(doc=asdict(entity), identifier=entity.identifier, _submitter_id=user.id).save()
            # trigger solr update
            update_bor_solr(entity.identifier, SolrDocEventType.UPDATE)

        return jsonify({'message': 'Update successful'}), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)


@bp.post('/resync')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def resync_solr():
    """Resync solr docs from the given date."""
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
            identifiers_to_resync = SolrDoc.get_updated_identifiers_after_date(resync_date)

        current_app.logger.debug(f'Resyncing: {identifiers_to_resync}')
        # update docs
        for identifier in identifiers_to_resync:
            try:
                update_bor_solr(identifier, SolrDocEventType.RESYNC)
            except SolrException:
                # log error so that ops can resync the business without redoing the whole batch
                current_app.logger.error('Failed to resync %s', identifier)
            # pause for 1 second so that solr doesn't get overloaded on large batches
            sleep(1)

        return jsonify({'message': 'Resync successful.'}), HTTPStatus.CREATED

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
        return Address(addressType=address_info.get('addressType', ''),
                       addressCity=address_info.get('addressCity', ''),
                       addressCountry=address_info.get('addressCountry', ''),
                       addressRegion=address_info.get('addressRegion', ''),
                       postalCode=address_info.get('postalCode', ''),
                       streetAddress=address_info.get('streetAddress', ''))

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

    address_info = request_json['businessAddresses'].get('registeredOffice', None)
    if not address_info:
        address_info = request_json['businessAddresses']['businessOffice']
    business_info = request_json['business']
    party_info = request_json.get('parties', [])

    # add new business doc
    business_address = get_delivery_address(address_info['deliveryAddress'])
    identifier = business_info['identifier']
    if needs_bc_prefix(identifier, business_info['legalType']):
        # set prefix to BC
        identifier = f'BC{identifier}'
    business = Entity(entityAddresses=[business_address],
                      entityType='BUSINESS',
                      identifier=identifier,
                      legalName=business_info['legalName'],
                      bn=business_info.get('taxId'),
                      legalType=business_info['legalType'],
                      state=business_info['state'])
    entities.append(business)
    for party in party_info:
        address = get_delivery_address(party['deliveryAddress'])
        name = get_party_name(party['officer'])

        # NOTE: business parties are ignored for now -- waiting for LEAR update
        identifier = f"{party['source']}{party['officer']['id']}"
        # add a doc for each role
        for role in party.get('roles'):
            entities.append(Entity(entityAddresses=[address],
                                   entityType='PERSON',
                                   identifier=identifier,
                                   legalName=name,
                                   roles=[EntityRole(relatedEntityType='BUSINESS',
                                                     relatedIdentifier=business.identifier,
                                                     relatedLegalType=business.legalType,
                                                     relatedName=business.legalName,
                                                     relatedState=business.state,
                                                     roleDates=[DateRange(start=role['appointmentDate'],
                                                                          end=role.get('cessationDate', None))],
                                                     roleType=role['roleType'],
                                                     relatedBN=business.bn)]))

    return entities
