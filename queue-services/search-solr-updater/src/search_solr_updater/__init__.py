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
"""The Search Solr Updater service."""
import os
from http import HTTPStatus
from uuid import uuid4

from flask import Flask, current_app, redirect, request

from search_solr_updater.config import DevConfig, ProdConfig, TestConfig
from search_solr_updater.resources import ops_bp, worker_bp
from search_solr_updater.services import gcp_queue
from search_solr_updater.services.auth import auth_cache
from search_solr_updater.services.entity import entity_cache
from search_solr_updater.version import get_run_version
from structured_logging import StructuredLogging

CONFIG_MAP = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig
}


def create_app(environment: str = os.getenv("DEPLOYMENT_ENV", "production"), **kwargs):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.logger = StructuredLogging(app).get_logger().new(worker_id=str(uuid4()))
    app.config.from_object(CONFIG_MAP.get(environment, ProdConfig))

    gcp_queue.init_app(app)

    app.register_blueprint(ops_bp)
    app.register_blueprint(worker_bp)
    auth_cache.init_app(app)
    entity_cache.init_app(app)

    @app.route("/")
    def be_nice_swagger_redirect():
        return redirect("/api/v1", code=HTTPStatus.MOVED_PERMANENTLY)

    @app.before_request
    def add_logger_context():
        current_app.logger.debug("path: %s, app_name: %s, account_id: %s, api_key: %s",
                                 request.path,
                                 request.headers.get("app-name"),
                                 request.headers.get("account-id"),
                                 request.headers.get("x-apikey"))

    @app.after_request
    def add_version(response):
        version = get_run_version()
        response.headers["API"] = f"search_solr_updater/{version}"
        return response

    register_shellcontext(app)

    return app


def register_shellcontext(app: Flask):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {"app": app}

    app.shell_context_processor(shell_context)
