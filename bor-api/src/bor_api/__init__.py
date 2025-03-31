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
"""The BOR API service.

This module is the API for the BC Beneficial Ownership Search system.
"""
import os
import uuid
from http import HTTPStatus

from flask import Flask, current_app, redirect, request
from flask_migrate import Migrate

from bor_api import errorhandlers, models
from bor_api.config import DevelopmentConfig, MigrationConfig, ProductionConfig, UnitTestingConfig
from bor_api.models import db
from bor_api.resources import v1_endpoint
from bor_api.services import Flags, jwt, solr
from bor_api.services.authz import auth_cache
from bor_api.utils.run_version import get_run_version
from structured_logging import StructuredLogging

CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": UnitTestingConfig,
    "migration": MigrationConfig,
    "production": ProductionConfig,
}


def create_app(environment: str = os.getenv("DEPLOYMENT_ENV", "production"), **kwargs):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.logger = StructuredLogging(app).get_logger().new(worker_id=str(uuid.uuid4()))
    app.config.from_object(CONFIG_MAP.get(environment, "production"))

    db.init_app(app)

    if environment == "migration":
        Migrate(app, db)

    else:
        solr.init_app(app)
        errorhandlers.init_app(app)
        v1_endpoint.init_app(app)
        # td is testData instance passed in to support testing
        td = kwargs.get("ld_test_data")
        Flags().init_app(app, td)
        setup_jwt_manager(app, jwt)

        auth_cache.init_app(app)

    @app.route("/")
    def be_nice_swagger_redirect():
        return redirect("/api/v1", code=HTTPStatus.MOVED_PERMANENTLY)

    @app.after_request
    def add_version(response):
        version = get_run_version()
        response.headers["API"] = f"bor_api/{version}"
        return response
    
    @app.before_request
    def add_logger_context():
        # TODO: bind this to the logger within the context without replacing it on all threads
        # app.logger = logger.bind(
        #     thread_id=str(uuid.uuid4())
        #     path=request.path,
        #     account_id=request.headers.get('account-id'),
        #     app_name=request.headers.get('app-name'),
        #     api_key=request.headers.get('x-apikey')
        # )
        current_app.logger.debug("path: %s, app_name: %s, account_id: %s, api_key: %s",
                                 request.path,
                                 request.headers.get("app-name"),
                                 request.headers.get("account-id"),
                                 request.headers.get("x-apikey"))

    register_shellcontext(app)

    return app


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""

    def get_roles(a_dict):
        return a_dict["realm_access"]["roles"]  # pragma: no cover

    app.config["JWT_ROLE_CALLBACK"] = get_roles

    jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"app": app, "jwt": jwt, "db": db, "models": models}  # pragma: no cover

    app.shell_context_processor(shell_context)
