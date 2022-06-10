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
"""The document delivery service."""
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Tuple

import pytz
import requests
from search_api.models import Document, DocumentAccessRequest

from doc_service.config import BaseConfig
from doc_service.services.iam import JWTService
from doc_service.services.logging import logging
from doc_service.services.storage import AbstractStorageService, StorageDocumentTypes  # noqa: I001


class DocumentDeliveryError(Exception):
    """The exception for document delivery errors."""


DOCUMENT_DATA_KEYS = {
    Document.DocumentType.BUSINESS_SUMMARY_FILING_HISTORY: 'summary',
}

DOCUMENT_DISPLAY_NAME = {
    Document.DocumentType.BUSINESS_SUMMARY_FILING_HISTORY: 'SUMMARY',
}


def generate_search_docs(doc_access_id: int,
                         config: BaseConfig,
                         jwt_service: JWTService,
                         storage_service: AbstractStorageService
                         ) -> HTTPStatus:
    """Deliver the verification document.

    Args:
        doc_access_id: The DocumentAccessRequest id (modelled in search-api).
        config: The application config data.
        jwt_service: The JWT service.
        storage_service: The storage service.
    Returns:
        The status code.
    """
    token = jwt_service.get_token()

    # get document data
    document_access_request = DocumentAccessRequest.find_by_id(doc_access_id)

    # get document pdfs
    pdfs = []
    for document in document_access_request.documents:
        pdf, status = _get_document_pdf(document_access_request.business_identifier,
                                        DOCUMENT_DATA_KEYS[document.document_type],
                                        token, config)
        if status not in (HTTPStatus.OK, HTTPStatus.CREATED):
            return status
        pdfs.append(pdf)

        # create a filename
        file_name = _get_filename(document_access_request.business_identifier, document)
        # save document to storage
        _save_doc_to_storage(file_name, pdf, config, storage_service)
        document.file_name = file_name

    document_access_request.status = DocumentAccessRequest.Status.COMPLETED
    document_access_request.save()

    return HTTPStatus.CREATED


def _get_filename(identifier: str, document: Document) -> str:
    """Build a correctly formatted unique name."""
    filename_template = '{identifier}.{type}.{year}{month}{day}.{statement_key}.PDF'
    today_utc = datetime.datetime.now(pytz.utc)
    today_local = today_utc.astimezone(pytz.timezone('Canada/Pacific'))

    filename = filename_template.format(statement_key=document.document_key,
                                        day=str(today_local.day).zfill(2),
                                        month=str(today_local.month).zfill(2),
                                        year=str(today_local.year),
                                        type=DOCUMENT_DISPLAY_NAME[document.document_type],
                                        identifier=identifier
                                        )
    return filename


def _get_document_pdf(identifier: str,
                      doc_type: str,
                      token: str,
                      config: BaseConfig) -> Tuple[bytes, HTTPStatus]:
    """Retrieve the document pdf from the Reports API.

    Args:
        data: The data to send to the API.
        token: The token to access the API.
        config: The application config data.
        end_point: The end point to call on the API.

    Returns:
        The pdf data and the status code.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    url = config.LEGAL_API_URL + f'/{identifier}/documents/{doc_type}'

    response = requests.get(url=url, headers=headers)
    if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
        return None, response.status_code

    if response.content:
        return response.content, response.status_code

    logging.info('No pdf data returned')
    return None, HTTPStatus.BAD_REQUEST


def _save_doc_to_storage(file_name: str,
                         document_pdf: bytes,
                         config: BaseConfig,
                         storage_service: AbstractStorageService):
    storage_service.connect()
    storage_filepath = file_name
    if hasattr(config, 'STORAGE_FILEPATH') and config.STORAGE_FILEPATH:
        storage_filepath = f'{config.STORAGE_FILEPATH}/{file_name}'
    storage_service.save_document(bucket_name=config.STORAGE_BUCKET_NAME,
                                  filename=storage_filepath,
                                  raw_data=document_pdf,
                                  doc_type=StorageDocumentTypes.BINARY.value)
