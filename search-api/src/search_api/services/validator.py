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


class RequestValidator():  # pylint: disable=too-few-public-methods
    """The class manages methods to validate a request."""

    valid_doc_types = [DocumentType.BUSINESS_SUMMARY_FILING_HISTORY.name]

    @staticmethod
    def validate_document_access_request(document_access_request_json: dict, account_id: str, token):
        """Validate a document access request."""
        validation_errors = []

        account_org = auth_svc.account_org(token, account_id)
        if not account_org:
            validation_errors.append({'error': 'Invalid Account'})

        if account_org.get('orgType') != 'PREMIUM':
            validation_errors.append({'error': 'Document Access Request can be created only by a premium account user'})

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
