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
"""Exposes all of the businesses endpoints in Flask-Blueprint style."""
from flask import Blueprint

from .documents import bp as documents_bp
from .search import bp as search_bp


bp = Blueprint('BUSINESSES', __name__, url_prefix='/businesses')  # pylint: disable=invalid-name
bp.register_blueprint(search_bp)
bp.register_blueprint(documents_bp)
