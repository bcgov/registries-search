# Copyright © 2019 Province of British Columbia
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

from search_api import auth_cache
from search_api.services import authz
from tests.unit.services.utils import helper_create_jwt

MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_URL = 'https://bcregistry-bcregistry-mock.apigee.net/auth/api/v1/'

# testdata pattern is ({description}, {account id}, {valid})
TEST_SBC_DATA = [
    ('Valid account id', authz.GOV_ACCOUNT_ROLE, 'Service BC', True),
    ('No account id', None, '', False),
    ('Invalid account id', authz.STAFF_ROLE, 'BC Registries', False),
    ('Invalid account id', '2518', 'Something', False)
]
TEST_REG_STAFF_DATA = [
    ('Valid account id', authz.STAFF_ROLE, True),
    ('No account id', None, False),
    ('Invalid account id', authz.GOV_ACCOUNT_ROLE, False),
    ('Invalid account id', '2518', False)
]
TEST_STAFF_DATA = [
    ('Valid account id', authz.STAFF_ROLE, True),
    ('No account id', None, False),
    ('Invalid account id', authz.BCOL_HELP, False),
    ('Invalid account id', '2518', False)
]


def test_user_orgs_mock(client, session, jwt):
    """Assert that a auth-api user orgs request works as expected with the mock service endpoint."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    token = helper_create_jwt(jwt, [authz.PPR_ROLE])

    # test
    org_data = authz.user_orgs(token)

    # check
    assert org_data
    assert 'orgs' in org_data
    assert len(org_data['orgs']) == 1
    org = org_data['orgs'][0]
    assert org['orgStatus'] == 'ACTIVE'
    assert org['statusCode'] == 'ACTIVE'
    assert org['orgType'] == 'PREMIUM'
    assert org['id']
    assert org['name']


@pytest.mark.parametrize('desc,account_id,branch_name,valid', TEST_SBC_DATA)
def test_sbc_office_account(session, jwt, requests_mock, desc, account_id, branch_name, valid):
    """Assert that sbc office account check returns the expected result."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_URL)
    requests_mock.get(f'{MOCK_URL}orgs/{account_id}', json={'branchName': branch_name})
    token = helper_create_jwt(jwt, [authz.GOV_ACCOUNT_ROLE])
    result = authz.is_sbc_office_account(token, account_id) or False
    # check
    assert result == valid


@pytest.mark.parametrize('desc,account_id,valid', TEST_REG_STAFF_DATA)
def test_reg_staff_account(session, desc, account_id, valid):
    """Assert that registries staff account check returns the expected result."""
    # test
    result = authz.is_reg_staff_account(account_id)
    # check
    assert result == valid


@pytest.mark.parametrize('desc,account_id,valid', TEST_STAFF_DATA)
def test_staff_account(session, desc, account_id, valid):
    """Assert that staff account check returns the expected result."""
    # test
    result = authz.is_staff_account(account_id)
    # check
    assert result == valid


USERS_ORG_123 = {
    "orgs": [
        {"id": 123, }
    ]
}

USERS_ORG_1234 = {
    "orgs": [
        {"id": 1234, }
    ]
}


@pytest.mark.parametrize('_test_name, claims, account_id, user_orgs, expect_auth_call, expected',[
    ('regular_user_valid', {'loginSource': 'Not API'}, '123', USERS_ORG_123, True, True),
    ('regular_user_invalid', {'loginSource': 'Not API'}, '124', USERS_ORG_123, True, False),
    ('api_user_valid', {'loginSource': 'API_GW', 'Account-Id': '58'}, '58', None, False, True),
    ('api_user_invalid', {'loginSource': 'API_GW', 'Account-Id': '1'}, '58', None, False, False),
])
def test_does_user_have_account(app, requests_mock, jwt, _test_name, claims, account_id, user_orgs, expect_auth_call, expected):
    """Assert that the account access check works correctly."""
    auth_cache.clear()
    app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    auth_mock = requests_mock.get(f"{app.config.get('AUTH_SVC_URL')}users/orgs", json=user_orgs)
    with app.test_request_context("test", headers={'Account-Id': account_id}) as r:
        # Set request_ctx is set by flask_jwt_oidc during the request, need to set it manually here
        r.current_user = claims
        header = {
            "alg": "RS256",
            "typ": "JWT",
            "kid": "flask-jwt-oidc-test-client"
        }
        jwt_token = jwt.create_jwt(claims, header)

        result = authz.does_user_have_account(jwt_token, account_id)
        
        assert auth_mock.called == expect_auth_call
        assert result == expected


def test_does_user_have_account_caching(app, requests_mock):
    """Assert that the user has account caching works correctly."""
    auth_cache.clear()
    app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)

    requests_mock.get(f"{app.config.get('AUTH_SVC_URL')}users/orgs", json=USERS_ORG_123)
    with app.test_request_context("test") as r:
        r.current_user = {}
        result = authz.does_user_have_account(jwt_token='jwt_token_123', account_id='123')
        assert result == True

        requests_mock.get(f"{app.config.get('AUTH_SVC_URL')}users/orgs", json=USERS_ORG_1234)

        result = authz.does_user_have_account(jwt_token='jwt_token_123', account_id='123')
        assert result == True

        auth_cache.clear()
        result = authz.does_user_have_account(jwt_token='jwt_token_123', account_id='123')
        assert result == False
