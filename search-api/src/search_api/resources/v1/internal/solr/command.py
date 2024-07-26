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

import search_api.resources.utils as resource_utils
from search_api.exceptions import SolrException
from search_api.services import SYSTEM_ROLE, business_solr
from search_api.utils.auth import jwt


bp = Blueprint('COMMAND', __name__, url_prefix='/command')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def replication_command():
    """Execute a replication command on solr."""
    try:
        request_json: dict = request.json

        # validate payload
        if not (command := request_json.get('command')):
            return resource_utils.bad_request_response('Invalid payload.',
                                                       [{'Missing Required Field': 'Expected "command" in payload.'}])

        valid_commands = ['backup', 'details', 'restore', 'restorestatus']
        if command not in valid_commands:
            return resource_utils.bad_request_response('Invalid payload.',
                                                       [{'error': f'Expected value to be one of {valid_commands}',
                                                         'path': '/command'}])

        resp = business_solr.replication(command)
        return jsonify(resp.json()), resp.status_code

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as exception:  # noqa: B902
        return resource_utils.default_exception_response(exception)
