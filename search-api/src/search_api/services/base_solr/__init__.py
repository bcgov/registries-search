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
"""This module wraps the solr classes/fields for using registries search solr."""


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

from contextlib import suppress
from http import HTTPStatus

from flask import Flask, current_app
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import ConnectionError as SolrConnectionError

from search_api.exceptions import SolrException
from search_api.utils.base import BaseEnum


class Solr:
    """Wrapper class around the solr instance."""

    def __init__(self, config_prefix: str, app: Flask = None):
        """Initialize the solr class."""
        self.app = None
        self.config_prefix = config_prefix

        # solr cores
        self.follower_core = None
        self.leader_core = None
        # solr urls
        self.follower_url = None
        self.leader_url = None

        self.default_start = 0
        self.default_rows = 10

        # base urls
        self.reload_url = '{url}/admin/cores?action=RELOAD&core={core}'
        self.replication_url = '{url}/{core}/replication'
        self.search_url = '{url}/{core}/query'
        self.suggest_url = '{url}/{core}/suggest'
        self.synonyms_url = '{url}/{core}/schema/analysis/synonyms'
        self.update_url = '{url}/{core}/update?commit=true&overwrite=true&wt=json'
        self.bulk_update_url = '{url}/{core}/update?overwrite=true&wt=json'

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize the Solr environment."""
        self.app = app

        # NOTE: for a single core implementation set leader/follower cores the same
        self.leader_core = app.config.get(f'{self.config_prefix}_LEADER_CORE')
        self.follower_core = app.config.get(f'{self.config_prefix}_FOLLOWER_CORE')
        # NOTE: for a single node implementation set the leader/follower urls the same
        self.leader_url = app.config.get(f'{self.config_prefix}_LEADER_URL')
        self.follower_url = app.config.get(f'{self.config_prefix}_FOLLOWER_URL')

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def call_solr(self,
                  method: str,
                  query: str,
                  params: dict = None,
                  json_data: dict = None,
                  xml_data: str = None,
                  leader=True,
                  timeout=25) -> Response:
        """Call solr instance with given params."""
        base_url = self.leader_url if leader else self.follower_url
        core = self.leader_core if leader else self.follower_core
        url = query.format(url=base_url, core=core)
        retries = Retry(total=1,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=['GET', 'POST'])
        session = Session()
        session.mount(url, HTTPAdapter(max_retries=retries))

        response = None
        try:
            if method == 'GET':
                response = session.get(url, params=params, timeout=timeout)
            elif method == 'POST' and json_data:
                response = session.post(url=url, json=json_data, timeout=timeout)
            elif method == 'PUT' and json_data:
                response = session.put(url=url, json=json_data, timeout=timeout)
            elif method == 'POST' and xml_data:
                headers = {'Content-Type': 'application/xml'}
                response = session.post(url=url, data=xml_data, headers=headers, timeout=timeout)
            else:
                current_app.logger.debug(
                    f'Invalid function params: {method}, {query}, {params}, {json_data}, {xml_data}')
                raise Exception('Invalid params given.')  # pylint: disable=broad-exception-raised
            # check for error
            if response.status_code != HTTPStatus.OK:
                error = response.json().get('error', {}).get('msg', 'Error handling Solr request.')
                raise Exception(error)  # pylint: disable=broad-exception-raised;

            return response

        except SolrConnectionError as err:
            current_app.logger.debug(err.with_traceback(None))
            raise SolrException(
                error='Connection error while handling Solr request.',
                status_code=HTTPStatus.GATEWAY_TIMEOUT) from err
        except Exception as err:  # noqa B902
            current_app.logger.debug(err.with_traceback(None))
            msg = 'Error handling Solr request.'
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            with suppress(Exception):
                status_code = response.status_code
                msg = response.json().get('error', {}).get('msg', msg)
            current_app.logger.debug(msg)
            raise SolrException(error=msg, status_code=status_code) from err

    def create_or_update_synonyms(self, synonym_type: BaseEnum, synonyms: dict[str: list[str]]):
        """Create or update solr docs in the core."""
        return self.call_solr('PUT', f'{self.synonyms_url}/{synonym_type.value}', json_data=synonyms, timeout=180)

    def delete_all_docs(self):
        """Delete all solr docs from the core."""
        payload = '<delete><query>*:*</query></delete>'
        response = self.call_solr('POST', self.update_url, xml_data=payload, timeout=60)
        return response

    def delete_docs(self, unique_keys: list[str]):
        """Delete solr docs from the core."""
        payload = '<delete><query>'
        if unique_keys:
            # TODO: set unique key in init
            payload += f'id:{unique_keys[0].upper()}'
        for key in unique_keys[1:]:
            payload += f' OR id:{key.upper()}'
        payload += '</query></delete>'

        response = self.call_solr('POST', self.update_url, xml_data=payload, timeout=60)
        return response

    def query(self, payload: dict[str, str], start: int = None, rows: int = None) -> dict:
        """Return a list of solr docs from the solr query handler for the given params."""
        payload['offset'] = start if start else self.default_start
        payload['limit'] = rows if rows else self.default_rows
        response = self.call_solr('POST', self.search_url, json_data=payload, leader=False)
        return response.json()

    def suggest(self, query: str, rows: int, build: bool = False) -> list[str]:
        """Return a list of suggestions from the solr suggest handler for the given query."""
        suggest_params = {
            'suggest.q': query,
            'suggest.count': rows if rows else self.default_rows,
            'suggest.build': str(build).lower()
        }
        # call solr
        response = self.call_solr('GET', self.suggest_url, suggest_params)
        # parse response
        suggestions = response.json() \
            .get('suggest', {}).get('name', {}).get(query, {}).get('suggestions', [])
        return [x.get('term', '').upper() for x in suggestions]  # i.e. returning list = ['COMPANY 1', 'COMPANY 2', ...]

    def reload_core(self):
        """Reload the solr core."""
        current_app.logger.info('Reloading core...')
        reload = self.call_solr(method='GET', query=self.reload_url)
        current_app.logger.info('Core reloaded.')
        return reload

    def replication(self, command: str, leader=True):
        """Send a replication command to solr."""
        current_app.logger.info(f'Sending {command} command to {"leader" if leader else "follower"}')
        resp = self.call_solr(method='GET',
                              query=self.replication_url,
                              params={'command': command},
                              leader=leader)
        current_app.logger.info(f'{command} command executed.')
        return resp
