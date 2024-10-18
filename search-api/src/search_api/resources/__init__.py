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
from .v1 import bus_bp, internal_bp, meta_bp, ops_bp, purchases_bp
from .v2 import payments_bp, search_bp
from .version_endpoint import VersionEndpoint


v1_endpoint = VersionEndpoint(  # pylint: disable=invalid-name
    name='API_V1',
    path=EndpointVersionPath.API_V1,
    bps=[bus_bp, meta_bp, ops_bp, purchases_bp, internal_bp])

v2_endpoint = VersionEndpoint(  # pylint: disable=invalid-name
    name='API_V2',
    path=EndpointVersionPath.API_V2,
    bps=[search_bp, payments_bp])
