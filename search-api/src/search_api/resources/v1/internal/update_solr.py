# Copyright © 2022 Province of British Columbia
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
from http import HTTPStatus
from typing import Dict

from datetime import datetime, timedelta
from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.enums import SolrDocEventType
from search_api.exceptions import SolrException
from search_api.models import SolrDoc, User
from search_api.request_handlers import update_search_solr
from search_api.services import is_system
from search_api.services.solr.solr_docs import BusinessDoc, PartyDoc
from search_api.services.validator import RequestValidator
from search_api.utils.auth import jwt


bp = Blueprint('UPDATE', __name__, url_prefix='/solr/update')  # pylint: disable=invalid-name


@bp.put('')
@cross_origin(origin='*')
@jwt.requires_auth
def update_solr():
    """Add/Update business in solr."""
    try:
        if not is_system(jwt):
            # system only endpoint
            return jsonify({'message': 'Not authorized to update a solr doc.'}), HTTPStatus.UNAUTHORIZED

        request_json = request.json
        errors = RequestValidator.validate_solr_update_request(request_json)
        if errors:
            return resource_utils.bad_request_response(errors)

        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        solr_doc = _prepare_data(request_json)
        # commit so that other flows will take this record as most recent for this identifier
        solr_doc_update = SolrDoc(doc=asdict(solr_doc), identifier=solr_doc.identifier, _submitter_id=user.id).save()

        update_search_solr(solr_doc_update.identifier, SolrDocEventType.UPDATE)
        return jsonify({'message': 'Update successful'}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


@bp.post('/resync')
@cross_origin(origin='*')
def resync_solr():
    """Resync solr docs from the given date."""
    try:
        request_json = request.json
        from_datetime = datetime.utcnow()
        minutes_offset = request_json.get('minutesOffset', None)
        identifiers_to_resync = request_json.get('identifiers', None)
        if not minutes_offset and not identifiers_to_resync:
            return resource_utils.bad_request_response('Missing required field "minutesOffset" or "identifiers".')
        try:
            minutes_offset = float(minutes_offset)
        except:  # pylint: disable=bare-except # noqa F841;
            if not identifiers_to_resync:
                return resource_utils.bad_request_response(
                    'Invalid value for field "minutesOffset". Expecting a number.')

        if minutes_offset:
            # get all updates since the from_datetime
            resync_date = from_datetime - timedelta(minutes=minutes_offset)
            identifiers_to_resync = SolrDoc.get_updated_identifiers_after_date(resync_date)

        current_app.logger.debug(f'Resyncing: {identifiers_to_resync}')
        # update docs
        for identifier in identifiers_to_resync:
            try:
                update_search_solr(identifier, SolrDocEventType.RESYNC)
            except SolrException:
                # log error so that ops can resync the business without redoing the whole batch
                current_app.logger.error('Failed to resync %s', identifier)

        return jsonify({'message': 'Resync successful.'}), HTTPStatus.CREATED

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


def _prepare_data(request_json: Dict) -> BusinessDoc:
    """Return the solr doc for the json data."""
    def needs_bc_prefix(identifier: str, legal_type: str) -> bool:
        """Return if the identifier should have the BC prefix or not."""
        numbers_only_rgx = r'^[0-9]+$'
        # TODO: get legal types from shared enum
        return legal_type in ['BEN', 'BC', 'CC', 'ULC'] and re.search(numbers_only_rgx, identifier)

    def get_party_name(officer: Dict[str, str]) -> str:
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

    business_info = request_json.get('business')
    party_info = request_json.get('parties')

    # add new base doc
    identifier = business_info['identifier']
    legal_type = business_info['legalType']
    business_doc = BusinessDoc(
        bn=business_info.get('taxId'),
        identifier=f'BC{identifier}' if needs_bc_prefix(identifier, legal_type) else identifier,
        legalType=legal_type,
        name=business_info['legalName'],
        status=business_info['state'])

    if party_info:
        party_list = []
        # add party doc to base doc
        for party in party_info:
            party_doc = PartyDoc(
                parentBN=business_info.get('taxId'),
                parentLegalType=business_info['legalType'],
                parentName=business_info['legalName'],
                parentStatus=business_info['state'],
                partyName=get_party_name(party['officer']),
                partyRoles=[x['roleType'].lower() for x in party['roles']],
                partyType=party['officer']['partyType']
            )
            party_list.append(party_doc)

        if party_list:
            business_doc.parties = party_list
    # add doc to updates table
    return business_doc
