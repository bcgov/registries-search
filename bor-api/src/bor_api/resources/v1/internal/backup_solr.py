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
"""API endpoint for backing up / restoring a solr index."""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from bor_api.exceptions import bad_request_response, exception_response
from bor_api.services import SYSTEM_ROLE, bor_solr, jwt


bp = Blueprint('BACKUP', __name__, url_prefix='/solr/backup')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def backup():
    """Backup/restore an index in solr."""
    try:
        request_json: dict = request.json

        # validate payload
        if not (command := request_json.get('command')):
            return bad_request_response('Invalid payload.',
                                        [{'Missing Required Field': 'Expected "command" in payload.'}])

        valid_commands = ['backup', 'details', 'restore', 'restorestatus']
        if command not in valid_commands:
            return bad_request_response('Invalid payload.',
                                        [{'error': f'Expected value to be one of {valid_commands}',
                                          'path': '/command'}])

        resp = bor_solr.replication(command)
        return jsonify(resp.json()), resp.status_code

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
