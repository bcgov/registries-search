# Copyright © 2024 Province of British Columbia
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
"""Exposes all of the internal solr endpoints in Flask-Blueprint style."""
from flask import Blueprint

from .command import bp as command_bp
from .imports import bp as import_bp
from .update import bp as update_bp

bp = Blueprint("SOLR", __name__, url_prefix="/solr")
bp.register_blueprint(command_bp)
bp.register_blueprint(import_bp)
bp.register_blueprint(update_bp)
