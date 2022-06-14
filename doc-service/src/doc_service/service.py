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
"""This module contains the service."""
from __future__ import annotations

from http import HTTPStatus

from simple_cloudevent import SimpleCloudEvent

from doc_service.services.documents import generate_search_docs  # noqa: I001
from doc_service.services.iam import JWTService
from doc_service.services.storage import GoogleCloudStorage

from .config import Config
from .services.logging import logging


DOC_FUNCTION = {
    'search_documents': generate_search_docs,
}


def doc_service_callback(ce: SimpleCloudEvent) -> HTTPStatus:  # pylint: disable=invalid-name
    """Generate the documents and save their names in search db for the given event."""
    try:
        if not ce:
            logging.info('No CloudEvent message given')
            return HTTPStatus.BAD_REQUEST

        event_type = ce.data.get('event_type')
        doc_access_id = ce.data.get('access_id')

        config = Config()
        jwt_service = JWTService(config.OIDC_TOKEN_URL,
                                 config.OIDC_SA_CLIENT_ID,
                                 config.OIDC_SA_CLIENT_SECRET)

        gcs = GoogleCloudStorage(config)
        if doc_func := get_document_function(event_type):
            status = doc_func(doc_access_id, config, jwt_service, gcs)
            return status

        logging.info(f'Ignoring: Got nothing to do for ce: {ce}')
        return HTTPStatus.OK

    except Exception as err:  # noqa: B902
        logging.error(err)
        return HTTPStatus.INTERNAL_SERVER_ERROR


def get_document_function(event_type: str) -> callable:
    """Get the document function for the given event type."""
    return DOC_FUNCTION.get(event_type)
