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
"""Test-Suite to ensure that the solr doc import enpoint works as expected."""
import json
import time
from copy import deepcopy
from dataclasses import asdict
from http import HTTPStatus

import pytest
import requests_mock

from bor_api.enums import SolrDocEventStatus
from bor_api.services import bor_solr
from bor_api.services.authz import SYSTEM_ROLE

from tests.unit.utils import SOLR_TEST_DOCS, create_header
from tests import integration_solr

from . import check_update_recorded


@pytest.mark.parametrize('test_name,docs', [
    ('single', [SOLR_TEST_DOCS[0]]),
    ('multiple', SOLR_TEST_DOCS),
])
def test_import_solr_mocked(app, session, client, jwt, test_name, docs):
    """Assert that update operation sends correct payload to solr."""
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'
    docs_json = [asdict(x) for x in docs]
    with requests_mock.mock() as m:
        m.post(solr_url)
        api_response = client.put(f'/api/v1/internal/solr/import',
                                  json={'entities': docs_json},
                                  headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                               'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.CREATED

        # check call to solr was correct
        assert m.called == True
        assert m.call_count == 1  # batch updated all docs
        assert solr_url in m.request_history[0].url
        assert m.request_history[0].json() == docs_json


@integration_solr
def test_update_solr(session, client, jwt):
    """Assert that the import operation is successful."""
    # setup -- start with no docs
    bor_solr.delete_all_docs()
    # import
    docs_json = [asdict(x) for x in SOLR_TEST_DOCS]
    api_response = client.put(f'/api/v1/internal/solr/import',
                              json={'entities': docs_json},
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.CREATED

    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    for entity in SOLR_TEST_DOCS:
        search_response = bor_solr.query(payload={'query': f'id:{entity.id}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    docs_json = [asdict(x) for x in SOLR_TEST_DOCS]
    api_response = client.put(f'/api/v1/internal/solr/import',
                              json={'entities': docs_json},
                              headers=create_header(jwt, [], **{'Accept-Version': 'v1',
                                                                'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED
