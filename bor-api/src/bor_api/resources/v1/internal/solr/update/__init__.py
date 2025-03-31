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
"""Exposes all of the internal endpoints in Flask-Blueprint style."""
from dataclasses import asdict
from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

from bor_api.enums import SolrDocEventType
from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import SolrDoc, SolrDocEvent, User
from bor_api.services import SYSTEM_ROLE, jwt
from bor_api.services.bor_solr.doc_models import Entity
from bor_api.utils.data_converters import get_btr_owner, get_lear_business, get_lear_party
from bor_api.utils.request_validators import validate_solr_update_request

from .resync import bp as resync_bp
from .sync import bp as sync_bp
from .synonyms import bp as synonyms_bp

bp = Blueprint("UPDATE", __name__, url_prefix="/update")
bp.register_blueprint(resync_bp)
bp.register_blueprint(sync_bp)
bp.register_blueprint(synonyms_bp)


@bp.put("")
@cross_origin(origins="*")
@jwt.requires_roles([SYSTEM_ROLE])
def update_entity():
    """Add/Update entity in BOR."""
    try:
        request_json: dict = request.json
        errors = validate_solr_update_request(request_json)
        if errors:
            return bad_request_response("Invalid payload.", errors)

        user = User.get_or_create_user_by_jwt(g.jwt_oidc_token_info)

        entities = _parse_entities(request_json)
        for entity in entities:
            # commit each entity. Ensures other flows (i.e. resync) will use the current data
            solr_doc = SolrDoc(doc=asdict(entity), entity_id=entity.id, _submitter_id=user.id).save()
            SolrDocEvent(event_type=SolrDocEventType.UPDATE, solr_doc_id=solr_doc.id).save()
            # SOLR update will be triggered by job (does a frequent bulk update to solr)

        return jsonify({"message": "Update accepted."}), HTTPStatus.ACCEPTED

    except Exception as exception:
        return exception_response(exception)


def _parse_entities(request_json: dict) -> list[Entity]:
    """Return the entity docs for the given data."""
    entities = []

    business = get_lear_business(request_json["business"])
    entities.append(business)

    for party_info in request_json.get("parties", []):
        entities += get_lear_party(party_info, business)

    owners = request_json.get("owners", [])
    for party_info in owners:
        entities.append(get_btr_owner(party_info, business))

    return entities
