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
"""API endpoints for Document json/pdfs."""
from http import HTTPStatus

from flask import Blueprint, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.exceptions import ApiConnectionException, StorageException
from search_api.models import Document, DocumentAccessRequest
# from search_api.services import storage
from search_api.services.entity import get_business_document, get_business_filing_document
from search_api.utils.auth import jwt


bp = Blueprint('DOCUMENTS', __name__, url_prefix='/<string:business_identifier>/documents/<int:document_key>')  # pylint: disable=invalid-name


@bp.get('')
@bp.get('/<int:filing_id>')
@cross_origin(origin='*')
@jwt.requires_auth
def get_document_data(business_identifier, document_key, filing_id = None):
    """Return the document json/pdf specified by the document key / file name."""
    try:
        account_id = request.headers.get('accountId', None)
        if not account_id:
            return resource_utils.account_required_response()

        # get document
        document = Document.find_by_document_key(document_key)
        if not document:
            return resource_utils.not_found_error_response('Document', document_key)

        # check access
        access_request = DocumentAccessRequest.find_by_id(document.access_request_id)
        if str(access_request.account_id) != account_id:
            return resource_utils.unauthorized_error_response(account_id)
        if not access_request.isActive:
            return resource_utils.authorization_expired_error_response(account_id)

        # get pdf
        if filing_id and document.document_type == Document.DocumentType.BUSINESS_SUMMARY_FILING_HISTORY:
            # Request is for a filing history document.
            resp = get_business_filing_document(business_identifier, filing_id)
            return resp.content, resp.status_code

        # TODO: uncomment after testing with running gcp service
        # if document.file_name:
        #     # get from google cache
        #     raw_data = storage.get_document(document.file_name, document.document_type)
        #     return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

        # get from lear (cached doc not ready yet)
        resp = get_business_document(business_identifier, document.document_type)
        return resp.content, resp.status_code
    
    except ApiConnectionException as api_exception:
        return resource_utils.default_exception_response(api_exception)
    except StorageException as storage_exception:
        return resource_utils.gcp_storage_service_error(storage_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
