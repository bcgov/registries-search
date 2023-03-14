# Copyright © 2019 Province of British Columbia
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
"""This class is a wrapper for document storage API calls."""
import os

from flask import current_app
from google.cloud import storage

from search_api.enums import DocumentType
from search_api.exceptions import StorageException
from search_api.services.gcp_auth.auth_service import GoogleAuthService
from search_api.services.document_storage.abstract_storage_service import StorageService


class GoogleStorageService(StorageService):  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    # Google cloud storage configuration.
    GCP_BUCKET_ID_SUMMARY = str(os.getenv('GCP_CS_BUCKET_ID_SUMMARY'))
    GCP_BUCKET_ID_COGS = str(os.getenv('GCP_BUCKET_ID_CERT_OF_GOOD_STANDING'))
    GCP_BUCKET_ID_COS = str(os.getenv('GCP_BUCKET_ID_CERT_OF_STATUS'))
    GCP_BUCKET_ID_LUS = str(os.getenv('GCP_BUCKET_ID_LETTER_UNDER_SEAL'))

    @classmethod
    def get_document(cls, name: str, doc_type: DocumentType = None):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            current_app.logger.info(f'Fetching doc type={doc_type}, name={name}.')
            credentials = GoogleAuthService.get_credentials()
            storage_client = storage.Client(credentials=credentials)
            bucket = storage_client.bucket(cls.__get_bucket_id(doc_type))
            blob = bucket.blob(name)
            return blob.download_as_bytes()

        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(str(err))
            raise StorageException(f'GET document failed for doc type={doc_type}, name={name}.') from err

    @classmethod
    def __get_bucket_id(cls, doc_type: DocumentType = None):
        """Map the document type to a bucket ID. The default is GCP_BUCKET_ID_SUMMARY."""
        if not doc_type or doc_type == DocumentType.BUSINESS_SUMMARY_FILING_HISTORY:
            return cls.GCP_BUCKET_ID_SUMMARY
        if doc_type == DocumentType.CERTIFICATE_OF_GOOD_STANDING:
            return cls.GCP_BUCKET_ID_COGS
        if doc_type == DocumentType.CERTIFICATE_OF_STATUS:
            return cls.GCP_BUCKET_ID_COS
        if doc_type == DocumentType.LETTER_UNDER_SEAL:
            return cls.GCP_BUCKET_ID_LUS

        current_app.logger.error(f'No bucket ID mapped for DocumentType {str(doc_type)}')
        return None
