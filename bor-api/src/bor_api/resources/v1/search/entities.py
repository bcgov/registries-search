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
"""API endpoints for searching directors."""
from http import HTTPStatus

from flask import jsonify, request, Blueprint
from flask_cors import cross_origin

from bor_api.exceptions import exception_response
from bor_api.services import bor_solr
from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.bor_solr_search_params import SearchParams
from bor_api.services.solr.bor_solr_search_util import entities_search, parse_facets, prep_query_str


bp = Blueprint('ENTITIES', __name__, url_prefix='/entities')  # pylint: disable=invalid-name


@bp.post('')
@cross_origin(origin='*')
def entities():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-locals
    """Return a list of entity results from solr."""
    try:
        request_json = request.get_json()
        name = request_json.get(Field.NAME.value, None)
        if not name:
            # update this later once we have other filters going
            return jsonify({'message': f"Expected payload to include '{Field.NAME.value}'."}), HTTPStatus.BAD_REQUEST
        # clean query values
        query = {
            Field.NAME.value: prep_query_str(name)
            # add in other params later
        }
        # add in facet categories later

        start = request_json.get('start', bor_solr.default_start)
        rows = request_json.get('rows', bor_solr.default_rows)
        try:
            start = int(start)
            rows = int(rows)
        except ValueError:  # catch invalid start/row entry
            return {'message': "Expected integer for params: 'start', 'rows'"}, HTTPStatus.BAD_REQUEST

        params = SearchParams(query, start, rows)
        results = entities_search(params)
        response = {
            'facets': parse_facets(results),
            'searchResults': {
                'queryInfo': {
                    'query': {**query},
                    'rows': rows,
                    'start': start
                },
                'totalResults': results.get('response', {}).get('numFound'),
                'results': results.get('response', {}).get('docs')}}

        return jsonify(response), HTTPStatus.OK

    except Exception as exception:  # noqa: B902
        return exception_response(exception)
