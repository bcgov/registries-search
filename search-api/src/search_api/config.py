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
import json
import os


class Config:
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    # Used by /sync endpoint
    MAX_BATCH_UPDATE_NUM = int(os.getenv("MAX_BATCH_UPDATE_NUM", "1000"))
    # Used by /sync heartbeat
    LAST_REPLICATION_THRESHOLD = int(os.getenv("LAST_REPLICATION_THRESHOLD", "24"))  # hours
    # Used by /businesses/bulk endpoint (NOTE: this value must be less than the solr instance max boolean clauses - default: 1024)
    MAX_BULK_SEARCH_VALUES = int(os.getenv("MAX_BULK_SEARCH_VALUES", "1000"))

    SOLR_SVC_BUS_LEADER_CORE = os.getenv("SOLR_SVC_BUS_LEADER_CORE", "business")
    SOLR_SVC_BUS_FOLLOWER_CORE = os.getenv("SOLR_SVC_BUS_FOLLOWER_CORE", "business_follower")
    SOLR_SVC_BUS_LEADER_URL = os.getenv("SOLR_SVC_BUS_LEADER_URL", "http://localhost:8873/solr")
    SOLR_SVC_BUS_FOLLOWER_URL = os.getenv("SOLR_SVC_BUS_FOLLOWER_URL", "http://localhost:8873/solr")
    SOLR_SVC_BUS_MAX_ROWS = int(os.getenv("SOLR_SVC_BUS_MAX_ROWS", "10000"))
    # Retry settings
    SOLR_RETRY_TOTAL = int(os.getenv("SOLR_RETRY_TOTAL", "2"))
    SOLR_RETRY_BACKOFF_FACTOR = int(os.getenv("SOLR_RETRY_BACKOFF_FACTOR", "5"))

    PAYMENT_SVC_URL = os.getenv("PAY_API_URL", "http://") + os.getenv("PAY_API_VERSION", "/api/v1")
    AUTH_SVC_URL = os.getenv("AUTH_API_URL", "http://") + os.getenv("AUTH_API_VERSION", "/api/v1")
    LEAR_SVC_URL = os.getenv("LEGAL_API_URL", "http://") + os.getenv("LEGAL_API_VERSION_2", "/api/v2")

    # Flask-Pub
    FLASK_PUB_CONFIG = {"plugins": [{"gcp": "gcp-pub-sub"}, ]}  # noqa: RUF012
    FLASK_PUB_DEFAULT_SUBJECT = "projects/unique-project-id/topics/simpleTopicName"
    QUEUE_PROJECT_ID = os.getenv("QUEUE_PROJECT_ID", "12345")
    QUEUE_TOPIC = os.getenv("QUEUE_TOPIC", "doc-test")

    # Cache stuff # flask cache uses these internally as defaults when instantiating cache with no config options
    # e.g. like this: Cache()
    CACHE_TYPE = os.getenv("CACHE_TYPE", "FileSystemCache")
    CACHE_DIR = os.getenv("CACHE_DIR", "cache")
    try:
        CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    except (TypeError, ValueError):
        CACHE_DEFAULT_TIMEOUT = 300

    LD_SDK_KEY = os.getenv("LD_SDK_KEY", None)

    # Flag Names
    FF_QUEUE_DOC_REQUEST_NAME = os.getenv("FF_QUEUE_DOC_REQUEST_NAME", None)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALEMBIC_INI = "migrations/alembic.ini"

    # External API Timeouts
    try:
        AUTH_API_TIMEOUT = int(os.getenv("AUTH_API_TIMEOUT", "20"))
    except:  # pylint: disable=bare-except;
        AUTH_API_TIMEOUT = 20
    try:
        PAY_API_TIMEOUT = int(os.getenv("PAY_API_TIMEOUT", "20"))
    except:  # pylint: disable=bare-except;
        PAY_API_TIMEOUT = 20
    try:
        BUSINESS_API_TIMEOUT = int(os.getenv("BUSINESS_API_TIMEOUT", "20"))
    except:  # pylint: disable=bare-except;
        BUSINESS_API_TIMEOUT = 20

    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_HOST = os.getenv("DATABASE_HOST", "")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")  # POSTGRESQL
    # POSTGRESQL
    if DB_UNIX_SOCKET := os.getenv("DATABASE_UNIX_SOCKET", None):
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Connection pool settings
    DB_MIN_POOL_SIZE = os.getenv("DATABASE_MIN_POOL_SIZE", "2")
    DB_MAX_POOL_SIZE = os.getenv("DATABASE_MAX_POOL_SIZE", "10")
    DB_CONN_WAIT_TIMEOUT = os.getenv("DATABASE_CONN_WAIT_TIMEOUT", "5")
    DB_CONN_TIMEOUT = os.getenv("DATABASE_CONN_TIMEOUT", "900")

    SQLALCHEMY_ENGINE_OPTIONS = {  # noqa: RUF012
        "pool_pre_ping": True,
        # 'echo_pool': 'debug',  # noqa: ERA001
        "pool_size": int(DB_MIN_POOL_SIZE),
        "max_overflow": (int(DB_MAX_POOL_SIZE) - int(DB_MIN_POOL_SIZE)),
        "pool_recycle": int(DB_CONN_TIMEOUT),
        "pool_timeout": int(DB_CONN_WAIT_TIMEOUT)
    }

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv("JWT_OIDC_WELL_KNOWN_CONFIG")
    JWT_OIDC_ALGORITHMS = os.getenv("JWT_OIDC_ALGORITHMS")
    JWT_OIDC_JWKS_URI = os.getenv("JWT_OIDC_JWKS_URI")
    JWT_OIDC_ISSUER = os.getenv("JWT_OIDC_ISSUER")
    JWT_OIDC_AUDIENCE = os.getenv("JWT_OIDC_AUDIENCE")
    JWT_OIDC_CLIENT_SECRET = os.getenv("JWT_OIDC_CLIENT_SECRET")
    JWT_OIDC_CACHING_ENABLED = os.getenv("JWT_OIDC_CACHING_ENABLED")
    JWT_OIDC_TOKEN_URL = os.getenv("JWT_OIDC_TOKEN_URL")
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv("JWT_OIDC_JWKS_CACHE_TIMEOUT"))
        if not JWT_OIDC_JWKS_CACHE_TIMEOUT:
            JWT_OIDC_JWKS_CACHE_TIMEOUT = 300
    except (TypeError, ValueError):
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300

    JWT_OIDC_USERNAME = os.getenv("JWT_OIDC_USERNAME", "username")
    JWT_OIDC_FIRSTNAME = os.getenv("JWT_OIDC_FIRSTNAME", "firstname")
    JWT_OIDC_LASTNAME = os.getenv("JWT_OIDC_LASTNAME", "lastname")
    JWT_OIDC_ACCOUNT_ID = os.getenv("JWT_OIDC_ACCOUNT_ID", "Account-Id")
    JWT_OIDC_LOGIN_SOURCE = os.getenv("JWT_OIDC_LOGIN_SOURCE", "loginSource")
    JWT_OIDC_API_GW = os.getenv("JWT_OIDC_API_GW", "API_GW")

    # service accounts
    ACCOUNT_SVC_AUTH_URL = os.getenv("ACCOUNT_SVC_AUTH_URL")
    ACCOUNT_SVC_CLIENT_ID = os.getenv("ACCOUNT_SVC_CLIENT_ID")
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv("ACCOUNT_SVC_CLIENT_SECRET")

    # Event tracking max retries before human intervention.
    EVENT_MAX_RETRIES: int = int(os.getenv("EVENT_MAX_RETRIES", "3"))

    # Google APIs and cloud storage
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_SA_CLIENT_EMAIL = os.getenv("GCP_SA_CLIENT_EMAIL")
    GCP_SA_CLIENT_ID = os.getenv("GCP_SA_CLIENT_ID")
    GCP_SA_PRIVATE_KEY = os.getenv("GCP_SA_PRIVATE_KEY")
    # https://developers.google.com/identity/protocols/oauth2/scopes
    GCP_SA_SCOPES = json.loads(os.getenv("GCP_SA_SCOPES", '["https://www.googleapis.com/auth/cloud-platform"]'))

    GATEWAY_URL = os.getenv("GATEWAY_URL", "https://bcregistry-dev.apigee.net")
    SUBSCRIPTION_API_KEY = os.getenv("SUBSCRIPTION_API_KEY")

    # cc gcloud listener payments vars
    PAY_AUDIENCE_SUB = os.getenv("PAY_AUDIENCE_SUB")
    VERIFY_PUBSUB_EMAILS = os.getenv("VERIFY_PUBSUB_EMAILS", "").split(",")

    try:
        DOCUMENT_REQUEST_DAYS_DURATION = int(os.getenv("DOCUMENT_REQUEST_DAYS_DURATION", "14"))
    except:
        DOCUMENT_REQUEST_DAYS_DURATION = 14


class DevelopmentConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for development environment."""

    DEBUG = True
    DEVELOPMENT = True
    TESTING = False


class UnitTestingConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for unit testing environment."""

    DEBUG = True
    DEVELOPMENT = False
    TESTING = True
    # SOLR
    SOLR_SVC_BUS_LEADER_CORE = os.getenv("SOLR_SVC_BUS_LEADER_TEST_CORE", "business")
    SOLR_SVC_BUS_FOLLOWER_CORE = os.getenv("SOLR_SVC_BUS_FOLLOWER_TEST_CORE", "business")
    SOLR_SVC_BUS_LEADER_URL = os.getenv("SOLR_SVC_BUS_LEADER_TEST_URL", "http://localhost:8980/solr")
    SOLR_SVC_BUS_FOLLOWER_URL = os.getenv("SOLR_SVC_BUS_FOLLOWER_TEST_URL", "http://localhost:8980/solr")
    SOLR_RETRY_TOTAL = 0
    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_TEST_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_TEST_NAME", "")
    DB_HOST = os.getenv("DATABASE_TEST_HOST", "")
    DB_PORT = os.getenv("DATABASE_TEST_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"

    # JWT OIDC settings
    # JWT_OIDC_TEST_MODE will set jwt_manager to use
    JWT_OIDC_TEST_MODE = True
    JWT_OIDC_TEST_AUDIENCE = "example"
    JWT_OIDC_TEST_ISSUER = "https://example.localdomain/auth/realms/example"
    JWT_OIDC_TEST_KEYS = {  # noqa: RUF012
        "keys": [
            {
                "kid": "flask-jwt-oidc-test-client",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR",
                "e": "AQAB"
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {  # noqa: RUF012
        "keys": [
            {
                "kid": "flask-jwt-oidc-test-client",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR",
                "e": "AQAB",
                "d": "C0G3QGI6OQ6tvbCNYGCqq043YI_8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhskURaDwk4-8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh_xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0",
                "p": "APXcusFMQNHjh6KVD_hOUIw87lvK13WkDEeeuqAydai9Ig9JKEAAfV94W6Aftka7tGgE7ulg1vo3eJoLWJ1zvKM",
                "q": "AOjX3OnPJnk0ZFUQBwhduCweRi37I6DAdLTnhDvcPTrrNWuKPg9uGwHjzFCJgKd8KBaDQ0X1rZTZLTqi3peT43s",
                "dp": "AN9kBoA5o6_Rl9zeqdsIdWFmv4DB5lEqlEnC7HlAP-3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhc",
                "dq": "ANtbSY6njfpPploQsF9sU26U0s7MsuLljM1E8uml8bVJE1mNsiu9MgpUvg39jEu9BtM2tDD7Y51AAIEmIQex1nM",
                "qi": "XLE5O360x-MhsdFXx8Vwz4304-MJg-oGSJXCK_ZWYOB_FGXFRTfebxCsSYi0YwJo-oNu96bvZCuMplzRI1liZw"
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_PEM = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDfn1nKQshOSj8xw44oC2klFWSNLmK3BnHONCJ1bZfq0EQ5gIfg
tlvB+Px8Ya+VS3OnK7Cdi4iU1fxO9ktN6c6TjmmmFevk8wIwqLthmCSF3r+3+h4e
ddj7hucMsXWv05QUrCPoL6YUUz7Cgpz7ra24rpAmK5z7lsV+f3BEvXkrUQIDAQAB
AoGAC0G3QGI6OQ6tvbCNYGCqq043YI/8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhs
kURaDwk4+8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh/
xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0CQQD13LrBTEDR44ei
lQ/4TlCMPO5bytd1pAxHnrqgMnWovSIPSShAAH1feFugH7ZGu7RoBO7pYNb6N3ia
C1idc7yjAkEA6Nfc6c8meTRkVRAHCF24LB5GLfsjoMB0tOeEO9w9Ous1a4o+D24b
AePMUImAp3woFoNDRfWtlNktOqLel5PjewJBAN9kBoA5o6/Rl9zeqdsIdWFmv4DB
5lEqlEnC7HlAP+3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhcCQQDb
W0mOp436T6ZaELBfbFNulNLOzLLi5YzNRPLppfG1SRNZjbIrvTIKVL4N/YxLvQbT
NrQw+2OdQACBJiEHsdZzAkBcsTk7frTH4yGx0VfHxXDPjfTj4wmD6gZIlcIr9lZg
4H8UZcVFN95vEKxJiLRjAmj6g273pu9kK4ymXNEjWWJn
-----END RSA PRIVATE KEY-----"""

    # cc gcloud listener payments vars
    PAY_AUDIENCE_SUB = "/api/v2/payments"
    VERIFY_PUBSUB_EMAILS = ["test@goole.email.com"]  # noqa: RUF012


class ProductionConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for production environment."""

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False


class MigrationConfig:  # pylint: disable=too-few-public-methods
    """Config object for migration environment."""

    ALEMBIC_INI = "migrations/alembic.ini"

    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_HOST = os.getenv("DATABASE_HOST", "")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")

    if DB_UNIX_SOCKET := os.getenv("DATABASE_UNIX_SOCKET", None):
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
