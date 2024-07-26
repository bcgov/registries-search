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

import search_api.resources.utils as resource_utils
from search_api.exceptions import SolrException
from search_api.services import SYSTEM_ROLE, business_solr
from search_api.services.business_solr.doc_models import BusinessDoc
from search_api.utils.auth import jwt


bp = Blueprint('IMPORT', __name__, url_prefix='/import')  # pylint: disable=invalid-name


@bp.put('')
@cross_origin(origin='*')
@jwt.requires_roles([SYSTEM_ROLE])
def import_businesses():
    """Import businesses into Business SOLR."""
    try:
        request_json: dict = request.json
        if not (doc_list := request_json.get('businesses', [])):
            return resource_utils.bad_request_response('Invalid payload.', ['Expecting required field: "businesses"'])

        if (timeout := int(request_json.get('timeout', '25'))) > 200:
            return resource_utils.bad_request_response('Invalid payload.', ['Expecting desired "timeout" to be under 200.'])

        if request_json.get('type') == 'partial':
            # NOTE: raw_docs may be partial data and/or child documents
            current_app.logger.debug('Sending partials list to SOLR...')
            business_solr.create_or_replace_docs(raw_docs=doc_list, timeout=timeout)
        else:
            current_app.logger.debug('Translating import payload to entity docs...')
            businesses = [BusinessDoc(**e) for e in doc_list]
            current_app.logger.debug('Sending business docs to SOLR...')
            business_solr.create_or_replace_docs(docs=businesses, timeout=timeout, additive=False)

        current_app.logger.debug('Import completed.')
        return jsonify({'message': 'Import finished.'}), HTTPStatus.CREATED

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as exception:  # noqa: B902
        return resource_utils.default_exception_response(exception)
