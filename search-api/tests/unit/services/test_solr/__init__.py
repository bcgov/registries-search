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
"""Tests to assure the Solr Services."""
from search_api.services.solr import SolrDoc

SOLR_TEST_DOCS = [
    SolrDoc('CP1234567', 'test 1234', 'ACTIVE', 'CP', 'BN00012334').json(),
    SolrDoc('CP0234567', 'tester 1111', 'HISTORICAL', 'CP', '09876K').json(),
    SolrDoc('CP0034567', 'tests 2222', 'ACTIVE', 'CP').json(),
    SolrDoc('BC0004567', 'test 3333', 'ACTIVE', 'BEN', '00987766800988').json(),
    SolrDoc('BC0000567', '4444 test', 'HISTORICAL', 'BC', 'BN9000776557').json(),
    SolrDoc('BC0000067', 'single', 'ACTIVE', 'BEN', '242217').json(),
    SolrDoc('BC0000007', 'lots of words in here', 'ACTIVE', 'BEN', '124221').json(),
    SolrDoc('BC0020047', 'NOt Case SENSitive', 'ACTIVE', 'BEN', '1255323221').json()
]