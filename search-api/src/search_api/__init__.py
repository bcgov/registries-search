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
import os
from http import HTTPStatus

from flask import Flask, redirect
from flask_migrate import Migrate
from structured_logging import StructuredLogging

from search_api import errorhandlers, models
from search_api.config import DevelopmentConfig, MigrationConfig, ProductionConfig, UnitTestingConfig
from search_api.models import db
from search_api.resources import v1_endpoint, v2_endpoint
from search_api.services import Flags, business_solr, queue
from search_api.translations import babel
from search_api.utils.auth import jwt
from search_api.utils.run_version import get_run_version


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'testing': UnitTestingConfig,
    'migration': MigrationConfig,
    'production': ProductionConfig
}


def create_app(environment: str = os.getenv('DEPLOYMENT_ENV', 'production'), **kwargs):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.logger = StructuredLogging().get_logger()
    app.config.from_object(CONFIG_MAP.get(environment, 'production'))

    if environment == 'migration':
        Migrate(app, db)

    else:
        # td is testData instance passed in to support testing
        td = kwargs.get('ld_test_data', None)  # pylint: disable=invalid-name;
        Flags().init_app(app, td)

        errorhandlers.init_app(app)
        db.init_app(app)
        queue.init_app(app)
        business_solr.init_app(app)
        babel.init_app(app)

        v1_endpoint.init_app(app)
        v2_endpoint.init_app(app)
        setup_jwt_manager(app, jwt)

    @app.route('/')
    def be_nice_swagger_redirect():  # pylint: disable=unused-variable
        return redirect('/api/v1', code=HTTPStatus.MOVED_PERMANENTLY)

    @app.after_request
    def add_version(response):  # pylint: disable=unused-variable
        version = get_run_version()
        response.headers['API'] = f'search_api/{version}'
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
