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
from enum import Enum
from typing import List

import requests


class SolrFields(str, Enum):
    """Enum of the fields available in the solr search core."""

    BN = 'tax_id'
    IDENTIFIER = 'identifier'
    NAME = 'legal_name'
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
        self.start = 0
        self.rows = 10
        self.facets = f'&facet=on&facet.field={SolrFields.STATE}&facet.field={SolrFields.TYPE}'
        self.fields = \
            f'&fl={SolrFields.BN},{SolrFields.IDENTIFIER},{SolrFields.NAME},{SolrFields.STATE},{SolrFields.TYPE}'
        # TODO: add in facet selection stuff + sort + suggester stuff

        self.search_query = '{url}/{core}/select?q=*:*&wt=json{search_params}{fields}&start={start}&rows={rows}'
        self.update_query = '{url}/{core}/update?commitWithin=1000&overwrite=true&wt=json'

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Solr environment."""
        self.app = app
        self.solr_url = app.config.get('SOLR_SVC_URL')

    def business_search(self, legal_name: str = None, identifier: str = None):
        """Return the list of businesses from Solr that match the search criteria."""
        search_params = ''
        # build search params
        if legal_name:
            search_params += f'&fq={SolrFields.NAME}:"{legal_name}"~{len(legal_name.split())}'
        if identifier:
            search_params += f'&fq={SolrFields.IDENTIFIER}:{identifier}'
        search_params += self.facets

        # query solr
        query = self.search_query.format(
            url=self.solr_url,
            core=self.core,
            search_params=search_params,
            fields=self.fields,
            start=self.start,
            rows=self.rows
        )
        response = requests.get(query)
        return response

    def create_or_replace_docs(self, docs: List):
        """Create or replace solr docs in the core."""
        url = self.update_query.format(
            url=self.solr_url,
            core=self.core
        )
        response = requests.post(url=url, json=docs)
        return response

    def delete_docs(self, identifiers: List):
        """Delete solr docs from the core."""
        payload = '<add><delete>'
        for identifier in identifiers:
            payload += f'<id>{identifier.upper()}</id>'
        payload += '</delete></add>'

        update_url = self.update_query.format(
            url=self.solr_url,
            core=self.core
        )
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=update_url, data=payload, headers=headers)
        return response
