# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoints for document filing json/pdfs."""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.enums import DocumentType
from search_api.exceptions import ApiConnectionException, UnauthorizedException
from search_api.models import DocumentAccessRequest
from search_api.services.authz import does_user_have_account
from search_api.services.entity import get_business_filing_document, get_business_filing_document_list
from search_api.utils.auth import jwt

bp = Blueprint("FILINGS", __name__, url_prefix="/filings")


@bp.get("/<int:filing_id>")
@bp.get("/<int:filing_id>/<string:filing_name>")
@cross_origin(origins="*")
@jwt.requires_auth
def get_filing_documents_info(business_identifier, filing_id, filing_name=None):
    """Return the document list or document pdf for the given filing id / name."""
    try:
        if not filing_name:
            # get filing document list
            resp = get_business_filing_document_list(business_identifier, filing_id)
            return resp.json(), resp.status_code

        account_id = request.headers.get("Account-Id", None)
        if not account_id:
            return resource_utils.account_required_response()

        token = jwt.get_token_auth_header()
        user_is_part_of_org = does_user_have_account(token, account_id)

        if not user_is_part_of_org:
            raise UnauthorizedException(account_id)

        # check access
        active_access_requests = DocumentAccessRequest.find_active_requests(account_id, business_identifier)
        has_filing_history_access = False
        for access_req in active_access_requests:
            if [x for x in access_req.documents if x.document_type == DocumentType.BUSINESS_SUMMARY_FILING_HISTORY]:
                has_filing_history_access = True

        if not has_filing_history_access:
            # account doesn't have an active access request with a business summary/history doc
            raise UnauthorizedException(account_id)

        # get pdf
        resp = get_business_filing_document(business_identifier, filing_id, filing_name)
        return resp.content, resp.status_code

    except UnauthorizedException as unauthorized_exception:
        return resource_utils.unauthorized_error_response(unauthorized_exception.account_id)
    except ApiConnectionException as api_exception:
        return jsonify({"message": "Error getting document data.", "detail": api_exception.detail}), api_exception.code
    except Exception as default_exception:
        return resource_utils.default_exception_response(default_exception)
