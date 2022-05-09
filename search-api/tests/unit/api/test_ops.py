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

"""Tests to verify the ops ready/health check endpoints.

Test-Suite to ensure that the /ops endpoint is working as expected.
"""
from http import HTTPStatus

def test_ready_check(session, client, jwt):
    """Assert that ops ready check endpoint works."""
    # no setup

    # test
    rv = client.get('/api/v1/ops/readyz')
    # check
    assert rv.status_code == HTTPStatus.OK
    assert rv.json['message'] == 'api is ready'

def test_health_check(session, client, jwt):
    """Assert that ops health check endpoint works."""
    # no setup

    # test
    rv = client.get('/api/v1/ops/healthz')
    # check
    assert rv.status_code == HTTPStatus.OK
    assert rv.json['message'] == 'api is healthy'
