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

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""
# from functools import wraps
from typing import Dict

import dpath.util


def cors_preflight(methods: str = 'GET'):
    """Render an option method on the class."""
    def wrapper(f):  # pylint: disable=invalid-name
        def options(self, *args, **kwargs):  # pylint: disable=unused-argument
            return {'Allow': 'GET'}, 200, \
                   {'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': methods,
                    'Access-Control-Allow-Headers': 'Authorization, Content-Type'}

        setattr(f, 'options', options)
        return f
    return wrapper


def get_str(payload: Dict, path: str) -> str:
    """Extract a str from the JSON filing, at the provided path.

    Args:
        d (Dict): any dictionary.
        path (str): The path to the nested value.

    Examples:
        >>>get_str(
            d={'filing':{'header':{'name': 'annualReport'}}},
            path='filing/header/name')
        'annualReport'

    """
    try:
        raw = dpath.util.get(payload, path)
        return str(raw)
    except (IndexError, KeyError, TypeError, ValueError):
        return None
