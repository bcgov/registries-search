# Copyright © 2023 Daxiom™ Systems Inc.
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
"""Feature flag wrapper for Flask."""
from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

import ldclient
from flask import Flask, current_app
from ldclient import Config, Context, LDClient

import search_api
from search_api.services.authz import get_role

if TYPE_CHECKING:
    from ldclient.integrations.test_data import TestData

    from search_api.utils.auth import JwtManager


class Flags:
    """Wrapper around the feature flag system.

    1 client per application.
    """

    COMPONENT_NAME = "featureflags"

    def __init__(self, app: Flask = None):
        """Initialize this object."""
        self.sdk_key = None
        self.app = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask, td: TestData = None):
        """Initialize the Feature Flag environment.

        Provide TD for TestData.
        """
        self.app = app
        self.sdk_key = app.config.get("LD_SDK_KEY")
        if td:
            client = LDClient(config=Config("testing", update_processor_class=td))
        elif self.sdk_key:
            ldclient.set_config(Config(self.sdk_key))
            client = ldclient.get()

        try:
            if client and client.is_initialized():
                app.extensions[Flags.COMPONENT_NAME] = client
                app.teardown_appcontext(self.teardown)
        except Exception as err:
            app.logger.warning("Issue registering flag service %s", err)

    def teardown(self, exception):
        """Destroy all objects created by this extension.

        Ensure we close the client connection nicely.
        """
        with suppress(Exception):
            if client := current_app.extensions.get(Flags.COMPONENT_NAME):
                client.close()

    @staticmethod
    def get_client():
        """Get the currently configured ldclient."""
        with suppress(KeyError):
            client = current_app.extensions[Flags.COMPONENT_NAME]
            return client

        try:
            return ldclient.get()
        except Exception:
            return None

    @staticmethod
    def flag_user(user: search_api.models.User,
                  account_id: int | None = None,
                  jwt: JwtManager | None = None):
        """Convert User into a Flag user dict."""
        if not isinstance(user, search_api.models.User):
            return None

        _user = {
            "key": user.sub,
            "firstName": user.firstname,
            "lastName": user.lastname,
            "email": user.email,
            "custom": {
                "loginSource": user.login_source,
            }
        }
        with suppress(Exception):
            if account_id and jwt:
                _user["custom"]["group"] = get_role(jwt, account_id)

        return _user

    @staticmethod
    def get_anonymous_user():
        """Return an anonymous key."""
        return {"key": "anonymous"}

    @staticmethod
    def value(flag: str, user=None):
        """Retrieve the value  of the (flag, user) tuple."""
        try:
            client = Flags.get_client()
            flag_user = user if user else Flags.get_anonymous_user()
            flag_context = Context.from_dict({**flag_user, "kind": "user"})
            return client.variation(flag, flag_context, None)
        except Exception as err:
            current_app.logger.error("Unable to read flags: %s", repr(err), exc_info=True)
            return None
