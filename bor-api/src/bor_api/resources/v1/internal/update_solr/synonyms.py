# Copyright © 2024 Province of British Columbia
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
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from bor_api.enums import SolrSynonymType
from bor_api.exceptions import bad_request_response, exception_response
from bor_api.models import SolrSynonymList
from bor_api.services import SYSTEM_ROLE, bor_solr, jwt
from bor_api.services.solr.utils import get_synonyms


bp = Blueprint('SYNONYMS', __name__, url_prefix='/synonyms')  # pylint: disable=invalid-name


@bp.put('')
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
