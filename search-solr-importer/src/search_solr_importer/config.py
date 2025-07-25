# Copyright © 2023 Province of British Columbia
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

from dotenv import find_dotenv, load_dotenv

# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())


class Config:
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SOLR_SVC_BUS_LEADER_CORE = os.getenv("SOLR_SVC_BUS_LEADER_CORE", "business")
    SOLR_SVC_BUS_FOLLOWER_CORE = os.getenv("SOLR_SVC_BUS_FOLLOWER_CORE", "business_follower")
    SOLR_SVC_BUS_LEADER_URL = os.getenv("SOLR_SVC_BUS_LEADER_URL", "http://localhost:8873/solr")
    SOLR_SVC_BUS_FOLLOWER_URL = os.getenv("SOLR_SVC_BUS_FOLLOWER_URL", "http://localhost:8874/solr")
    HAS_FOLLOWER = SOLR_SVC_BUS_FOLLOWER_URL != SOLR_SVC_BUS_LEADER_URL
    # Retry settings
    SOLR_RETRY_TOTAL = int(os.getenv("SOLR_RETRY_TOTAL", "2"))
    SOLR_RETRY_BACKOFF_FACTOR = int(os.getenv("SOLR_RETRY_BACKOFF_FACTOR", "5"))

    SEARCH_API_URL = os.getenv("SEARCH_API_INTERNAL_URL", "http://")
    SEARCH_API_V1 = os.getenv("SEARCH_API_VERSION", "")

    BATCH_SIZE = int(os.getenv("SOLR_BATCH_UPDATE_SIZE", "1000"))
    REINDEX_CORE = os.getenv("REINDEX_CORE", "False") == "True"
    PRELOADER_JOB = os.getenv("PRELOADER_JOB", "False") == "True"

    MODERNIZED_LEGAL_TYPES = os.getenv("MODERNIZED_LEGAL_TYPES", "BEN,CBEN,CP,GP,SP").upper().split(",")

    BATCH_SIZE_SOLR = int(os.getenv("SOLR_BATCH_UPDATE_SIZE", "1000"))
    BATCH_SIZE_SOLR_SI = int(os.getenv("SOLR_BATCH_UPDATE_SIZE_SI", "1000"))

    INCLUDE_BTR_LOAD = os.getenv("INCLUDE_BTR_LOAD", "False") == "True"
    INCLUDE_COLIN_LOAD = os.getenv("INCLUDE_COLIN_LOAD", "True") == "True"
    INCLUDE_LEAR_LOAD = os.getenv("INCLUDE_LEAR_LOAD", "True") == "True"
    RESYNC_OFFSET = os.getenv("RESYNC_OFFSET", "130")

    BTR_BATCH_LIMIT = int(os.getenv("BTR_BATCH_LIMIT", "100000"))

    # TODO: or not include btr
    IS_PARTIAL_IMPORT = not INCLUDE_COLIN_LOAD or not INCLUDE_LEAR_LOAD

    # Service account details
    ACCOUNT_SVC_AUTH_URL = os.getenv("ACCOUNT_SVC_AUTH_URL")
    ACCOUNT_SVC_CLIENT_ID = os.getenv("ACCOUNT_SVC_CLIENT_ID")
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv("ACCOUNT_SVC_CLIENT_SECRET")
    try:
        ACCOUNT_SVC_TIMEOUT = int(os.getenv("AUTH_API_TIMEOUT", "20"))
    except:  # pylint: disable=bare-except;
        ACCOUNT_SVC_TIMEOUT = 20

    # ORACLE - CDEV/CTST/CPRD
    ORACLE_USER = os.getenv("ORACLE_USER", "")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
    ORACLE_DB_NAME = os.getenv("ORACLE_DB_NAME", "")
    ORACLE_HOST = os.getenv("ORACLE_HOST", "")
    ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))

    # POSTGRESQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_HOST = os.getenv("DATABASE_HOST_LEAR", "")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_CONNECTION_NAME = os.getenv("DATABASE_CONNECTION_NAME")  # project:region:instance-name
    GOOGLE_APPLICATION_CREDENTIALS_LEAR = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_LEAR", "sa-secret/sa-importer-key-lear-dev.json")

    BTR_DB_USER = os.getenv("DATABASE_USERNAME_BTR", "")
    BTR_DB_PASSWORD = os.getenv("DATABASE_PASSWORD_BTR", "")
    BTR_DB_NAME = os.getenv("DATABASE_NAME_BTR", "")
    BTR_DB_HOST = os.getenv("DATABASE_HOST_BTR", "")
    BTR_DB_PORT = os.getenv("DATABASE_PORT_BTR", "5432")
    BTR_DB_CONNECTION_NAME = os.getenv("DATABASE_CONNECTION_NAME_BTR")  # project:region:instance-name
    GOOGLE_APPLICATION_CREDENTIALS_BTR = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BTR", "sa-secret/sa-importer-key-btr-dev.json")

    # Connection pool settings
    DB_MIN_POOL_SIZE = os.getenv("DATABASE_MIN_POOL_SIZE", "2")
    DB_MAX_POOL_SIZE = os.getenv("DATABASE_MAX_POOL_SIZE", "10")
    DB_CONN_WAIT_TIMEOUT = os.getenv("DATABASE_CONN_WAIT_TIMEOUT", "5")
    DB_CONN_TIMEOUT = os.getenv("DATABASE_CONN_TIMEOUT", "900")

    SQLALCHEMY_ENGINE_OPTIONS = {  # noqa: RUF012
        "pool_pre_ping": True,
        "pool_size": int(DB_MIN_POOL_SIZE),
        "max_overflow": (int(DB_MAX_POOL_SIZE) - int(DB_MIN_POOL_SIZE)),
        "pool_recycle": int(DB_CONN_TIMEOUT),
        "pool_timeout": int(DB_CONN_WAIT_TIMEOUT)
    }

    # Event tracking max retries before human intervention.
    EVENT_MAX_RETRIES: int = int(os.getenv("EVENT_MAX_RETRIES", "3"))

    # temp migration vars
    BUSINESSES_MANAGED_BY_COLIN = (os.getenv("BUSINESSES_MANAGED_BY_COLIN", "")).split(",")


class DevelopmentConfig(Config):
    """Config object for development environment."""

    DEBUG = True
    DEVELOPMENT = True
    TESTING = False


class UnitTestingConfig(Config):
    """Config object for unit testing environment."""

    DEBUG = True
    DEVELOPMENT = False
    TESTING = True
    # TODO: update these when tests are ready
    INCLUDE_BTR_LOAD = False
    INCLUDE_COLIN_LOAD = False
    INCLUDE_LEAR_LOAD = False
    # SOLR
    SOLR_SVC_BUS_LEADER_CORE = os.getenv("TEST_SOLR_SVC_BUS_LEADER_CORE", "business")
    SOLR_SVC_BUS_FOLLOWER_CORE = os.getenv("TEST_SOLR_SVC_BUS_FOLLOWER_CORE", "business_follower")
    SOLR_SVC_BUS_LEADER_URL = os.getenv("TEST_SOLR_SVC_BUS_LEADER_URL", "http://test.leader.fake")
    SOLR_SVC_BUS_FOLLOWER_URL = os.getenv("TEST_SOLR_SVC_BUS_FOLLOWER_URL", "http://test.follower.fake")
    HAS_FOLLOWER = SOLR_SVC_BUS_FOLLOWER_URL != SOLR_SVC_BUS_LEADER_URL

    SEARCH_API_URL = "http://test.SEARCH_API_URL.fake"
    SEARCH_API_V1 = os.getenv("REGISTRIES_SEARCH_API_VERSION", "")

    # Service account details
    ACCOUNT_SVC_AUTH_URL = "http://test.account-svc-url.fake"

    # ORACLE - CDEV/CTST/CPRD
    ORACLE_USER = os.getenv("ORACLE_TEST_USER", "")
    ORACLE_PASSWORD = os.getenv("ORACLE_TEST_PASSWORD", "")
    ORACLE_DB_NAME = os.getenv("ORACLE_TEST_DB_NAME", "")
    ORACLE_HOST = os.getenv("ORACLE_TEST_HOST", "")
    ORACLE_PORT = int(os.getenv("ORACLE_TEST_PORT", "1521"))

    DB_USER = os.getenv("DATABASE_TEST_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_TEST_NAME", "")
    DB_HOST = os.getenv("DATABASE_TEST_HOST_LEAR", "")
    DB_PORT = os.getenv("DATABASE_TEST_PORT", "5432")
    DB_CONNECTION_NAME = os.getenv("DATABASE_TEST_CONNECTION_NAME")

    BTR_DB_USER = os.getenv("DATABASE_TEST_USERNAME_BTR", "")
    BTR_DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD_BTR", "")
    BTR_DB_NAME = os.getenv("DATABASE_TEST_NAME_BTR", "")
    BTR_DB_HOST = os.getenv("DATABASE_TEST_HOST_BTR", "")
    BTR_DB_PORT = os.getenv("DATABASE_TEST_PORT_BTR", "5432")
    BTR_DB_CONNECTION_NAME = os.getenv("DATABASE_TEST_CONNECTION_NAME_BTR")


class ProductionConfig(Config):
    """Config object for production environment."""

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
