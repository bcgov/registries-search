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
"""Utils for the api search endpoint tests."""


def format_param(param_dict: dict) -> str:
    """Return the formatted param."""
    param = ''
    for key, value in param_dict.items():
        if param:
            param += '::'
        if isinstance(value, list):
            value = ','.join(value)
        param += f'{key}:{value}'
    return param
