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
"""Manages solr classes for search."""
from contextlib import suppress
from enum import Enum
from http import HTTPStatus
from typing import Dict, List

import requests
from flask import current_app

from search_api.exceptions import SolrException


class SolrField(str, Enum):
    """Enum of the fields available in the solr search core."""

    BN = 'bn'
    BN_SELECT = 'bn_select'
    IDENTIFIER = 'identifier'
    IDENTIFIER_SELECT = 'identifier_select'
    NAME = 'name'
    NAME_SELECT = 'name_select'
    NAME_SINGLE = 'name_single_term'
    NAME_STEM_AGRO = 'name_stem_agro'
    NAME_SYNONYM = 'name_synonym'
    SCORE = 'score'
    STATE = 'status'
    TYPE = 'legalType'


class SolrDoc:  # pylint: disable=too-few-public-methods
    """Class representation for a solr search core doc."""

    # TODO: make enums for state and type
    def __init__(self, identifier: str, name: str, state: str, legal_type: str, tax_id: str = None):
        # pylint: disable=too-many-arguments
        """Initialize this object."""
        self.identifier = identifier
        self.name = name
        self.state = state
        self.legal_type = legal_type
        if tax_id:
            self.tax_id = tax_id

    def json(self):
        """Return the dict representation of a SolrDoc."""
        doc_json = {
            SolrField.IDENTIFIER: self.identifier,
            SolrField.NAME: self.name,
            SolrField.STATE: self.state,
            SolrField.TYPE: self.legal_type,
        }
        with suppress(AttributeError):
            if self.tax_id:
                doc_json[SolrField.BN] = self.tax_id
        return doc_json


class Solr:
    """Wrapper around the solr instance."""

    def __init__(self, app=None):
        """Initialize this object."""
        self.app = None

        self.solr_url = None
        self.core = 'search'
        self.default_start = 0
        self.default_rows = 10
        self.facets = f'&facet=on&facet.field={SolrField.STATE}&facet.field={SolrField.TYPE}'
        self.fields = f'&fl={SolrField.BN},{SolrField.IDENTIFIER},{SolrField.NAME},{SolrField.STATE},' + \
            f'{SolrField.TYPE},{SolrField.SCORE}'
        self.boost_params = '{boost_params}&defType=edismax'

        self.search_query = '{url}/{core}/select?{search_params}{fields}&start={start}&rows={rows}'
        self.suggest_query = '{url}/{core}/suggest?{suggest_params}&suggest.count={rows}&suggest.build={build}'
        self.update_query = '{url}/{core}/update?commitWithin=1000&overwrite=true&wt=json'

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Solr environment."""
        self.app = app
        self.solr_url = app.config.get('SOLR_SVC_URL')

    def create_or_replace_docs(self, docs: List):
        """Create or replace solr docs in the core."""
        url = self.update_query.format(url=self.solr_url, core=self.core)
        response = requests.post(url=url, json=docs)
        return response

    def delete_all_docs(self):
        """Delete all solr docs from the core."""
        payload = '<delete><query>*:*</query></delete>'
        delete_url = self.update_query.format(url=self.solr_url, core=self.core)
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=delete_url, data=payload, headers=headers)
        return response

    def delete_docs(self, identifiers: List):
        """Delete solr docs from the core."""
        payload = '<add><delete>'
        for identifier in identifiers:
            payload += f'<id>{identifier.upper()}</id>'
        payload += '</delete></add>'

        delete_url = self.update_query.format(url=self.solr_url, core=self.core)
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=delete_url, data=payload, headers=headers)
        return response

    def select(self, params: str, start: int, rows: int) -> List:
        """Return a list of solr docs from the solr select handler for the given params."""
        select_query = self.search_query.format(
            url=self.solr_url,
            core=self.core,
            search_params=params,
            fields=self.fields,
            start=start,
            rows=rows)
        try:
            response = requests.get(select_query)
            if response.status_code != HTTPStatus.OK:
                raise SolrException('Error handling Solr request.', response.status_code)
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

        return response.json()

    def suggest(self, query: str, rows: int, build: bool = False) -> List:
        """Return a list of suggestions from the solr suggest handler for the given query."""
        suggest_params = f'suggest.q={query}'
        # build solr query
        suggest_query = self.suggest_query.format(
            url=self.solr_url,
            core=self.core,
            suggest_params=suggest_params,
            rows=rows,
            build=str(build).lower())
        # call solr
        try:
            response = requests.get(suggest_query)
            # check for error
            if response.status_code != HTTPStatus.OK:
                raise SolrException(
                    error=response.json().get('error', {}).get('msg', 'Error handling Solr request.'),
                    status_code=response.status_code)
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
        # parse response
        suggestions = response.json() \
            .get('suggest', {}).get('name', {}).get(query, {}).get('suggestions', [])
        return [x.get('term', '').upper() for x in suggestions]  # i.e. returning list = ['COMPANY 1', 'COMPANY 2', ...]

    @staticmethod
    def build_split_query(query: str, fields: List, wild_card_fields: List) -> str:
        """Return a solr query with fqs for each subsequent term."""
        terms = query.split()
        params = f'q={fields[0]}:{terms[0]}'
        if fields[0] in wild_card_fields:
            params += '*'
        for field in fields[1:]:
            params += f' OR {field}:{terms[0]}'
            if field in wild_card_fields:
                params += '*'
        # add filter query for each subsequent term
        for term in terms[1:]:
            params += f'&fq={fields[0]}:{term}'
            if fields[0] in wild_card_fields:
                params += '*'
            for field in fields[1:]:
                params += f' OR {field}:{term}'
                if field in wild_card_fields:
                    params += '*'
        return params

    @staticmethod
    def highlight_names(query: str, names: List) -> List:
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
        facet_info = facet_data.get('facet_counts', {}).get('facet_fields')
        facets = {}
        for category in facet_info:
            facets[category] = []
            for i in range(len(facet_info[category])):
                # even indexes are values, odd indexes are counts - i.e. category = ['BEN',12,'CP',100]
                if i % 2 == 0:
                    facets[category].append({
                        'value': facet_info[category][i],
                        'count': facet_info[category][i+1]})

        return {'fields': facets}
