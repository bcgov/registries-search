# Copyright © 2025 Province of British Columbia
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
"""All of the configuration for the service is captured here."""
import os
import sys

from dotenv import find_dotenv, load_dotenv

# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())


class _Config:
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    LEAR_SVC_URL = os.getenv("BUSINESS_API_URL", "http://") + os.getenv("BUSINESS_API_VERSION_2", "/api/v2")
    LEAR_SVC_TIMEOUT = int(os.getenv("BUSINESS_SVC_TIMEOUT", "20"))
    SEARCH_SVC_URL = os.getenv("SEARCH_API_INTERNAL_URL") + os.getenv("SEARCH_API_VERSION", "/api/v1")
    SEARCH_SVC_TIMEOUT = int(os.getenv("SEARCH_SVC_TIMEOUT", "30"))

    # Service account details
    ACCOUNT_SVC_AUTH_URL = os.getenv("ACCOUNT_SVC_AUTH_URL", None)
    ACCOUNT_SVC_CLIENT_ID = os.getenv("ACCOUNT_SVC_CLIENT_ID", None)
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv("ACCOUNT_SVC_CLIENT_SECRET", None)
    ACCOUNT_SVC_TIMEOUT = int(os.getenv("ACCOUNT_SVC_TIMEOUT", "20"))

    # pub/sub
    SUB_AUDIENCE = os.getenv("SUB_AUDIENCE", "")
    SUB_SERVICE_ACCOUNT = os.getenv("SUB_SERVICE_ACCOUNT", "")

    # flask caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", "FileSystemCache")
    CACHE_DIR = os.getenv("CACHE_DIR", "cache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))


class DevConfig(_Config):
    """Creates the Development Config object."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True

    LEAR_SVC_URL = os.getenv("TEST_LEGAL_API_URL", "http://legal_api_url.test")
    SEARCH_API_URL = os.getenv("TEST_REGISTRIES_SEARCH_API_INTERNAL_URL", "http://search_api_url.test")
    ACCOUNT_SVC_AUTH_URL = os.getenv("TEST_KEYCLOAK_AUTH_TOKEN_URL", "http://kc_url.test")


class ProdConfig(_Config):
    """Production environment configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print("WARNING: SECRET_KEY being set as a one-shot", file=sys.stderr)  # noqa: T201

    TESTING = False
    DEBUG = False
