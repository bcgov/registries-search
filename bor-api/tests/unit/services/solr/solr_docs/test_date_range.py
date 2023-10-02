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
"""Tests to ensure that the Date Range Solr Doc works as expected."""
from dataclasses import asdict

import pytest

from bor_api.services.solr.bor_solr_fields import SolrField as Field
from bor_api.services.solr.solr_docs import DateRange


@pytest.mark.parametrize('test_name,start,end', [
    ('test_1', '2022-03-21T14:24:02Z', '2023-04-11T06:44:52Z'),
    ('test_2', '2019-12-01T02:44:56Z', None),
    ('test_3', None, '2023-04-11T06:44:52Z'),
    ('test_4', None, None),
])
def test_date_range_doc(test_name, start, end):
    """Assert the Date Range solr doc class works as expected."""
    date_range = DateRange(start=start, end=end)

    assert date_range

    json = asdict(date_range)
    assert json
    assert json.get(Field.START.value) == start
    assert json.get(Field.END.value) == end
