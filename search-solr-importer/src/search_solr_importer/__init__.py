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
import logging
import logging.config
import os
from http import HTTPStatus

import sentry_sdk  # noqa: I001; pylint: disable=ungrouped-imports; conflicts with Flake8
from sentry_sdk.integrations.flask import FlaskIntegration  # noqa: I001
from flask import Flask  # noqa: I001
# from legal_api.models import db
from registry_schemas import __version__ as registry_schemas_version
from registry_schemas.flask import SchemaServices  # noqa: I001
from search_api.services import solr

from search_solr_importer import config
from search_solr_importer.logging import setup_logging
from search_solr_importer.oracle import oracle_db
from search_solr_importer.translations import babel
from search_solr_importer.version import __version__
# noqa: I003; the sentry import creates a bad line count in isort

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.conf'))  # important to do this first


def _get_build_openshift_commit_hash():
    return os.getenv('OPENSHIFT_BUILD_COMMIT', None)


def get_run_version():
    """Return a formatted version string for this service."""
    commit_hash = _get_build_openshift_commit_hash()
    if commit_hash:
        return f'{__version__}-{commit_hash}'
    return __version__


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {'app': app}

    app.shell_context_processor(shell_context)


def create_app(run_mode=os.getenv('FLASK_ENV', 'production')):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(config.CONFIGURATION[run_mode])

    # Configure Sentry
    if dsn := app.config.get('SENTRY_DSN'):
        sentry_sdk.init(  # pylint: disable=E0110
            dsn=dsn,
            integrations=[FlaskIntegration()],
            environment=app.config.get('POD_NAMESPACE'),
            release=f'search-solr-importer@{get_run_version()}',
            traces_sample_rate=app.config.get('SENTRY_TSR'))

    # db.init_app(app)
    oracle_db.init_app(app)
    solr.init_app(app)
    babel.init_app(app)

    register_shellcontext(app)

    return app
