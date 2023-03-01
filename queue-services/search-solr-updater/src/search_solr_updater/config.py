# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here.

All items are loaded, or have Constants defined here that
are loaded into the Flask configuration.
All modules and lookups get their configuration from the
Flask config, rather than reading environment variables directly
or by accessing this configuration directly.
"""
import os
import random

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'search_solr_updater.config.DevConfig',
    'testing': 'search_solr_updater.config.TestConfig',
    'production': 'search_solr_updater.config.ProdConfig',
    'default': 'search_solr_updater.config.ProdConfig'
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        app_config = ProdConfig()
    elif config_name == 'testing':
        app_config = TestConfig()
    elif config_name == 'development':
        app_config = DevConfig()
    else:
        raise KeyError(f'Unknown configuration: {config_name}')
    return app_config


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    POD_NAMESPACE = os.getenv('POD_NAMESPACE', 'unknown')

    SENTRY_ENABLE = os.getenv('SENTRY_ENABLE', 'False')
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)
    SENTRY_TSR = os.getenv('SENTRY_TSR', '1.0')

    NATS_CONNECTION_OPTIONS = {
        'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
        'name': os.getenv('NATS_SEARCH_SOLR_CLIENT_NAME', 'search.solr.worker')
    }

    STAN_CONNECTION_OPTIONS = {
        'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
        'client_id': str(random.SystemRandom().getrandbits(0x58)),
        'ping_interval': 1,
        'ping_max_out': 5,
    }

    SUBSCRIPTION_OPTIONS = {
        'subject': os.getenv('NATS_ENTITY_EVENTS_SUBJECT', 'entity.events'),
        'queue': os.getenv('NATS_SEARCH_SOLR_QUEUE', 'search-solr-worker'),
        'durable_name': os.getenv('NATS_SEARCH_SOLR_QUEUE', 'search-solr-worker') + '_durable'
    }

    LEAR_SVC_URL = os.getenv('LEGAL_API_URL', 'http://') + os.getenv('LEGAL_API_VERSION_2', '/api/v2')
    SEARCH_API_URL = os.getenv('REGISTRIES_SEARCH_API_INTERNAL_URL') \
        + os.getenv('REGISTRIES_SEARCH_API_VERSION', '/api/v1')

    # External API Timeouts
    try:
        AUTH_API_TIMEOUT = int(os.getenv('AUTH_API_TIMEOUT', '30'))
    except:  # pylint: disable=bare-except; # noqa: B901, E722
        AUTH_API_TIMEOUT = 30
    try:
        BUSINESS_API_TIMEOUT = int(os.getenv('BUSINESS_API_TIMEOUT', '30'))
    except:  # pylint: disable=bare-except; # noqa: B901, E722
        BUSINESS_API_TIMEOUT = 30

    # Service account details
    KEYCLOAK_AUTH_TOKEN_URL = os.getenv('KEYCLOAK_AUTH_TOKEN_URL')
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('BUSINESS_SEARCH_SERVICE_ACCOUNT_CLIENT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('BUSINESS_SEARCH_SERVICE_ACCOUNT_SECRET')


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Creates the Development Config object."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True

    SENTRY_ENABLE = 'false'
    STAN_CLUSTER_NAME = 'test-cluster'
    SEARCH_API_URL = os.getenv('TEST_REGISTRIES_SEARCH_API_INTERNAL_URL', 'http://search_api_url.test')


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
