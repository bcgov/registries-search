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
"""This module holds request non-schema data validation functions and helpers."""
from flask import current_app, request


def valid_charset(word: str) -> bool:
    """Verify word characters adhere to a supported set."""
    return word == word.encode('ascii', 'ignore').decode('utf-8')


def validate_search_request() -> tuple[dict, list[dict]]:
    """Validate the search request headers / payload."""
    errors = []
    request_json = request.get_json()
    query_json = request_json.get('query', None)
    if not isinstance(query_json, dict):
        errors.append({'Invalid payload': "Expected an object for 'query'."})
    else:
        value = query_json.get('value', None)
        if not value or not isinstance(value, str):
            errors.append({'Invalid payload': "Expected a string for 'query/value'."})

        if not isinstance(query_json.get('parties', {}), dict):
            errors.append({'Invalid payload': "Expected an object for 'query/parties'."})

    categories = request_json.get('categories', {})
    if not isinstance(categories, dict):
        errors.append({'Invalid payload': "Expected an object for 'categories'."})
    else:
        for key, value in categories.items():
            if not isinstance(value, list):
                errors.append({'Invalid payload': f"Expected a list for 'categories/{key}'."})
    try:
        start = int(request_json.get('start', 0))
        rows = int(request_json.get('rows', 0))
        if start < 0:
            errors.append({'Invalid payload': "Expected 'start' to be >= 0."})
        if rows > (max_rows := current_app.config['SOLR_SVC_BUS_MAX_ROWS']) or rows < 0:
            errors.append({'Invalid payload': f"Expected 'rows' to be between 0 and {max_rows}."})
    except ValueError:  # catch invalid start/row entry
        errors.append({'Invalid payload': "Expected integer for params: 'start', 'rows'"})

    return request_json, errors
