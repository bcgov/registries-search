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
"""Test-Suite to ensure that the solr business update endpoints/functions work as expected."""
import json
import copy
from datetime import datetime
from http import HTTPStatus

from dateutil.relativedelta import relativedelta

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User
from search_api.services.authz import STAFF_ROLE
from search_api.services.validator import RequestValidator
from tests.unit import MockResponse
from tests.unit.services.utils import create_header
from tests import integration_solr

REQUEST_TEMPLATE = {
   "business":{
      "identifier":"BC1233334",
      "legalName":"ABCD Corp",
      "legalType":"BEN",
      "taxId":"123456789",
      "status":"ACTIVE"
   },
   "parties":[
      {
         "id":1,
         "partyType":"organization",
         "organizationName":"TEST ABC",
         "roles":[
            "director",
            "incorporator"
         ]
      }
   ]
}

@integration_solr
def test_update_business_in_solr(session, client, jwt, mocker):
    """Assert that update operation is successful."""
    api_response = client.put(f'/api/v1/businesses/update',
                     data=json.dumps(REQUEST_TEMPLATE),
                    headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                'content-type': 'application/json'})
                    )
    # check
    assert api_response.status_code == HTTPStatus.OK


@integration_solr
def test_update_business_in_solr_missing_data(session, client, jwt, mocker):
    """Assert that error is returned."""
    request_json = copy.deepcopy(REQUEST_TEMPLATE)
    del request_json['business']['identifier']
    api_response = client.put(f'/api/v1/businesses/update',
                     data=json.dumps(request_json),
                    headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                'content-type': 'application/json'})
                    )
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST


@integration_solr
def test_update_business_in_solr_invalid_data(session, client, jwt, mocker):
    """Assert that error is returned."""
    request_json = copy.deepcopy(REQUEST_TEMPLATE)
    request_json['parties'][0]['partyType'] = 'test'
    api_response = client.put(f'/api/v1/businesses/update',
                     data=json.dumps(request_json),
                    headers=create_header(jwt, [STAFF_ROLE], **{'Accept-Version': 'v1',
                                                                'content-type': 'application/json'})
                    )
    # check
    assert api_response.status_code == HTTPStatus.BAD_REQUEST

