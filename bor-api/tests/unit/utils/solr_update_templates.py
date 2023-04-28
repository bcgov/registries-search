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
"""Tests utils module."""

SOLR_UPDATE_REQUEST_TEMPLATE = {
    "business": {
        "identifier": "FM1233334",
        "legalName": "ABCD Prop",
        "legalType": "SP",
        "taxId": "123456789",
        "state": "ACTIVE"
    },
    "businessAddresses": {
        "recordsOffice": {
            "deliveryAddress": {
                "addressCity": "Coquitlam",
                "addressCountry": "CA",
                "addressRegion": "BC",
                "addressType": "delivery",
                "deliveryInstructions": "",
                "id": 2664211,
                "postalCode": "V3K 3V9",
                "streetAddress": "Bc-435 North Rd",
                "streetAddressAdditional": ""
            },
            "mailingAddress": {
                "addressCity": "Coquitlam",
                "addressCountry": "CA",
                "addressRegion": "BC",
                "addressType": "mailing",
                "deliveryInstructions": "",
                "id": 2664210,
                "postalCode": "V3K 3V9",
                "streetAddress": "Bc-435 North Rd",
                "streetAddressAdditional": ""
            }
        },
        "registeredOffice": {
            "deliveryAddress": {
                "addressCity": "Coquitlam",
                "addressCountry": "CA",
                "addressRegion": "BC",
                "addressType": "delivery",
                "deliveryInstructions": "",
                "id": 2664213,
                "postalCode": "V3K 3V9",
                "streetAddress": "Bc-435 North Rd",
                "streetAddressAdditional": ""
            },
            "mailingAddress": {
                "addressCity": "Coquitlam",
                "addressCountry": "CA",
                "addressRegion": "BC",
                "addressType": "mailing",
                "deliveryInstructions": "",
                "id": 2664212,
                "postalCode": "V3K 3V9",
                "streetAddress": "Bc-435 North Rd",
                "streetAddressAdditional": ""
            }
        }
    },
    "parties": [
        {
            "deliveryAddress": {
                "addressCity": "Calgary",
                "addressCountry": "CA",
                "addressRegion": "AB",
                "deliveryInstructions": None,
                "id": 2664208,
                "postalCode": "T3J 3Z5",
                "streetAddress": "1234-4818 Westwinds Dr NE",
                "streetAddressAdditional": ""
            },
            "mailingAddress": {
                "addressCity": "Calgary",
                "addressCountry": "CA",
                "addressRegion": "AB",
                "deliveryInstructions": None,
                "id": 2664209,
                "postalCode": "T3J 3Z5",
                "streetAddress": "1234-4818 Westwinds Dr NE",
                "streetAddressAdditional": ""
            },
            "officer": {
                "email": "ppr@dev.com",
                "firstName": "BCREG2 LIANG",
                "id": 570343,
                "lastName": "FORTY",
                "partyType": "person"
            },
            "roles": [
                {
                    "appointmentDate": "2023-03-06",
                    "cessationDate": None,
                    "roleType": "Director"
                }
            ],
            "source": "LEAR"
        },
        {
            "deliveryAddress": {
                "addressCity": "Québec",
                "addressCountry": "CA",
                "addressRegion": "QC",
                "deliveryInstructions": None,
                "id": 2669641,
                "postalCode": "G1N 1C1",
                "streetAddress": "W-558 Rue Saint-Vallier O",
                "streetAddressAdditional": ""
            },
            "mailingAddress": {
                "addressCity": "Québec",
                "addressCountry": "CA",
                "addressRegion": "QC",
                "deliveryInstructions": None,
                "id": 2669642,
                "postalCode": "G1N 1C1",
                "streetAddress": "W-558 Rue Saint-Vallier O",
                "streetAddressAdditional": ""
            },
            "officer": {
                "email": None,
                "firstName": "BLIPPITY",
                "id": 570721,
                "lastName": "BOP",
                "partyType": "person"
            },
            "roles": [
                {
                    "appointmentDate": "2023-03-20",
                    "cessationDate": None,
                    "roleType": "Director"
                }
            ],
            "source": "LEAR"
        }
    ]
}
