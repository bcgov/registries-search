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
"""API endpoint for bulk importing entity records into solr."""
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin

from bor_api.exceptions import bad_request_response, exception_response
from bor_api.services import SYSTEM_ROLE, jwt, solr
from bor_api.services.bor_solr.doc_models import Entity


bp = Blueprint('IMPORT', __name__, url_prefix='/solr/import')  # pylint: disable=invalid-name


@bp.put('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def import_entities():
    """Import entities into BOR SOLR."""
    try:
        request_json: dict = request.json
        if not (entities_json := request_json.get('entities', [])):
            return bad_request_response('Invalid payload.', ['Expecting required field: "entities"'])

        if (timeout := int(request_json.get('timeout', '25'))) > 200:
            return bad_request_response('Invalid payload.', ['Expecting desired "timeout" to be under 200.'])

        current_app.logger.debug('Translating import payload to entity docs...')
        entities = [Entity(**e) for e in entities_json]
        current_app.logger.debug('Sending entity docs to SOLR...')
        solr.create_or_replace_docs(entities, timeout)
        current_app.logger.debug('Import completed.')

        return jsonify({'message': 'Import finished.'}), HTTPStatus.CREATED

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
