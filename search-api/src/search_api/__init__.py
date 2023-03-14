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
"""The SEARCH API service.

This module is the API for the BC Registries Registry Search system.
"""
import asyncio
import logging
import logging.config
import os
from http import HTTPStatus

import sentry_sdk  # noqa: I001; pylint: disable=ungrouped-imports; conflicts with Flake8
from sentry_sdk.integrations.flask import FlaskIntegration  # noqa: I001
from flask import redirect, url_for, Flask  # noqa: I001
from flask_migrate import Migrate
from registry_schemas import __version__ as registry_schemas_version
from registry_schemas.flask import SchemaServices  # noqa: I001

from search_api import errorhandlers, models
from search_api.config import config
from search_api.models import db
from search_api.resources import v1_endpoint
from search_api.schemas import rsbc_schemas
from search_api.services import Flags, queue, search_solr
from search_api.translations import babel
from search_api.utils.auth import jwt
from search_api.utils.logging import set_log_level_by_flag, setup_logging
from search_api.utils.run_version import get_run_version
# noqa: I003; the sentry import creates a bad line count in isort

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.conf'))  # important to do this first
migrate = Migrate()  # pylint: disable=invalid-name


def create_app(config_name: str = os.getenv('APP_ENV') or 'production', **kwargs):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure Sentry
    if dsn := app.config.get('SENTRY_DSN'):
        sentry_sdk.init(  # pylint: disable=E0110
            dsn=dsn,
            integrations=[FlaskIntegration()],
            environment=app.config.get('POD_NAMESPACE'),
            release=f'search-api@{get_run_version()}',
            traces_sample_rate=app.config.get('SENTRY_TSR')
        )

    # td is testData instance passed in to support testing
    td = kwargs.get('ld_test_data', None)  # pylint: disable=invalid-name;
    Flags().init_app(app, td)

    errorhandlers.init_app(app)
    db.init_app(app)
    rsbc_schemas.init_app(app)
    queue.init_app(app)
    search_solr.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)

    v1_endpoint.init_app(app)
    setup_jwt_manager(app, jwt)

    @app.before_request
    def before_request():  # pylint: disable=unused-variable
        # do any common setup here
        # set logging level
        set_log_level_by_flag()

    @app.route('/')
    def be_nice_swagger_redirect():  # pylint: disable=unused-variable
        return redirect('/api/v1', code=HTTPStatus.MOVED_PERMANENTLY)

    @app.after_request
    def add_version(response):  # pylint: disable=unused-variable
        version = get_run_version()
        response.headers['API'] = f'search_api/{version}'
        response.headers['SCHEMAS'] = f'registry_schemas/{registry_schemas_version}'
        return response

    register_shellcontext(app)

    return app


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""
    def get_roles(a_dict):
        return a_dict['realm_access']['roles']  # pragma: no cover
    app.config['JWT_ROLE_CALLBACK'] = get_roles

    jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'app': app,
            'jwt': jwt,
            'db': db,
            'models': models}  # pragma: no cover

    app.shell_context_processor(shell_context)
