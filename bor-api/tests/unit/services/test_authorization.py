# Copyright © 2023 Province of British Columbia
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

"""Tests to verify the auth-api integration.

Test-Suite to ensure that the client for the auth-api service is working as expected.
"""
import pytest
from flask import current_app

from bor_api.services import authz
from tests.unit.test_utils import helper_create_jwt


MOCK_URL_NO_KEY = "https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/"
MOCK_URL = "https://bcregistry-bcregistry-mock.apigee.net/auth/api/v1/"

# testdata pattern is ({description}, {account id}, {valid})
TEST_SBC_DATA = [
    ("Valid account id", authz.GOV_ACCOUNT_ROLE, "Service BC", True),
    ("No account id", None, "", False),
    ("Invalid account id", authz.STAFF_ROLE, "BC Registries", False),
    ("Invalid account id", "2518", "Something", False),
]
TEST_REG_STAFF_DATA = [
    ("Valid account id", authz.STAFF_ROLE, True),
    ("No account id", None, False),
    ("Invalid account id", authz.GOV_ACCOUNT_ROLE, False),
    ("Invalid account id", "2518", False),
]
TEST_STAFF_DATA = [
    ("Valid account id", authz.STAFF_ROLE, True),
    ("No account id", None, False),
    ("Invalid account id", authz.BCOL_HELP, False),
    ("Invalid account id", "2518", False),
]


def test_user_orgs_mock(client, session, jwt):
    """Assert that a auth-api user orgs request works as expected with the mock service endpoint."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    # print('env auth-api url=' + current_app.config.get('AUTH_SVC_URL'))
    token = helper_create_jwt(jwt, [authz.PPR_ROLE])

    # test
    org_data = authz.user_orgs(token)

    # check
    assert org_data
    assert "orgs" in org_data
    assert len(org_data["orgs"]) == 1
    org = org_data["orgs"][0]
    assert org["orgStatus"] == "ACTIVE"
    assert org["statusCode"] == "ACTIVE"
    assert org["orgType"] == "PREMIUM"
    assert org["id"]
    assert org["name"]
