# Copyright © 2024 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the "License");
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    https://opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Auth Services."""
from http import HTTPStatus

import requests
from flask import current_app, request
from flask_caching import Cache
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token
from requests import exceptions

from search_solr_updater.exceptions import BusinessException, ExternalServiceException

auth_cache = Cache()


def verify_gcp_jwt():
    """Verify the bearer token as sign by gcp oauth."""
    try:
        bearer_token = request.headers.get("Authorization")
        current_app.logger.debug("bearer_token %s", bearer_token)
        token = bearer_token.split(" ")[1]
        audience = current_app.config.get("SUB_AUDIENCE")
        current_app.logger.debug("audience %s", audience)
        claim = id_token.verify_oauth2_token(
            token, google_auth_requests.Request(), audience=audience
        )
        sa_email = current_app.config.get("SUB_SERVICE_ACCOUNT")
        current_app.logger.debug("sa_email %s", sa_email)
        if not claim["email_verified"] or claim["email"] != sa_email:
            raise BusinessException(f"Invalid service account or email not verified for email: {claim['email']}")

    except Exception as err:
        raise BusinessException(f"Invalid token: {err}") from err


@auth_cache.cached(timeout=300, key_prefix="view/token")
def get_bearer_token():
    """Get a valid Bearer token for the service to use."""
    data = "grant_type=client_credentials"
    try:
        res = requests.post(
            url=current_app.config["ACCOUNT_SVC_AUTH_URL"],
            data=data,
            headers={"content-type": "application/x-www-form-urlencoded"},
            auth=(current_app.config["ACCOUNT_SVC_CLIENT_ID"], current_app.config["ACCOUNT_SVC_CLIENT_SECRET"]),
            timeout=current_app.config["ACCOUNT_SVC_TIMEOUT"]
        )
        if res.status_code != HTTPStatus.OK:
            raise ConnectionError({"statusCode": res.status_code, "json": res.json()})
        return res.json().get("access_token")
    except exceptions.Timeout as err:
        current_app.logger.debug("Account service connection timeout: %s", err.with_traceback(None))
        raise ExternalServiceException(
            status_code=HTTPStatus.GATEWAY_TIMEOUT,
            error=err.with_traceback(None),
            message="Unable to get service account token.",
        ) from err
    except Exception as err:
        current_app.logger.debug("Account service connection failure: %s", err.with_traceback(None))
        raise ExternalServiceException(
            status_code=HTTPStatus.GATEWAY_TIMEOUT,
            error=err.with_traceback(None),
            message="Unable to get service account token.",
        ) from err



