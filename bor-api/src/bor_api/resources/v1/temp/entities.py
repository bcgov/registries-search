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
"""API endpoints for searching entities over the temp bo solr instance."""
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request

from bor_api.exceptions import exception_response
from bor_api.services.solr import Solr


bp = Blueprint('TEMP_ENTITIES', __name__, url_prefix='/entities')  # pylint: disable=invalid-name


@bp.post('')
def entities():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Temp endpoint to return a list of entity results from the temp bo solr."""
    try:
        if current_app.config.get('POD_NAMESPACE') == 'prod':
            return {}, HTTPStatus.NOT_IMPLEMENTED

        solr = Solr()
        solr.leader_core = current_app.config.get('TEMP_SOLR_SVC_CORE')
        solr.follower_core = current_app.config.get('TEMP_SOLR_SVC_CORE')
        solr.leader_url = current_app.config.get('TEMP_SOLR_SVC_URL')
        solr.follower_url = current_app.config.get('TEMP_SOLR_SVC_URL')

        request_json = request.get_json()

        results = solr.query({'query': request_json.get('value')})
        response = {
            'totalResults': results.get('response', {}).get('numFound'),
            'results': results.get('response', {}).get('docs')
        }

        return jsonify(response), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
