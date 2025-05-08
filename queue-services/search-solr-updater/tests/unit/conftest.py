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
"""Common setup and fixtures for the pytest suite used by this service."""
import os
import random
import time
from contextlib import contextmanager

import pytest
from flask import Flask

from search_solr_updater import create_app
from search_solr_updater.services.auth import auth_cache
from search_solr_updater.services.entity import entity_cache

os.environ['DEPLOYMENT_ENV'] = 'testing'


@contextmanager
def not_raises(exception):
    """Corallary to the pytest raises builtin.

    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except exception:
        raise pytest.fail(f'DID RAISE {exception}')


@pytest.fixture(scope='session')
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')
    with _app.app_context():
        yield _app


@pytest.fixture(scope='session')
def client(app: Flask):
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the caches before and after each test run."""
    auth_cache.clear()
    entity_cache.clear()
    yield
    auth_cache.clear()
    entity_cache.clear()
