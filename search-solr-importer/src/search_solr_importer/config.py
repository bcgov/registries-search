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


class Config():  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SOLR_SVC_LEADER_CORE = os.getenv('SOLR_SVC_LEADER_CORE', 'business')
    SOLR_SVC_FOLLOWER_CORE = os.getenv('SOLR_SVC_FOLLOWER_CORE', 'business_follower')
    SOLR_SVC_LEADER_URL = os.getenv('SOLR_SVC_LEADER_URL', 'http://localhost:8873/solr')
    SOLR_SVC_FOLLOWER_URL = os.getenv('SOLR_SVC_FOLLOWER_URL', 'http://localhost:8874/solr')
    HAS_FOLLOWER = SOLR_SVC_FOLLOWER_URL != SOLR_SVC_LEADER_URL

    SEARCH_API_URL = os.getenv('REGISTRIES_SEARCH_API_INTERNAL_URL', 'http://')
    SEARCH_API_V1 = os.getenv('REGISTRIES_SEARCH_API_VERSION', '')

    POD_NAMESPACE = os.getenv('POD_NAMESPACE', 'unknown')

    LD_SDK_KEY = os.getenv('LD_SDK_KEY', None)
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)
    SENTRY_TSR = os.getenv('SENTRY_TSR', '1.0')

    BATCH_SIZE = int(os.getenv('SOLR_BATCH_UPDATE_SIZE', '1000'))
    REINDEX_CORE = os.getenv('REINDEX_CORE', 'False') == 'True'
    PRELOADER_JOB = os.getenv('PRELOADER_JOB', 'False') == 'True'

    MODERNIZED_LEGAL_TYPES = os.getenv('MODERNIZED_LEGAL_TYPES', 'BEN,CBEN,CP,GP,SP').upper().split(',')

    BATCH_SIZE_SOLR = int(os.getenv('SOLR_BATCH_UPDATE_SIZE', '1000'))
    BATCH_SIZE_SOLR_SI = int(os.getenv('SOLR_BATCH_UPDATE_SIZE_SI', '1000'))
    REINDEX_CORE = os.getenv('REINDEX_CORE', 'False') == 'True'
    PRELOADER_JOB = os.getenv('PRELOADER_JOB', 'False') == 'True'
    INCLUDE_BTR_LOAD = os.getenv('INCLUDE_BTR_LOAD', 'False') == 'True'
    INCLUDE_COLIN_LOAD = os.getenv('INCLUDE_COLIN_LOAD', 'True') == 'True'
    INCLUDE_LEAR_LOAD = os.getenv('INCLUDE_LEAR_LOAD', 'True') == 'True'
    RESYNC_OFFSET = os.getenv('RESYNC_OFFSET', '130')

    BTR_BATCH_LIMIT = int(os.getenv('BTR_BATCH_LIMIT', '100000'))

    MODERNIZED_LEGAL_TYPES = os.getenv('MODERNIZED_LEGAL_TYPES', 'BEN,CBEN,CP,GP,SP').upper().split(',')

    # TODO: or not include btr
    IS_PARTIAL_IMPORT = not INCLUDE_COLIN_LOAD or not INCLUDE_LEAR_LOAD

    # Service account details
    ACCOUNT_SVC_AUTH_URL = os.getenv('KEYCLOAK_AUTH_TOKEN_URL')
    ACCOUNT_SVC_CLIENT_ID = os.getenv('BUSINESS_SEARCH_SERVICE_ACCOUNT_CLIENT_ID')
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv('BUSINESS_SEARCH_SERVICE_ACCOUNT_SECRET')
    try:
        ACCOUNT_SVC_TIMEOUT = int(os.getenv('AUTH_API_TIMEOUT', '20'))
    except:  # pylint: disable=bare-except; # noqa: B901, E722
        ACCOUNT_SVC_TIMEOUT = 20

    # ORACLE - CDEV/CTST/CPRD
    ORACLE_USER = os.getenv('ORACLE_USER', '')
    ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD', '')
    ORACLE_DB_NAME = os.getenv('ORACLE_DB_NAME', '')
    ORACLE_HOST = os.getenv('ORACLE_HOST', '')
    ORACLE_PORT = int(os.getenv('ORACLE_PORT', '1521'))

    # POSTGRESQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_LOCATION = os.getenv('DATABASE_LOCATION', 'OCP')

    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST_LEAR', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')

    if DB_LOCATION == 'GCP':
        DB_USER = os.getenv('DATABASE_USERNAME_GCP', '')
        DB_PASSWORD = os.getenv('DATABASE_PASSWORD_GCP', '')
        DB_NAME = os.getenv('DATABASE_NAME_GCP', '')
        DB_HOST = os.getenv('DATABASE_HOST_GCP', '')
        DB_PORT = os.getenv('DATABASE_PORT_GCP', '5432')

    BTR_DB_USER = os.getenv('DATABASE_USERNAME_BTR', '')
    BTR_DB_PASSWORD = os.getenv('DATABASE_PASSWORD_BTR', '')
    BTR_DB_NAME = os.getenv('DATABASE_NAME_BTR', '')
    BTR_DB_HOST = os.getenv('DATABASE_HOST_BTR', '')
    BTR_DB_PORT = os.getenv('DATABASE_PORT_BTR', '5432')

    # Connection pool settings
    DB_MIN_POOL_SIZE = os.getenv('DATABASE_MIN_POOL_SIZE', '2')
    DB_MAX_POOL_SIZE = os.getenv('DATABASE_MAX_POOL_SIZE', '10')
    DB_CONN_WAIT_TIMEOUT = os.getenv('DATABASE_CONN_WAIT_TIMEOUT', '5')
    DB_CONN_TIMEOUT = os.getenv('DATABASE_CONN_TIMEOUT', '900')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        # 'echo_pool': 'debug',
        'pool_size': int(DB_MIN_POOL_SIZE),
        'max_overflow': (int(DB_MAX_POOL_SIZE) - int(DB_MIN_POOL_SIZE)),
        'pool_recycle': int(DB_CONN_TIMEOUT),
        'pool_timeout': int(DB_CONN_WAIT_TIMEOUT)
    }

    # Event tracking max retries before human intervention.
    EVENT_MAX_RETRIES: int = int(os.getenv('EVENT_MAX_RETRIES', '3'))


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
    SOLR_SVC_URL = os.getenv('SOLR_SVC_TEST_URL', 'http://')
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', '')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', '')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # JWT OIDC settings
    # JWT_OIDC_TEST_MODE will set jwt_manager to use
    JWT_OIDC_TEST_MODE = True
    JWT_OIDC_TEST_AUDIENCE = 'example'
    JWT_OIDC_TEST_ISSUER = 'https://example.localdomain/auth/realms/example'
    JWT_OIDC_TEST_KEYS = {
        'keys': [
            {
                'kid': 'flask-jwt-oidc-test-client',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',  # noqa: E501
                'e': 'AQAB'
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {
        'keys': [
            {
                'kid': 'flask-jwt-oidc-test-client',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',  # noqa: E501
                'e': 'AQAB',
                'd': 'C0G3QGI6OQ6tvbCNYGCqq043YI_8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhskURaDwk4-8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh_xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0',  # noqa: E501
                'p': 'APXcusFMQNHjh6KVD_hOUIw87lvK13WkDEeeuqAydai9Ig9JKEAAfV94W6Aftka7tGgE7ulg1vo3eJoLWJ1zvKM',
                'q': 'AOjX3OnPJnk0ZFUQBwhduCweRi37I6DAdLTnhDvcPTrrNWuKPg9uGwHjzFCJgKd8KBaDQ0X1rZTZLTqi3peT43s',
                'dp': 'AN9kBoA5o6_Rl9zeqdsIdWFmv4DB5lEqlEnC7HlAP-3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhc',
                'dq': 'ANtbSY6njfpPploQsF9sU26U0s7MsuLljM1E8uml8bVJE1mNsiu9MgpUvg39jEu9BtM2tDD7Y51AAIEmIQex1nM',
                'qi': 'XLE5O360x-MhsdFXx8Vwz4304-MJg-oGSJXCK_ZWYOB_FGXFRTfebxCsSYi0YwJo-oNu96bvZCuMplzRI1liZw'
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


class ProductionConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for production environment."""

    DEBUG = False
    DEVELOPMENT = False
    TESTING = False


config = {  # pylint: disable=invalid-name; Keeping name consistent with our other apps
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'unitTesting': UnitTestingConfig,
}
