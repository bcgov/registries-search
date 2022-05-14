# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This creates the pymarks for the integrations used by the SEARCH API.

The database used by the SEARCH API is not considered an integration, as it is fully
owned and managed by the API.

The other integrations only run if their environment variables are set,
in others words they fail open and will not run.
"""
import os

import pytest
from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

def get_skip_value(env_skip_val):
    return (os.getenv(env_skip_val, 'false') == 'false') or (os.getenv(env_skip_val, 'False') == 'False')

integration_authorization = pytest.mark.skipif(
    get_skip_value('RUN_AUTHORIZATION_TESTS'),
    reason='Test requiring authorization service are skipped when RUN_AUTHORIZATION_TESTS is False.')

integration_nats = pytest.mark.skipif(get_skip_value('RUN_NATS_TESTS'),
                                      reason='NATS tests are skipped when RUN_NATS_TESTS is False.')

integration_payment = pytest.mark.skipif(get_skip_value('RUN_PAYMENT_TESTS'),
                                         reason='Test requiring payment service are skipped when RUN_PAYMENT_TESTS is False.')

integration_ldarkly = pytest.mark.skipif(get_skip_value('RUN_LD_TESTS'),
                                        reason='Launch Darkly integration tests are skipped when RUN_LD_TESTS is False.')

integration_solr = pytest.mark.skipif(get_skip_value('RUN_SOLR_TESTS'),
                                        reason='SOLR integration tests are skipped when RUN_SOLR_TESTS is False.')

not_github_ci = pytest.mark.skipif(get_skip_value('NOT_GITHUB_CI'),
                                   reason='Does not pass on github ci.')
