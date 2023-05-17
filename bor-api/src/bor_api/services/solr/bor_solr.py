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
"""Manages solr class for using search solr."""
from contextlib import suppress
from datetime import datetime, timedelta
from dataclasses import asdict
from http import HTTPStatus

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry
from flask import current_app

from bor_api.exceptions import SolrException

from .bor_solr_fields import SolrField as Field
from .solr_docs import Entity


class Solr:
    """Wrapper around the solr instance."""

    def __init__(self, app=None):
        """Initialize this object."""
        self.app = None

        self.solr_url = None
        self.core = 'bor'
        self.default_start = 0
        self.default_rows = 10
        # field selections
        self.entity_fields = [
            Field.BN.value, Field.BN_SP.value, Field.ENTITY_ADDRESSES.value,
            Field.ENTITY_TYPE.value, Field.IDENTIFIER_Q.value, Field.LEGAL_NAME.value,
            Field.LEGAL_TYPE.value, Field.OPERATING_NAME.value, Field.ROLES.value,
            Field.STATE.value, Field.SCORE.value, '[child]'
        ]
        self.address_fields = [
            Field.ADDRESS_CITY.value, Field.ADDRESS_COUNTRY.value,
            Field.ADDRESS_REGION.value, Field.ADDRESS_TYPE.value,
            Field.POSTAL_CODE.value, Field.STREET_ADDRESS.value
        ]
        self.entity_role_fields = [
            Field.ACTIVE.value, Field.RELATED_BN.value, Field.RELATED_ENTITY_TYPE.value,
            Field.RELATED_IDENTIFIER.value, Field.RELATED_NAME.value,
            Field.RELATED_STATE.value, Field.ROLE_DATES.value, Field.ROLE_TYPE.value
        ]
        self.date_fields = [Field.START.value, Field.END.value]
        # base urls
        self.search_url = '{url}/{core}/query'
        self.update_url = '{url}/{core}/update?commitWithin=1000&overwrite=true&wt=json'

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Solr environment."""
        self.app = app
        self.solr_url = app.config.get('SOLR_SVC_URL')

    # pylint: disable=too-many-arguments
    def call_solr(self,
                  method: str,
                  query: str,
                  params: dict = None,
                  json_data: dict = None,
                  xml_data: str = None,
                  force=False) -> Response:
        """Call solr instance with given params."""
        try:
            if self.is_reindexing() and not force:
                err_msg = 'This resource is undergoing scheduled maintenance and will be ' \
                    f'unavailable for up to {self.app.config.get("SOLR_REINDEX_LENGTH")} minutes.'
                raise SolrException(err_msg, HTTPStatus.SERVICE_UNAVAILABLE)
            response = None
            url = query.format(url=self.solr_url, core=self.core)
            retry_times = 3 if method == 'GET' else 5
            backoff_factor = 1 if method == 'GET' else 2
            retries = Retry(total=retry_times,
                            backoff_factor=backoff_factor,
                            status_forcelist=[500, 502, 503, 504],
                            allowed_methods=['GET', 'POST'])
            session = Session()
            session.mount(url, HTTPAdapter(max_retries=retries))
            if method == 'GET':
                response = session.get(url, params=params, timeout=30)
            elif method == 'POST' and json_data:
                response = session.post(url=url, json=json_data, timeout=60)
            elif method == 'POST' and xml_data:
                headers = {'Content-Type': 'application/xml'}
                response = session.post(url=url, data=xml_data, headers=headers, timeout=60)
            else:
                raise Exception('Invalid params given.')  # pylint: disable=broad-exception-raised
            # check for error
            if response.status_code != HTTPStatus.OK:
                error = response.json().get('error', {}).get('msg', 'Error handling Solr request.')
                raise Exception(error)  # pylint: disable=broad-exception-raised;
            return response
        except Exception as err:  # noqa B902
            msg = 'Error handling Solr request.'
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            with suppress(Exception):
                status_code = response.status_code
                msg = response.json().get('error', {}).get('msg', msg)
            current_app.logger.debug(msg)
            raise SolrException(error=msg, status_code=status_code) from err

    def create_or_replace_docs(self, docs: list[Entity], force=False):
        """Create or replace solr docs in the core."""
        update_json = [asdict(doc) for doc in docs]
        response = self.call_solr('POST', self.update_url, json_data=update_json, force=force)
        return response

    def delete_all_docs(self):
        """Delete all solr docs from the core."""
        payload = '<delete><query>*:*</query></delete>'
        response = self.call_solr('POST', self.update_url, xml_data=payload)
        return response

    def delete_docs(self, identifiers: list[str]):
        """Delete solr docs from the core."""
        payload = '<delete><query>'
        if identifiers:
            payload += f'{Field.IDENTIFIER.value}:{identifiers[0].upper()}'
        for identifier in identifiers[1:]:
            payload += f' OR {Field.IDENTIFIER.value}:{identifier.upper()}'
        payload += '</query></delete>'

        response = self.call_solr('POST', self.update_url, xml_data=payload)
        return response

    def is_reindexing(self) -> bool:
        """Return True if this instance of solr is in the process of reindexing."""
        current_weekday = datetime.utcnow().weekday()
        timeout_start_weekday = self.app.config.get('SOLR_REINDEX_WEEKDAY')
        current_day = datetime.utcnow().strftime('%d')
        timeout_start_day = self.app.config.get('SOLR_REINDEX_DAY')
        if current_weekday == timeout_start_weekday or current_day == timeout_start_day:
            current_time = datetime.time(datetime.utcnow())
            timeout_start_time = datetime.strptime(self.app.config.get('SOLR_REINDEX_START_TIME'), '%H:%M:%S%z')
            timeout_length = self.app.config.get('SOLR_REINDEX_LENGTH')  # in minutes
            timeout_end_time = timeout_start_time + timedelta(minutes=timeout_length)
            if timeout_start_time.time() < current_time < timeout_end_time.time():
                return True
        return False

    def query(self, payload: dict[str, str], start: int = None, rows: int = None) -> dict:
        """Return a list of solr docs from the solr query handler for the given params."""
        payload['offset'] = start if start else self.default_start
        payload['limit'] = rows if rows else self.default_rows

        response = self.call_solr('POST', self.search_url, json_data=payload)
        return response.json()
