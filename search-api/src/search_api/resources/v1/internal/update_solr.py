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
from http import HTTPStatus
from typing import Dict

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.exceptions import SolrException
from search_api.services import solr
from search_api.services.solr import SolrDoc
from search_api.services.validator import RequestValidator


bp = Blueprint('UPDATE', __name__, url_prefix='/solr')  # pylint: disable=invalid-name


@bp.put('/update')
@cross_origin(origin='*')
def update_solr():
    """Add/Update business in solr."""
    try:
        request_json = request.json
        errors = RequestValidator.validate_solr_update_request(request_json)
        if errors:
            return resource_utils.bad_request_response(errors)

        solr_doc = _prepare_data(request_json)

        response = solr.create_or_replace_docs([solr_doc])
        return jsonify(response.json()), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


def _prepare_data(request_json: Dict) -> SolrDoc:
    """Return the SolrDoc for the json data."""
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
    prepped_data = {
        'identifier': business_info['identifier'],
        'name': business_info['legalName'],
        'legaltype': business_info['legalType'],
        'status': business_info['state'],
        'bn': business_info.get('taxId')
    }
    if party_info:
        party_list = []
        # add party doc to base doc
        for party in party_info:
            party_doc = {
                'parentBN': business_info.get('taxId'),
                'parentLegalType': business_info['legalType'],
                'parentName': business_info['legalName'],
                'parentStatus': business_info['state'],
                'partyName': get_party_name(party['officer']),
                'partyRoles': [x['roleType'].lower() for x in party['roles']],
                'partyType': party['officer']['partyType']
            }
            party_list.append(party_doc)

        if party_list:
            prepped_data['parties'] = party_list
    return SolrDoc(prepped_data)
