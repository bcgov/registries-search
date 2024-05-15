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
"""Tests to assure the SearchHistory Class.

Test-Suite to ensure that the SearchHistory Class is working as expected.
"""
import pytest

from bor_api.enums import SearchAccessLevel
from bor_api.models import User, SearchHistory


@pytest.mark.parametrize('test_name, username, account_id, access_level', [
    ('test_all', 'blippity', '456', SearchAccessLevel.PUBLIC),
    ('test_no_user', None, '234', SearchAccessLevel.LIMITED),
    ('test_no_account', 'bop', None, SearchAccessLevel.EXTENDED),
    ('test_no_values', None, None, None),
])
def test_search_history(session, test_name, username, account_id, access_level):
    """Assert that a SearchHistory can be stored in the service."""
    user = None
    if username:
        user = User(username=username, firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
        session.add(user)
        session.commit()
    # insert SearchHistory for user
    search = SearchHistory(params={'query': {'value': 'test'}},
                           results=[{'entityType': 'PERSON','legalName': 'tester','roles': [],'addresses': []}],
                           submitter_id=user.id if user else None,
                           submitter_account_id=account_id,
                           access_level=access_level)
    search.save()
    assert search.id is not None
