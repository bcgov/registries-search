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
"""Tests for the api utils module."""

SOLR_UPDATE_REQUEST_TEMPLATE_CORP = {
    "business": {
        "identifier": "BC1233987",
        "legalName": "Benefit test comp",
        "legalType": "BEN",
        "taxId": "987654321BC0001",
        "state": "ACTIVE",
        "goodStanding": False
   }
}

SOLR_UPDATE_REQUEST_TEMPLATE_FIRM = {
   "business": {
        "alternateNames": [
            {
                "entityType": "SP",
                "identifier": "FM1233334",
                "nameRegisteredDate": "2022-08-15T08:00:00+00:00",
                "nameStartDate": "2022-08-16",
                "operatingName": "ABCD Prop"
            }
        ],
        "identifier": "FM1233334",
        "legalName": "Test ABC",
        "legalType": "SP",
        "taxId": "123456789",
        "state": "ACTIVE"
   },
   "parties":[{
        "officer": {
            "id": 1,
            "partyType": "organization",
            "organizationName": "TEST ABC"
        },
        "roles": [{"roleType": "proprietor"}]
    }]
}
