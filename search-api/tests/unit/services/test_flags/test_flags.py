# Copyright © 2022 Daxiom™ Systems Inc.
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
import pytest

from search_api.utils.logging import logging, get_logging_flag_name
from tests import not_github_ci

@not_github_ci
@pytest.mark.skip(reason="skip in the ci")
def test_change_log_level_using_LD_flag():
    from search_api import create_app
    from ldclient.integrations.test_data import TestData

    # with app.app_context():
    ld = TestData.data_source()
    app = create_app('testing', **{'ld_test_data': ld})
    with app.test_client() as client:
        # setup
        TEST_FLAG_NAME = get_logging_flag_name()

        route_name = '/test_change_log_level_using_LD_flag'

        logging.getLogger().setLevel(logging.INFO)

        @app.route(route_name)
        def get():
            return "<p>Hello, World!</p>"
        
        # set environment variable for OPS_LOGGER_LEVEL
        app.config['OPS_LOGGER_LEVEL'] = TEST_FLAG_NAME
        assert TEST_FLAG_NAME == app.config.get('OPS_LOGGER_LEVEL')

        # set the test data for the flag
        ld.update(ld.flag(TEST_FLAG_NAME)
                    .variations('CRITICAL','DEBUG','ERROR','INFO','WARNING')
                    .variation_for_user(TEST_FLAG_NAME, 1)
                    .fallthrough_variation(0))

        # Before test assert the logging level is INFO
        assert logging.getLogger().level == logging.INFO

        # Execute test
        
        response = client.get(route_name)

        # Validate expected outcomes
        assert b"Hello, World" in response.data
        assert logging.getLogger().level == logging.DEBUG
