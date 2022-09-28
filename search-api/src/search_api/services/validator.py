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
"""The class manages methods to validate a request."""
import search_api.services.authz as auth_svc
from search_api.enums import DocumentType
from search_api.services import SBC_STAFF, STAFF_ROLE
from search_api.utils.util import get_str


class RequestValidator():  # pylint: disable=too-few-public-methods
    """The class manages methods to validate a request."""

    valid_doc_types = [DocumentType.BUSINESS_SUMMARY_FILING_HISTORY.name,
                       DocumentType.CERTIFICATE_OF_GOOD_STANDING.name,
                       DocumentType.CERTIFICATE_OF_STATUS.name,
                       DocumentType.LETTER_UNDER_SEAL.name]

    @staticmethod
    def validate_document_access_request(document_access_request_json: dict, account_id: str, token,
                                         role: str = 'basic'):
        """Validate a document access request."""
        validation_errors = []

        if role not in [STAFF_ROLE, SBC_STAFF]:
            account_org = auth_svc.account_org(token, account_id)
            if not account_org:
                validation_errors.append({'error': 'Invalid Account'})

            if account_org.get('orgType') != 'PREMIUM':
                validation_errors.append({
                    'error': 'Document Access Request can be created only by a premium account user'})

        documents = document_access_request_json.get('documentAccessRequest', {}).get('documents', [])
        if not documents:
            validation_errors.append({'error': 'Document list must contain atleast one document type'})

        for document in documents:
            document_type = document.get('type', None)
            if not document_type or document_type not in RequestValidator.valid_doc_types:
                validation_errors.append({'error': 'Invalid Document Type'})

        if validation_errors:
            return validation_errors
        return None

    @staticmethod
    def validate_solr_update_request(request_json: dict):  # pylint: disable=too-many-branches
        """Validate solr business update request."""
        err = []
        if not request_json.get('business'):
            err.append({'error': 'Business Object is required.', 'path': '/business'})
            return err

        identifier_path = '/business/identifier'
        if get_str(request_json, identifier_path) is None:
            err.append({'error': 'Identifier is required.', 'path': identifier_path})

        business_name_path = '/business/legalName'
        if get_str(request_json, business_name_path) is None:
            err.append({'error': 'Business Name is required.', 'path': business_name_path})

        business_type_path = '/business/legalType'
        if get_str(request_json, business_type_path) is None:
            err.append({'error': 'Business Type is required.', 'path': business_type_path})

        business_status_path = '/business/status'
        business_status = get_str(request_json, business_status_path)
        if business_status is None or business_status not in ['ACTIVE', 'HISTORICAL']:
            err.append({'error': 'A valid business status is required.', 'path': business_status_path})

        index = 0
        for party in request_json.get('parties', []):
            if not party.get('id'):
                err.append({'error': 'Party Id is required.', 'path': f'/parties/{index}/id'})

            if not party.get('partyType'):
                err.append({'error': 'Party Type is required.', 'path': f'/parties/{index}/partyType'})

            if not party.get('roles'):
                err.append({'error': 'Party Roles is required.', 'path': f'/parties/{index}/roles'})

            if party.get('partyType'):
                if party.get('partyType') == 'organization':
                    if not party.get('organizationName'):
                        err.append({'error': 'Organization name is required.',
                                    'path': f'/parties/{index}/organizationName'})
                else:
                    if not (party.get('firstName') or party.get('middleInitial') or party.get('lastName')):
                        err.append({'error': 'First name or middle name or last name is required.',
                                    'path': f'/parties/{index}'})
            index += 1
        return err
