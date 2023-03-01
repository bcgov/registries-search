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
"""Supply version and commit hash info.

When deployed in OKD, it adds the last commit hash onto the version info.
"""
import os
from http import HTTPStatus
from typing import Dict

import requests
from entity_queue_common.service_utils import QueueException
from requests import exceptions

from search_solr_updater import config
from search_solr_updater.logging import logger
from search_solr_updater.version import __version__


APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))


def _get_build_openshift_commit_hash():
    return os.getenv('OPENSHIFT_BUILD_COMMIT', None)


def get_run_version():
    """Return a formatted version string for this service."""
    commit_hash = _get_build_openshift_commit_hash()
    if commit_hash:
        return f'{__version__}-{commit_hash}'
    return __version__


# FUTURE: get this from a shared repo (copied in in a few places across repos now)
def get_bearer_token():
    """Get a valid Bearer token for the service to use."""
    token_url = APP_CONFIG.KEYCLOAK_AUTH_TOKEN_URL
    client_id = APP_CONFIG.KEYCLOAK_SERVICE_ACCOUNT_ID
    client_secret = APP_CONFIG.KEYCLOAK_SERVICE_ACCOUNT_SECRET
    auth_api_timeout = APP_CONFIG.AUTH_API_TIMEOUT

    data = 'grant_type=client_credentials'

    # get service account token
    try:
        res = requests.post(url=token_url,
                            data=data,
                            headers={'content-type': 'application/x-www-form-urlencoded'},
                            auth=(client_id, client_secret),
                            timeout=auth_api_timeout)
        if res.status_code != HTTPStatus.OK:
            raise QueueException(res.status_code, 'Unable to get service account token from auth.')

        return res.json().get('access_token')
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        logger.debug('AUTH connection failure: %s', err)
        raise QueueException(HTTPStatus.GATEWAY_TIMEOUT, 'Unable to get service account token from auth.')
    except QueueException as err:
        # pass along
        raise err
    except Exception as err:  # noqa: B902
        logger.debug('AUTH connection failure: %s', err.with_traceback(None))
        raise QueueException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to get service account token from auth.')


def get_business_info(url: str, headers: Dict[str, str]):
    """Get business data from the legal-api."""
    try:
        resp = requests.get(url=url, headers=headers, params={'slim': True}, timeout=APP_CONFIG.BUSINESS_API_TIMEOUT)
        if resp.status_code != HTTPStatus.OK:
            raise QueueException(resp.status_code, 'Unable to get business data from legal-api.')
        return resp
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        logger.debug('LEGAL API connection failure: %s', err)
        raise QueueException(HTTPStatus.GATEWAY_TIMEOUT, 'Unable to get business data from legal-api.')
    except QueueException as err:
        # pass along
        raise err
    except Exception as err:  # noqa: B902
        logger.debug('LEGAL API connection failure: %s', err.with_traceback(None))
        raise QueueException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to get business data from legal-api.')
