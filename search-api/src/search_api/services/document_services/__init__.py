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
"""This manages all the calls for the document service."""
from uuid import uuid4

from flask import current_app
from simple_cloudevent import SimpleCloudEvent

from search_api.models import Document, DocumentAccessRequest, User
from search_api.utils.datetime import datetime


def create_doc_request_ce(document_request: DocumentAccessRequest) -> SimpleCloudEvent:
    """Create a CloudEvent containing all the information for a document request."""
    sce_dict = {}
    sce_dict['id'] = str(uuid4())
    sce_dict['source'] = current_app.config.get('SERVICE_NAME')
    sce_dict['subject'] = current_app.config.get('SERVICE_DOCUMENT_SUBJECT')
    sce_dict['time'] = datetime.utcnow()

    sce_dict['data'] = {}
    sce_data = sce_dict['data']
    sce_data['businessIdentifier'] = document_request.business_identifier
    sce_data['accountId'] = document_request.account_id
    sce_data['user'] = document_request.submitter.sub

    sce_data['documents'] = []
    sce_documents = sce_data['documents']
    for doc in document_request.documents:
        document = {'documentKey': doc.document_key,
                    'documentType': doc.document_type,
                    }
        sce_documents.append(document)

    ce = SimpleCloudEvent(**sce_dict)  # pylint: disable=invalid-name;

    return ce
