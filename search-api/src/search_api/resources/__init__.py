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
"""Exposes the versioned endpoints."""
from .constants import EndpointVersionPath
from .internal import bp as internal_bp
from .meta import bp as meta_bp
from .ops import bp as ops_bp
from .v1 import bus_bp as v1_bus_bp
from .v1 import purchases_bp as v1_purchases_bp
from .v2 import businesses_bp, payments_bp, purchases_bp, search_bp
from .version_endpoint import VersionEndpoint

v1_endpoint = VersionEndpoint(
    name="API_V1",
    path=EndpointVersionPath.API_V1,
    bps=[v1_bus_bp, v1_purchases_bp])

v2_endpoint = VersionEndpoint(
    name="API_V2",
    path=EndpointVersionPath.API_V2,
    bps=[search_bp, payments_bp, businesses_bp, purchases_bp])
