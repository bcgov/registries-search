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
from typing import List

import requests

from search_api.exceptions import SolrException


class SolrFields(str, Enum):
    """Enum of the fields available in the solr search core."""

    BN = 'tax_id'
    BN_SELECT = 'tax_id_select'
    IDENTIFIER = 'identifier'
    IDENTIFIER_SELECT = 'identifier_select'
    NAME = 'legal_name'
    NAME_SELECT = 'name_select'
    NAME_SINGLE = 'name_single_term'
    STATE = 'state'
    TYPE = 'legal_type'


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
            SolrFields.IDENTIFIER: self.identifier,
            SolrFields.NAME: self.name,
            SolrFields.STATE: self.state,
            SolrFields.TYPE: self.legal_type,
        }
        with suppress(AttributeError):
            if self.tax_id:
                doc_json[SolrFields.BN] = self.tax_id
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
        self.facets = f'&facet=on&facet.field={SolrFields.STATE}&facet.field={SolrFields.TYPE}'
        self.fields = \
            f'&fl={SolrFields.BN},{SolrFields.IDENTIFIER},{SolrFields.NAME},{SolrFields.STATE},{SolrFields.TYPE}'
        # TODO: add in facet selection stuff + sort + suggester stuff

        self.search_query = '{url}/{core}/select?{search_params}{fields}&start={start}&rows={rows}'
        self.suggest_query = '{url}/{core}/suggest?{suggest_params}&suggest.count={rows}&suggest.build={build}'
        self.update_query = '{url}/{core}/update?commitWithin=1000&overwrite=true&wt=json'

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Solr environment."""
        self.app = app
        self.solr_url = app.config.get('SOLR_SVC_URL')

    def business_search(self, query: str):
        """Return the list of businesses from Solr that match the search criteria."""
        if not query:
            # TODO: raise error or something here
            return None
        name_query = f'{SolrFields.NAME_SELECT}:"{query}"~{len(query.split())}'
        identifier_query = f'{SolrFields.IDENTIFIER_SELECT}:{query}'
        bn_query = f'{SolrFields.BN_SELECT}:{query}'
        search_params = f'q={name_query} OR {identifier_query} OR {bn_query}'

        # query solr
        query = self.search_query.format(
            url=self.solr_url,
            core=self.core,
            search_params=search_params,
            fields=self.fields,
            start=self.default_start,
            rows=self.default_rows)
        response = requests.get(query)
        # TODO: check error, format response, etc.
        return response

    def business_suggest(self, query: str, rows: int = None) -> List:
        """Return the list of business suggestions from Solr from given text."""
        if not rows:
            rows = self.default_rows
        # 1st solr query (names)
        name_suggestions = self.suggest(query, rows)

        # 2nd solr query (extra names)
        extra_name_suggestions = []
        if len(name_suggestions) < rows:
            name_select_params = Solr.build_split_query(query, SolrFields.NAME_SINGLE)
            name_docs = self.select(name_select_params, rows)
            extra_name_suggestions = [x.get(SolrFields.NAME, '').upper() for x in name_docs]
        # remove dups
        name_suggestions = name_suggestions + list(set(extra_name_suggestions) - set(name_suggestions))
        # highlight
        name_suggestions = Solr.highlight_names(query.upper(), name_suggestions)

        # 3rd solr query (bns + identifiers)
        identifier_suggestions = []
        bn_suggestions = []
        if len(name_suggestions) < rows:
            bn_id_params = f'q={SolrFields.IDENTIFIER_SELECT}:{query} OR {SolrFields.BN_SELECT}:{query}'
            bn_id_docs = self.select(bn_id_params, rows)
            # return list of identifier strings with highlighted query
            identifier_suggestions = [
                x.get(SolrFields.IDENTIFIER).replace(query, f'<b>{query}</b>')
                for x in bn_id_docs if query in x.get(SolrFields.IDENTIFIER)]
            # return list of bn strings with highlighted query
            bn_suggestions = [
                x.get(SolrFields.BN).replace(query, f'<b>{query}</b>')
                for x in bn_id_docs if query in x.get(SolrFields.BN, '')]

        # format/combine response
        suggestions = [{'type': 'name', 'value': x} for x in name_suggestions]
        suggestions += [{'type': 'identifier', 'value': x} for x in identifier_suggestions]
        suggestions += [{'type': 'bn', 'value': x} for x in bn_suggestions]
        return suggestions[:rows]

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

    def select(self, params: str, rows: int) -> List:
        """Return a list of solr docs from the solr select handler for the given params."""
        select_query = self.search_query.format(
            url=self.solr_url,
            core=self.core,
            search_params=params,
            fields=self.fields,
            start=self.default_start,
            rows=rows)
        response = requests.get(select_query)
        if response.status_code != HTTPStatus.OK:
            raise SolrException(
                error=response.json().get('error', {}).get('msg', 'Error handling Solr request.'),
                status_code=response.status_code)

        return response.json().get('response', {}).get('docs')

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
        response = requests.get(suggest_query)
        # check for error
        if response.status_code != HTTPStatus.OK:
            raise SolrException(
                error=response.json().get('error', {}).get('msg', 'Error handling Solr request.'),
                status_code=response.status_code)
        # parse response
        suggestions = response.json() \
            .get('suggest', {}).get('name', {}).get(query, {}).get('suggestions')
        return [x.get('term', '').upper() for x in suggestions]  # i.e. returning list = ['COMPANY 1', 'COMPANY 2', ...]

    @staticmethod
    def build_split_query(query: str, field: SolrFields) -> str:
        """Return a solr query with fqs for each subsequent term."""
        terms = query.split()
        params = f'q={field}:{terms[0]}'
        # add filter query for each subsequent term
        for term in terms[1:]:
            params += f'&fq={field}:{term}'
        return params

    @staticmethod
    def highlight_names(query: str, names: List):
        """Highlight terms within names."""
        highlighted_names = []
        # TODO: add stuff in here to catch special chars / stems etc.
        for name in names:
            name = name.replace(query, f'<b>{query}</b>')
            highlighted_names.append(name)
        return highlighted_names
