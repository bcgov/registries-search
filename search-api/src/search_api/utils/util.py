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

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""
from datetime import UTC, datetime

import dpath.util


def get_str(filing: dict, path: str) -> str:
    """Extract a str from the JSON filing, at the provided path.

    Args:
        filing (Dict): A valid registry_schema filing.
        path (str): The path to the date, which is in ISO Format.

    Examples:
        >>>get_str(
            filing={'filing':{'header':{'name': 'annualReport'}}},
            path='filing/header/name')
        'annualReport'

    """
    try:
        raw = dpath.util.get(filing, path)
        return str(raw)
    except (IndexError, KeyError, TypeError, ValueError):
        return None


def utcnow():
    """Get the current datetime in utc.
    
    Helpful for model datetime defaults."""
    return datetime.now(UTC)
