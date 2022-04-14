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
"""API endpoints for Registry Search."""
from http import HTTPStatus

from flask import g, jsonify, request, current_app
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from search_api.exceptions import BusinessException, DatabaseException
from search_api.resources import utils as resource_utils
from search_api.services.authz import authorized
from search_api.utils.auth import jwt
from search_api.utils.util import cors_preflight


API = Namespace('registry-search', description='Endpoints for searching across all BC businesses.')
