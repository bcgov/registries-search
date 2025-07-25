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
"""Exposes all of the update endpoints in Flask-Blueprint style."""
import re
from dataclasses import asdict
from http import HTTPStatus

from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.enums import SolrDocEventType
from search_api.exceptions import SolrException
from search_api.models import SolrDoc, SolrDocEvent, User
from search_api.services import SYSTEM_ROLE, entity
from search_api.services.business_solr.doc_models import BusinessDoc, PartyDoc
from search_api.services.validator import RequestValidator
from search_api.utils.auth import jwt

from .resync import bp as resync_bp
from .sync import bp as sync_bp

bp = Blueprint("UPDATE", __name__, url_prefix="/update")
bp.register_blueprint(resync_bp)
bp.register_blueprint(sync_bp)


@bp.put("")
@cross_origin(origins="*")
@jwt.requires_roles([SYSTEM_ROLE])
def update_business():
    """Add/Update business in solr."""
    try:
        request_json: dict = request.json
        errors = RequestValidator.validate_solr_update_request(request_json)
        if errors:
            return resource_utils.bad_request_response("Invalid payload.", errors)

        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        business = _parse_business(request_json)
        # commit business. Ensures other flows (i.e. resync) will use the current data
        solr_doc = SolrDoc(doc=asdict(business), identifier=business.identifier, _submitter_id=user.id).save()
        SolrDocEvent(event_type=SolrDocEventType.UPDATE, solr_doc_id=solr_doc.id).save()
        # SOLR update will be triggered by job (does a frequent bulk update to solr)

        return jsonify({"message": "Update accepted."}), HTTPStatus.ACCEPTED

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as exception:
        return resource_utils.default_exception_response(exception)


def _parse_business(request_json: dict) -> BusinessDoc:
    """Return the solr doc for the json data."""
    def needs_bc_prefix(identifier: str, legal_type: str) -> bool:
        """Return if the identifier should have the BC prefix or not."""
        numbers_only_rgx = r"^[0-9]+$"
        # TODO: get legal types from shared enum
        return legal_type in ["BEN", "BC", "CC", "ULC"] and re.search(numbers_only_rgx, identifier)

    def get_party_name(officer: dict[str, str]) -> str:
        """Return the parsed name of the party in the given doc info."""
        if officer.get("organizationName"):
            return officer["organizationName"].strip()
        person_name = ""
        if officer.get("firstName"):
            person_name += officer["firstName"].strip()
        if officer.get("middleInitial"):
            person_name += " " + officer["middleInitial"].strip()
        if officer.get("lastName"):
            person_name += " " + officer["lastName"].strip()
        return person_name.strip()

    business_info = request_json.get("business")
    party_info = request_json.get("parties")

    # add new base doc
    identifier = business_info["identifier"]
    legal_type = business_info["legalType"]
    if needs_bc_prefix(identifier, legal_type):
        identifier = f"BC{identifier}"

    # Temporary code while migration is in progress
    if (
        "modernized" not in business_info \
        and identifier not in current_app.config["BUSINESSES_MANAGED_BY_COLIN"] \
        and legal_type in ["BC", "A", "C", "ULC", "CUL"]
    ):
        # make legal-api call to check current 'modernized' status
        try:
            lear_record = entity.get_business(identifier)
            if lear_record.status_code == HTTPStatus.OK:
                # the business is modernized
                business_info["modernized"] = True
        except Exception as err:
            current_app.logger.error("Could not determine modernization for %s.", identifier)
        
    business_doc = BusinessDoc(
        bn=business_info.get("taxId"),
        id=identifier,
        identifier=identifier,
        legalType=legal_type,
        name=business_info["legalName"].strip(),
        status=business_info["state"],
        goodStanding=business_info.get("goodStanding"),
        modernized=business_info.get("modernized"))
    if party_info:
        party_list = []
        # add party doc to base doc
        for party in party_info:
            party_doc = PartyDoc(
                id=f"{business_doc.identifier}_{party['officer']['id']!s}",
                parentBN=business_doc.bn,
                parentIdentifier=business_doc.identifier,
                parentLegalType=business_doc.legalType,
                parentName=business_doc.name,
                parentStatus=business_doc.status,
                partyName=get_party_name(party["officer"]),
                partyRoles=[x["roleType"].lower() for x in party["roles"]],
                partyType=party["officer"]["partyType"]
            )
            party_list.append(party_doc)

        if party_list:
            business_doc.parties = party_list
    # add doc to updates table
    return business_doc
