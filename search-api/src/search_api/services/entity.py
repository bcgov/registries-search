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
"""Manages LEAR api interactions."""
from http import HTTPStatus

import requests
from flask import current_app, request
from flask_caching import Cache
from requests import exceptions

from search_api.enums import DocumentType
from search_api.exceptions import ApiConnectionException
from search_api.services.authz import get_bearer_token

# DocumentType mapper to document name used in LEAR for business documents
DOCUMENT_NAME = {
    DocumentType.BUSINESS_SUMMARY_FILING_HISTORY: "summary",
    DocumentType.CERTIFICATE_OF_GOOD_STANDING: "cogs",
    DocumentType.CERTIFICATE_OF_STATUS: "cstat",
    DocumentType.LETTER_UNDER_SEAL: "lseal"
}


entity_cache = Cache()


def _get_business_cache_key(identifier: str):
    """Return the cache key for business information."""
    return "entity" + identifier


def _get_business_filing_cache_key(identifier: str, filing_id: int):
    """Return the cache key for business filing information."""
    return f"entity{identifier}{filing_id}"


def _get_drs_document_url(identifier: str, filing_id: int, filing_name: str):
    """Return the filing drs document url."""
    document_list_resp = get_business_filing_document_list(identifier, filing_id)
    legal_filings: list[dict[str, str]] = (document_list_resp.json()).get("documents", {}).get("legalFilings", [])
    for document_info in legal_filings:
        for document_name, document_url in document_info.items():
            if document_name == filing_name:
                return document_url


def get_business_document(identifier: str, document_type: DocumentType, content_type: str):
    """Get the business document for the given identifier and type."""
    document_name = DOCUMENT_NAME[document_type]
    if not document_name:
        raise ApiConnectionException(HTTPStatus.NOT_IMPLEMENTED,
                                     [{"message": f"Report type for {document_type.name} does not exist."}])

    lear_svc_url = f"{current_app.config.get('LEAR_SVC_URL')}/businesses/{identifier}/documents/{document_name}"
    try:
        token = get_bearer_token()
        headers = {"Authorization": "Bearer " + token, "Accept": content_type}
        business_api_timeout = current_app.config.get("BUSINESS_API_TIMEOUT")
        lear_response = requests.get(url=lear_svc_url, headers=headers, timeout=business_api_timeout)
    except exceptions.Timeout as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{"message": "Unable to get business document from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    except ApiConnectionException as err:
        # pass along auth exception
        raise err
    except Exception as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.SERVICE_UNAVAILABLE,
                                     [{"message": "Unable to get business document from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    return lear_response


def get_business_filing_document(identifier: str, filing_id: int, filing_name: str):
    """Get the business filing document for the given identifier, id and name."""
    lear_svc_url = \
        current_app.config.get("LEAR_SVC_URL") + \
        f"/businesses/{identifier}/filings/{filing_id}/documents/{filing_name}"

    if (report_type := request.args.get("reportType")) and (drs_id := request.args.get("drsId")):
        lear_svc_url += f"?reportType={report_type}&drsId={drs_id}"

    elif url_with_drs_params := _get_drs_document_url(identifier, filing_id, filing_name):
        # override url with the full document url including drs params
        lear_svc_url = url_with_drs_params

    try:
        token = get_bearer_token()
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/pdf"}
        business_api_timeout = current_app.config.get("BUSINESS_API_TIMEOUT")
        lear_response = requests.get(url=lear_svc_url, headers=headers, timeout=business_api_timeout)
    except exceptions.Timeout as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{"message": "Unable to get filing document pdf from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    except ApiConnectionException as err:
        # pass along auth exception
        raise err
    except Exception as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.SERVICE_UNAVAILABLE,
                                     [{"message": "Unable to get filing document pdf from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    return lear_response


@entity_cache.cached(timeout=600, make_cache_key=_get_business_filing_cache_key)
def get_business_filing_document_list(identifier: str, filing_id: int):
    """Get the business filing document list for the given identifier and id."""
    lear_svc_url = \
        current_app.config.get("LEAR_SVC_URL") + \
        f"/businesses/{identifier}/filings/{filing_id}/documents"
    try:
        token = get_bearer_token()
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
        business_api_timeout = current_app.config.get("BUSINESS_API_TIMEOUT")
        lear_response = requests.get(url=lear_svc_url, headers=headers, timeout=business_api_timeout)
    except exceptions.Timeout as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{"message": "Unable to get filing document list from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    except ApiConnectionException as err:
        # pass along auth exception
        raise err
    except Exception as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.SERVICE_UNAVAILABLE,
                                     [{"message": "Unable to get filing document list from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    return lear_response


@entity_cache.cached(timeout=600, make_cache_key=_get_business_cache_key)
def get_business(identifier: str):
    """Get the business json for the given identifier."""
    lear_svc_url = current_app.config.get("LEAR_SVC_URL") + f"/businesses/{identifier}"
    try:
        token = get_bearer_token()
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
        business_api_timeout = current_app.config.get("BUSINESS_API_TIMEOUT")
        lear_response = requests.get(url=lear_svc_url,
                                     headers=headers,
                                     params={"slim": True},
                                     timeout=business_api_timeout)
    except exceptions.Timeout as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.GATEWAY_TIMEOUT,
                                     [{"message": "Unable to get business json from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    except ApiConnectionException as err:
        # pass along auth exception
        raise err
    except Exception as err:
        current_app.logger.debug(err.with_traceback(None))
        raise ApiConnectionException(HTTPStatus.SERVICE_UNAVAILABLE,
                                     [{"message": "Unable to get business json from lear.",
                                       "reason": err.with_traceback(None)}]) from err
    return lear_response
