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
"""This maintains access tokens for API calls."""
import base64
import functools
import json
import os

import google.auth.transport.requests
import google.oauth2.id_token as id_token

from cachecontrol import CacheControl
from flask import abort, current_app, request
from google.oauth2 import service_account
from http import HTTPStatus
from requests.sessions import Session

from search_api.services.gcp_auth.abstract_auth_service import AuthService


class GoogleAuthService(AuthService):  # pylint: disable=too-few-public-methods
    """Google Auth Service implementation.

    Maintains a wrapper to get a service account access token and credentials for Google API calls.
    """

    # Google APIs and cloud storage os.getenv('GCP
    GOOGLE_DEFAULT_SERVICE_ACCOUNT = os.getenv('GOOGLE_DEFAULT_SERVICE_ACCOUNT')
    # https://developers.google.com/identity/protocols/oauth2/scopes
    GCP_SA_SCOPES = [os.getenv('GCP_CS_SA_SCOPES', 'https://www.googleapis.com/auth/cloud-platform')]

    service_account_info = None
    credentials = None
    # Use service account env var if available.
    if GOOGLE_DEFAULT_SERVICE_ACCOUNT:
        sa_bytes = bytes(GOOGLE_DEFAULT_SERVICE_ACCOUNT, 'utf-8')
        service_account_info = json.loads(base64.b64decode(sa_bytes.decode('utf-8')))
    # Otherwise leave as none and use the service account attached to the Cloud service.

    @classmethod
    def get_token(cls):
        """Generate an OAuth access token with cloud storage access."""
        if cls.credentials is None:
            cls.credentials = service_account.Credentials.from_service_account_info(cls.service_account_info,
                                                                                    scopes=cls.GCP_SA_SCOPES)
        request = google.auth.transport.requests.Request()
        cls.credentials.refresh(request)
        current_app.logger.info('Call successful: obtained token.')
        return cls.credentials.token

    @classmethod
    def get_credentials(cls):
        """Generate GCP auth credentials to pass to a GCP client."""
        if cls.credentials is None:
            cls.credentials = service_account.Credentials.from_service_account_info(cls.service_account_info,
                                                                                    scopes=cls.GCP_SA_SCOPES)
        current_app.logger.info('Call successful: obtained credentials.')
        return cls.credentials


def verify_jwt(session):
    """Check token is valid with the correct audience and email claims for configured email address."""
    try:
        jwt_token = request.headers.get('Authorization', '').split()[1]
        claims = id_token.verify_oauth2_token(
            jwt_token,
            google.auth.transport.requests.Request(session=session),
            audience=current_app.config.get('PAY_AUDIENCE_SUB')
        )
        required_emails = current_app.config.get('VERIFY_PUBSUB_EMAILS')
        if claims.get('email_verified') and claims.get('email') in required_emails:
            return None
        else:
            return 'Email not verified or does not match', 401
    except Exception as e:
        current_app.logger.info(f'Invalid token {e}')
        return f'Invalid token: {e}', 400


def ensure_authorized_queue_user(f):
    """Ensures the user is authorized to use the queue."""

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Use CacheControl to avoid re-fetching certificates for every request.
        if verify_jwt(CacheControl(Session())):
            abort(HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)

    return decorated_function
