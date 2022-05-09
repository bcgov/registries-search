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
"""API endpoints for Registry Search."""
from contextlib import suppress
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from search_api.exceptions import SolrException
import search_api.resources.utils as resource_utils
from search_api.services import solr


bp = Blueprint('SEARCH', __name__, url_prefix='/search')  # pylint: disable=invalid-name


@bp.get('/suggest')
@cross_origin(origin='*')
def suggest():
    """Return a list of suggestions from solr based from the given value."""
    try:
        query = request.args.get('query', None)
        if not query:
            return jsonify({'message': "Expected url param 'query'."}), HTTPStatus.BAD_REQUEST

        rows = None
        with suppress(Exception):
            rows = int(request.args.get('max_results', None))

        suggestions = solr.business_suggest(query, rows)
        return jsonify({'results': suggestions}), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.solr_exception_response(solr_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
