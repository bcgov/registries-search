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
from contextlib import contextmanager, suppress

import pytest
from ldclient.integrations.test_data import TestData

from search_api import create_app
from search_api import jwt as _jwt
from search_api.models import db as _db


@contextmanager
def not_raises(exception):
    """Corollary to the pytest raises builtin.

    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except exception:
        raise pytest.fail(f'DID RAISE {exception}')


@pytest.fixture(scope='session')
def ld():
    """LaunchDarkly TestData source."""
    td = TestData.data_source()
    yield td


@pytest.fixture(scope='session')
def app(ld):
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('unitTesting', **{'ld_test_data': ld})
    
    with _app.app_context():
        yield _app


@pytest.fixture
def set_env(app):
    """Factory to set environment and Flask config variables."""
    def _set_env(name, value):
        os.environ[name] = value
        app.config[name] = value

    return _set_env


@pytest.fixture(scope='function')
def client(app):  # pylint: disable=redefined-outer-name
    """Return a function-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def jwt():
    """Return a session-wide jwt manager."""
    return _jwt


@pytest.fixture(scope='session')
def db(app, request):  # pylint: disable=redefined-outer-name, invalid-name
    """Session-wide test database."""
    def teardown():
        _db.drop_all()
    _db.app = app

    _db.create_all()
    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Return a function-scoped session."""
    db.session.begin_nested()
    def commit():
        db.session.flush()
    # patch commit method
    old_commit = db.session.commit
    db.session.commit = commit
    def teardown():
        db.session.rollback()
        db.session.close()
        db.session.commit = old_commit
    request.addfinalizer(teardown)
    return db.session
