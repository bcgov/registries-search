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
# from http import HTTPStatus
from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.enums import DocumentType
from search_api.exceptions import ApiConnectionException, StorageException
from search_api.models import Document, DocumentAccessRequest
# from search_api.services import storage
from search_api.services.entity import (
    get_business_document,
    get_business_filing_document,
    get_business_filing_document_list)
from search_api.utils.auth import jwt


bp = Blueprint('DOCUMENTS', __name__, url_prefix='')  # pylint: disable=invalid-name


@bp.get('/filings/<int:filing_id>')
@bp.get('/filings/<int:filing_id>/<string:filing_name>')
@cross_origin(origin='*')
@jwt.requires_auth
def get_filing_documents_info(business_identifier, filing_id, filing_name=None):
    """Return the document list or document pdf for the given filing id / name."""
    try:
        if not filing_name:
            # get filing document list
            resp = get_business_filing_document_list(business_identifier, filing_id)
            return resp.json(), resp.status_code

        account_id = request.headers.get('Account-Id', None)
        if not account_id:
            return resource_utils.account_required_response()
        # check access
        active_access_requests = DocumentAccessRequest.find_active_requests(account_id, business_identifier)
        has_filing_history_access = False
        for access_req in active_access_requests:
            if [x for x in access_req.documents if x.document_type == DocumentType.BUSINESS_SUMMARY_FILING_HISTORY]:
                has_filing_history_access = True

        if not has_filing_history_access:
            # account doesn't have an active access request with a business summary/history doc
            return resource_utils.unauthorized_error_response(account_id)

        # get pdf
        resp = get_business_filing_document(business_identifier, filing_id, filing_name)
        return resp.content, resp.status_code

    except ApiConnectionException as api_exception:
        return jsonify({'message': 'Error getting document data.', 'detail': api_exception.detail}), api_exception.code
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)


@bp.get('/<string:document_key>')
@cross_origin(origin='*')
@jwt.requires_auth
# pylint: disable=too-many-return-statements
def get_document_data(business_identifier, document_key):
    """Return the document json/pdf specified by the document key."""
    try:
        account_id = request.headers.get('Account-Id', None)
        if not account_id:
            return resource_utils.account_required_response()

        if (content_type := str(request.accept_mimetypes)) not in ['application/json', 'application/pdf']:
            msg = f'Invalid Accept header. Expected application/json or application/pdf but received {content_type}'
            return resource_utils.bad_request_response(msg)

        # get document
        document = Document.find_by_document_key(document_key)
        if not document:
            return resource_utils.not_found_error_response('Document', document_key)

        # check access
        access_request = DocumentAccessRequest.find_by_id(document.access_request_id)
        if str(access_request.account_id) != account_id:
            return resource_utils.unauthorized_error_response(account_id)
        if not access_request.is_active:
            return resource_utils.authorization_expired_error_response(account_id)

        # TODO: uncomment after testing with running gcp service and provide json option from gcp
        # if document.file_name:
        #     # get from google cache
        #     raw_data = storage.get_document(document.file_name, document.document_type)
        #     return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

        # get from lear (cached doc not ready yet)
        resp = get_business_document(business_identifier, document.document_type, content_type)
        content = resp.content if content_type == 'application/pdf' else jsonify(resp.json())
        return content, resp.status_code

    except ApiConnectionException as api_exception:
        current_app.logger.error(api_exception)
        return jsonify({'message': 'Error getting document data.', 'detail': api_exception.detail}), api_exception.code
    except StorageException as storage_exception:
        return resource_utils.gcp_storage_service_error(storage_exception)
    except Exception as default_exception:  # noqa: B902
        return resource_utils.default_exception_response(default_exception)
