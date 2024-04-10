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
"""Tests to ensure that the Interest Solr Doc works as expected."""
from dataclasses import asdict

import pytest

from bor_api.enums import InterestDetails
from bor_api.services.bor_solr.fields import InterestField
from bor_api.services.bor_solr.doc_models import Interest


@pytest.mark.parametrize('test_name,interest_info', [
    ('test_1', {'details': 'bla'}),
    ('test_2', {'details': InterestDetails.DIR_DIRECT.value, 'directOrIndirect': 'direct'}),
    ('test_3', {'details': InterestDetails.SV_BEN_OWNER.value, 'directOrIndirect': 'direct', 'interestType': 'shareholding'}),
    ('test_4', {'details': InterestDetails.SV_REG_OWNER.value, 'directOrIndirect': 'direct', 'interestType': 'shareholding', 'sharesMax': 23.4}),
])
def test_interest_doc(test_name, interest_info):
    """Assert the Interest solr doc class works as expected."""
    interest = Interest(details=interest_info.get('details'),
                        directOrIndirect=interest_info.get('directOrIndirect'),
                        interestType=interest_info.get('interestType'),
                        sharesExact=interest_info.get('sharesExact'),
                        sharesMax=interest_info.get('sharesMax'),
                        sharesMin=interest_info.get('sharesMin'))

    assert interest

    json = asdict(interest)
    assert json
    if interest_info.get('details') == 'bla':
        assert json.get(InterestField.DETAILS.value) == 'other'
        assert json.get(InterestField.OTHER_REASON.value) == 'bla'
    else:
        assert json.get(InterestField.DETAILS.value) == interest_info.get('details')
        assert json.get(InterestField.OTHER_REASON.value) == None
    assert json.get(InterestField.DIRECT_INDIRECT.value) == interest_info.get('directOrIndirect')
    assert json.get(InterestField.TYPE.value) == interest_info.get('interestType')
    assert json.get(InterestField.SHARE_EXACT.value) == interest_info.get('sharesExact')
    assert json.get(InterestField.SHARE_MAX.value) == interest_info.get('sharesMax')
    assert json.get(InterestField.SHARE_MIN.value) == interest_info.get('sharesMin')
