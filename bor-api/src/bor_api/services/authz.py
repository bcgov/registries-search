# Copyright © 2023 Province of British Columbia
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
"""This manages all of the authentication and authorization service."""
from http import HTTPStatus

import requests
from flask import current_app
from flask.globals import request_ctx
from flask_caching import Cache
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bor_api.exceptions import ExternalServiceException
from flask_jwt_oidc import JwtManager

auth_cache = Cache()


# TODO: identify what roles we need for search
SYSTEM_ROLE = "system"
STAFF_ROLE = "staff"
COLIN_ROLE = "colin"
PPR_ROLE = "ppr"
BASIC_USER = "basic"
PRO_DATA_USER = "pro_data"
PUBLIC_USER = "public_user"
GOV_ACCOUNT_ROLE = "gov_account_user"
BCOL_HELP = "helpdesk"
SBC_STAFF = "sbc_staff"


def get_cache_key(path: str, token: str):
    """Return the cache key for the given args."""
    return "auth" + path + token


@auth_cache.cached(timeout=600, make_cache_key=get_cache_key)
def _call_auth_api(path: str, token: str) -> dict:
    """Return the auth api response for the given endpoint path."""
    response = None
    if not token:
        return response

    current_app.logger.debug(f"Auth getting {path}...")
    service_url = current_app.config.get("AUTH_SVC_URL")
    api_url = service_url + "/" if service_url[-1] != "/" else service_url
    api_url += path

    try:
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
        with Session() as http:
            retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            http.mount("http://", HTTPAdapter(max_retries=retries))
            ret_val = http.get(url=api_url, headers=headers)
            current_app.logger.debug(f"Auth get {path} response status: {ret_val.status_code!s}")
            response = ret_val.json()
    except (
        exceptions.ConnectionError,
        exceptions.Timeout,
        ValueError,
        Exception,
    ) as err:
        current_app.logger.debug(f"Auth api connection failure using svc:{api_url}", err)
        raise ExternalServiceException(
            HTTPStatus.SERVICE_UNAVAILABLE,
            [{"message": "Unable to get information from auth.", "reason": err.with_traceback(None)}],
        ) from err
    return response


@auth_cache.cached(timeout=300, key_prefix="view/token")
def get_bearer_token():
    """Get a valid Bearer token for the service to use."""
    token_url = current_app.config.get("ACCOUNT_SVC_AUTH_URL")
    client_id = current_app.config.get("ACCOUNT_SVC_CLIENT_ID")
    client_secret = current_app.config.get("ACCOUNT_SVC_CLIENT_SECRET")
    account_svc_timeout = current_app.config.get("ACCOUNT_SVC_TIMEOUT")

    data = "grant_type=client_credentials"

    # get service account token
    try:
        res = requests.post(
            url=token_url,
            data=data,
            headers={"content-type": "application/x-www-form-urlencoded"},
            auth=(client_id, client_secret),
            timeout=account_svc_timeout,
        )
        if res.status_code != HTTPStatus.OK:
            raise ConnectionError({"statusCode": res.status_code, "json": res.json()})
        return res.json().get("access_token")
    except exceptions.Timeout as err:
        current_app.logger.debug("ACCOUNT SVC connection failure: %s", err.with_traceback(None))
        raise ExternalServiceException(
            HTTPStatus.GATEWAY_TIMEOUT,
            [{"message": "Unable to get service account token.", "reason": err.with_traceback(None)}],
        ) from err
    except Exception as err:
        current_app.logger.debug("ACCOUNT SVC connection failure: %s", err.with_traceback(None))
        raise ExternalServiceException(
            HTTPStatus.SERVICE_UNAVAILABLE,
            [{"message": "Unable to get service account token.", "reason": err.with_traceback(None)}],
        ) from err


def user_info(token: str) -> dict:
    """Auth API call to get the stored user info."""
    return _call_auth_api("users/@me", token)


def user_orgs(token: str) -> dict:
    """Auth API call to get user organizations for the user identified by the token."""
    return _call_auth_api("users/orgs", token)


def account_org(token: str, account_id: str) -> dict:
    """Auth API call to get the account organization info identified by the account id."""
    if not account_id:
        return None
    return _call_auth_api(f"orgs/{account_id}", token)


def account_products(token: str, account_id: str) -> list[dict]:
    """Auth API call to get the account products of the org identified by the account id."""
    if not account_id:
        return None
    return _call_auth_api(f"orgs/{account_id}/products?include_hidden=true", token)


def is_staff(jwt: JwtManager) -> bool:
    """Return True if the user has the BC Registries staff role."""
    return jwt is not None and jwt.validate_roles(request_ctx.current_user, [STAFF_ROLE])


def is_system(jwt: JwtManager) -> bool:
    """Return True if the user has the BC Registries system role."""
    return jwt is not None and jwt.validate_roles(request_ctx.current_user, [SYSTEM_ROLE])
