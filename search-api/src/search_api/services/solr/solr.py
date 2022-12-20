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
"""Manages solr class for using search solr."""
import json
import re
from contextlib import suppress
from datetime import datetime, timedelta
from dataclasses import asdict
from http import HTTPStatus
from typing import Dict, List

import requests
from requests import Response
from flask import current_app

from search_api.exceptions import SolrException

from .solr_docs import BusinessDoc
from .solr_fields import SolrField


class Solr:
    """Wrapper around the solr instance."""

    def __init__(self, app=None):
        """Initialize this object."""
        self.app = None

        self.solr_url = None
        self.core = 'search'
        self.default_start = 0
        self.default_rows = 10
        # facets
        self.base_facets = json.dumps({
            SolrField.TYPE: {'type': 'terms', 'field': SolrField.TYPE},
            SolrField.STATE: {'type': 'terms', 'field': SolrField.STATE}})
        self.party_facets = json.dumps({
            SolrField.PARTY_ROLE: {'type': 'terms', 'field': SolrField.PARTY_ROLE},
            SolrField.PARENT_STATE: {'type': 'terms', 'field': SolrField.PARENT_STATE},
            SolrField.PARENT_TYPE: {'type': 'terms', 'field': SolrField.PARENT_TYPE}})
        # fields
        self.base_fields = f'{SolrField.BN},{SolrField.IDENTIFIER},{SolrField.NAME},{SolrField.STATE},' + \
            f'{SolrField.TYPE},{SolrField.SCORE}'
        self.nest_fields_party = f'{SolrField.PARTIES},{SolrField.PARTY_NAME},{SolrField.PARTY_ROLE},' + \
            f'{SolrField.PARTY_TYPE},[child childFilter=' + '{filter}]'
        self.party_fields = f'{SolrField.PARENT_BN},{SolrField.PARENT_IDENTIFIER},{SolrField.PARENT_NAME},' + \
            f'{SolrField.PARENT_STATE},{SolrField.PARENT_TYPE},{SolrField.PARTY_NAME},{SolrField.PARTY_ROLE},' + \
            f'{SolrField.PARTY_TYPE}'
        # query urls
        self.search_query = '{url}/{core}/query'
        self.suggest_query = '{url}/{core}/suggest'
        self.update_query = '{url}/{core}/update?commitWithin=1000&overwrite=true&wt=json'

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
                  xml_data: str = None) -> Response:
        """Call solr instance with given params."""
        try:
            if self.is_reindexing():
                err_msg = 'This resource is undergoing scheduled maintenance and will be ' \
                    f'unavailable for up to {self.app.config.get("SOLR_REINDEX_LENGTH")} minutes.'
                raise SolrException(err_msg, HTTPStatus.SERVICE_UNAVAILABLE)

            response = None
            url = query.format(url=self.solr_url, core=self.core)
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST' and json_data:
                response = requests.post(url=url, json=json_data)
            elif method == 'POST' and xml_data:
                headers = {'Content-Type': 'application/xml'}
                response = requests.post(url=url, data=xml_data, headers=headers)
            else:
                raise Exception('Invalid params given.')
            # check for error
            if response.status_code != HTTPStatus.OK:
                error = response.json().get('error', {}).get('msg', 'Error handling Solr request.')
                self.app.logger.error(f'{error}, {response.status_code}')
                raise SolrException(
                    error=error,
                    status_code=response.status_code)
            return response
        except SolrException as err:
            # pass along
            raise err
        except Exception as err:  # noqa B902
            current_app.logger.error(err.with_traceback(None))
            msg = 'Error handling Solr request.'
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            with suppress(Exception):
                status_code = response.status_code
                msg = response.json().get('error', {}).get('msg', 'Error handling Solr request.')
            raise SolrException(
                error=msg,
                status_code=status_code)

    def create_or_replace_docs(self, docs: List[BusinessDoc]):
        """Create or replace solr docs in the core."""
        update_json = [asdict(doc) for doc in docs]
        response = self.call_solr('POST', self.update_query, json_data=update_json)
        return response

    def delete_all_docs(self):
        """Delete all solr docs from the core."""
        payload = '<delete><query>*:*</query></delete>'
        response = self.call_solr('POST', self.update_query, xml_data=payload)
        return response

    def delete_docs(self, identifiers: List[str]):
        """Delete solr docs from the core."""
        payload = '<delete><query>'
        if identifiers:
            payload += f'{SolrField.IDENTIFIER}:{identifiers[0].upper()}'
        for identifier in identifiers[1:]:
            payload += f' OR {SolrField.IDENTIFIER}:{identifier.upper()}'
        payload += '</query></delete>'

        response = self.call_solr('POST', self.update_query, xml_data=payload)
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

    def query(self, params: str, start: int = None, rows: int = None) -> List:
        """Return a list of solr docs from the solr query handler for the given params."""
        params['start'] = start if start else self.default_start
        params['rows'] = rows if rows else self.default_rows

        response = self.call_solr('GET', self.search_query, params=params)
        return response.json()

    def suggest(self, query: str, rows: int, build: bool = False) -> List[str]:
        """Return a list of suggestions from the solr suggest handler for the given query."""
        suggest_params = {
            'suggest.q': query,
            'suggest.count': rows if rows else self.default_rows,
            'suggest.build': str(build).lower()
        }
        # call solr
        response = self.call_solr('GET', self.suggest_query, suggest_params)
        # parse response
        suggestions = response.json() \
            .get('suggest', {}).get('name', {}).get(query, {}).get('suggestions', [])
        return [x.get('term', '').upper() for x in suggestions]  # i.e. returning list = ['COMPANY 1', 'COMPANY 2', ...]

    # NB: to be used later for child doc searching enhancements.
    # @staticmethod
    # def build_child_query(query: str,
    #                       nest_field: SolrField,
    #                       boost_fields: List[SolrField],
    #                       search_field: SolrField) -> str:
    #     """Return a solr child query with fqs for each subsequent term."""
    #     terms = query.split()
    #     params = 'q={!parent which="*:* -_nest_path_:\\\\/' + f'{nest_field}' + '" score=Max}'
    #     params += f'(+_nest_path_:"/{nest_field}"'
    #     # add boosters
    #     for field in boost_fields:
    #         params += f' +{field}: "{query}"'
    #         params += f' +{field}: "{query}"~1'
    #         params += f' +{field}: "{query}"~2'
    #         params += f' +{field}: "{query}"~3'
    #         params += f' +{field}: "{query}"~10'
    #     # add main search match (should be less specific than booster fields in most cases)
    #     params += f' +{search_field}:{terms[0]}'
    #     for term in terms[1:]:
    #         params += f' AND {search_field}:{term}'
    #     return params + ')'

    @staticmethod
    def build_filter_query(field: SolrField, values: List[str]):
        """Return the solr filter clause for the given params."""
        filter_q = f'{field}:("{values[0]}"'
        for val in values[1:]:
            filter_q += f' OR "{val}"'
        return filter_q + ')'

    @staticmethod
    def build_split_query(query: Dict[str, str], fields: List[SolrField], wild_card_fields: List[SolrField]) -> Dict:
        """Return a solr query with fqs for each subsequent term."""
        def add_identifier(field: SolrField, term: str):
            """Return a special identifier query."""
            corp_prefix_regex = r'(^[aA-zZ]+)[0-9]+$'
            if identifier := re.search(corp_prefix_regex, term):
                prefix = identifier.group(1)
                new_term = term.replace(prefix, '', 1)
                return f'({field}:"{new_term}" AND {field}:"{prefix.upper()}")'
            return f'{field}:{term}'

        def add_to_q(q: str, fields: List[SolrField], term: str):
            """Return an updated solr q param with extra clauses."""
            identifier_fields = [SolrField.IDENTIFIER_Q, SolrField.PARENT_IDENTIFIER_Q]

            first_clause = f'({fields[0]}:{term}'
            if fields[0] in identifier_fields:
                first_clause = f'({add_identifier(fields[0], term)}'

            if not q:
                q = f'{first_clause}'
            else:
                q += f' AND {first_clause}'
            if fields[0] in wild_card_fields and fields[0] not in identifier_fields:
                q += '*'
            for field in fields[1:]:
                new_clause = f'{field}:{term}'
                if field in identifier_fields:
                    new_clause = f'{add_identifier(field, term)}'
                q += f' OR {new_clause}'
                if field in wild_card_fields and field not in identifier_fields:
                    q += '*'
            return q + ')'

        def add_to_fq(fq: str, fields: List[SolrField], terms: str):  # pylint: disable=invalid-name
            """Return an updated solr fq param with extra clauses."""
            for term in terms:
                if fq:
                    fq += f' AND ({fields[0]}:{term}'
                else:
                    fq = f'({fields[0]}:{term}'
                if fields[0] in wild_card_fields:
                    fq += '*'
                for field in fields[1:]:
                    fq += f' OR {field}:{term}'
                    if field in wild_card_fields:
                        fq += '*'
                fq += ')'
            return fq

        terms = query['value'].split()
        # add initial q param
        params = {'q': add_to_q('', fields, terms[0])}
        # add initial filter param for subsequent terms
        params['fq'] = add_to_fq('', fields, terms[1:])

        # add query clause and subsequent filter clauses for extra query items
        for key in query:
            if key == 'value' or not query[key]:
                continue
            extra_terms = query[key].split()
            # add query clause for 1st term in query[key]
            params['q'] = add_to_q(params['q'], [key], extra_terms[0])
            # add filter clause for subsequent terms in query[key]
            params['fq'] = add_to_fq(params['fq'], [key], extra_terms[1:])

        return params

    @staticmethod
    def highlight_names(query: str, names: List[str]) -> List[str]:
        """Highlight terms within names."""
        highlighted_names = []
        # TODO: add stuff in here to catch special chars / stems etc.
        for name in names:
            name = name.replace(query, f'<b>{query}</b>')
            highlighted_names.append(name)
        return highlighted_names

    @staticmethod
    def parse_facets(facet_data: Dict) -> Dict:
        """Return formatted solr facet response data."""
        facet_info = facet_data.get('facets', {})
        facets = {}
        for category in facet_info:
            if category == 'count':
                continue
            facets[category] = []
            for item in facet_info[category]['buckets']:
                facets[category].append({'value': item['val'], 'count': item['count']})

        return {'fields': facets}

    @staticmethod
    def prep_query_str(query: str) -> str:
        """Return query string prepped for solr call."""
        # replace solr specific special chars
        rmv_spec_chars_rgx = r'([\[\]!()\"~*?:/\\={}^%`#|<>,.@$;_\-])'
        handled_spec_chars_rgx = r'([&+]+)'
        query = re.sub(rmv_spec_chars_rgx, ' ', query.lower())
        return re.sub(handled_spec_chars_rgx, r' \\\1 ', query) if not query.isspace() else r'\*'
