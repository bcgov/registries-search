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
"""The application common configuration."""
import os

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


class BaseConfig:
    """Base configuration."""


class Config(BaseConfig):
    """Production configuration."""

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

    # OIDC and Authorization Config
    OIDC_TOKEN_URL = os.getenv('OIDC_TOKEN_URL')
    OIDC_SA_CLIENT_ID = os.getenv('OIDC_SA_CLIENT_ID')
    OIDC_SA_CLIENT_SECRET = os.getenv('OIDC_SA_CLIENT_SECRET')

    # BCRegistry API Config
    LEGAL_API_URL = os.getenv('LEGAL_API_URL', '') + os.getenv('LEGAL_API_VERSION_2', '')

    # Google SA account
    # create key base64.b64encode(json.dumps(auth_json).encode('utf-8'))
    GOOGLE_STORAGE_SERVICE_ACCOUNT = os.getenv('GOOGLE_STORAGE_SERVICE_ACCOUNT')
    if GOOGLE_STORAGE_SERVICE_ACCOUNT and isinstance(GOOGLE_STORAGE_SERVICE_ACCOUNT, str):
        GOOGLE_STORAGE_SERVICE_ACCOUNT = bytes(GOOGLE_STORAGE_SERVICE_ACCOUNT, 'utf-8')
    STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
    STORAGE_FILEPATH = os.getenv('STORAGE_FILEPATH')

    # Search Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')  # POSTGRESQL
    # POSTGRESQL
    if DB_UNIX_SOCKET := os.getenv('DATABASE_UNIX_SOCKET', None):
        SQLALCHEMY_DATABASE_URI = \
            f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}'
    else:
        SQLALCHEMY_DATABASE_URI = \
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

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
