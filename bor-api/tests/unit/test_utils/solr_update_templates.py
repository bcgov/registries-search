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
        "addresses": [
            {
                "addressCity": "Coquitlam",
                "addressCountry": "CA",
                "addressRegion": "BC",
                "addressType": "delivery",
                "deliveryInstructions": "dial 340",
                "id": 2664213,
                "postalCode": "V3K 3V9",
                "streetAddress": "Bc-435 North Rd",
                "streetAddressAdditional": "Crystal Condos"
            }
        ],
        "email": "test@email.com",
        "identifier": "BC1233334",
        "legalName": "ABCD Corp",
        "legalType": "BEN",
        "taxId": "123456789",
        "state": "ACTIVE"
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

SOLR_UPDATE_REQUEST_OWNER_TEMPLATE = {
    "business": {
        "addresses": [{
            "addressCity": "Ladysmith",
            "addressCountry": "CA",
            "addressRegion": "BC",
            "addressType": "delivery",
            "deliveryInstructions": "bla bla",
            "postalCode": "W2R 1C1",
            "streetAddress": "123456 Lalalane",
            "streetAddressAdditional": "additional info"
        }],
        "email": "test@email.com",
        "identifier": "BC1233335",
        "legalName": "EFGH Corp",
        "legalType": "BEN",
        "taxId": "123456788BC001",
        "state": "ACTIVE"
    },
    "owners": [
        {
            "interestedParty": {
                "describedByPersonStatement": "7f0511ba-9621-4134-8363-462c61b9162a",
                "addresses": [
                    {
                        "city": "Kelowna",
                        "country": "CA",
                        "countryName": "Canada",
                        "street": "123-720 Commonwealth Rd",
                        "streetAdditional": "test street additional",
                        "locationDescription": "test description",
                        "postalCode": "V4V 1R8",
                        "region": "BC"
                    }
                ],
                "birthDate": "1997-02-05",
                "email": "test@test.com",
                "externalInfluence": "CanBeInfluenced",
                "hasTaxNumber": True,
                "identifiers": [
                    {
                        "id": "402 931 299",
                        "scheme": "CAN-TAXID",
                        "schemeName": "ITN"
                    }
                ],
                "isPermanentResidentCa": False,
                "missingInfoReason": "",
                "names": [
                    {
                        "fullName": "Kial Jinnah",
                        "type": "individual"
                    },
                    {
                        "fullName": "wallaby willow",
                        "type": "alternative"
                    }
                ],
                "nationalities": [
                    {
                        "code": "CA",
                        "name": "Canada"
                    }
                ],
                "phoneNumber": {
                    "countryCallingCode": "44",
                    "countryCode2letterIso": "GB",
                    "number": "2004567890",
                    "extension": "123"
                },
                "placeOfResidence": {
                    "city": "Kelowna",
                    "country": {
                        "alpha_2": "CA",
                        "name": "Canada"
                    },
                    "line1": "123-720 Commonwealth Rd",
                    "line2": "",
                    "locationDescription": "",
                    "postalCode": "V4V 1R8",
                    "region": "BC"
                },
                "statementDate": "2024-02-07",
                "statementID": "7f0511ba-9621-4134-8363-462c61b9162a",
                "statementType": "personStatement",
                "taxResidencies": [
                    {
                        "code": "CA",
                        "name": "Canada"
                    }
                ],
                "uuid": "123xxx-456xxx"
            },
            "interests": [
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.directors.directControl",
                    "directOrIndirect": "direct",
                    "startDate": "2020-01-01",
                    "type": "appointmentOfBoard"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.directors.inConcertControl",
                    "directOrIndirect": "direct",
                    "startDate": "2020-01-01",
                    "type": "appointmentOfBoard",
                    "connectedIndividuals": [{ "uuid": "111-feknfvn-3432dgg", "legalName": "Name One" }],
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.directors.actingJointly",
                    "directOrIndirect": "direct",
                    "startDate": "2020-01-01",
                    "type": "appointmentOfBoard",
                    "connectedIndividuals": [{ "uuid": "222-feknfvn-3432dgg", "legalName": "Name Two" }],
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.votes.registeredOwner",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2020-01-01",
                    "type": "votingRights"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.votes.indirectControl",
                    "directOrIndirect": "indirect",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2020-01-01",
                    "type": "votingRights"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.votes.inConcertControl",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2020-01-01",
                    "connectedIndividuals": [{ "uuid": "333-feknfvn-3432dgg", "legalName": "Name Three" }],
                    "type": "votingRights"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.shares.registeredOwner",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2020-01-01",
                    "type": "shareholding"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.shares.indirectControl",
                    "directOrIndirect": "indirect",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2020-01-01",
                    "type": "shareholding"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "controlType.shares.actingJointly",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2020-01-01",
                    "connectedIndividuals": [{ "uuid": "444-feknfvn-3432dgg", "legalName": "Name Four" }],
                    "type": "shareholding"
                },
                {
                    "endDate": "2023-07-07",
                    "details": "bla bla",
                    "startDate": "2020-01-01",
                    "type": "otherInfluenceOrControl"
                },
                {
                    "details": "controlType.directors.directControl",
                    "directOrIndirect": "direct",
                    "startDate": "2024-02-07",
                    "type": "appointmentOfBoard"
                },
                {
                    "details": "controlType.directors.inConcertControl",
                    "directOrIndirect": "direct",
                    "startDate": "2024-02-07",
                    "type": "appointmentOfBoard",
                    "connectedIndividuals": [{ "uuid": "111-feknfvn-3432dgg", "legalName": "Name One" }],
                },
                {
                    "details": "controlType.directors.actingJointly",
                    "directOrIndirect": "direct",
                    "startDate": "2024-02-07",
                    "type": "appointmentOfBoard",
                    "connectedIndividuals": [{ "uuid": "222-feknfvn-3432dgg", "legalName": "Name Two" }],
                },
                {
                    "details": "controlType.votes.registeredOwner",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2024-02-07",
                    "type": "votingRights"
                },
                {
                    "details": "controlType.votes.indirectControl",
                    "directOrIndirect": "indirect",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2024-02-07",
                    "type": "votingRights"
                },
                {
                    "details": "controlType.votes.inConcertControl",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 50,
                        "minimum": 25
                    },
                    "startDate": "2024-02-07",
                    "connectedIndividuals": [{ "uuid": "333-feknfvn-3432dgg", "legalName": "Name Three" }],
                    "type": "votingRights"
                },
                {
                    "details": "controlType.shares.registeredOwner",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2024-02-07",
                    "type": "shareholding"
                },
                {
                    "details": "controlType.shares.indirectControl",
                    "directOrIndirect": "indirect",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2024-02-07",
                    "type": "shareholding"
                },
                {
                    "details": "controlType.shares.actingJointly",
                    "directOrIndirect": "direct",
                    "share": {
                        "exclusiveMaximum": False,
                        "maximum": 75,
                        "minimum": 50
                    },
                    "startDate": "2024-02-07",
                    "connectedIndividuals": [{ "uuid": "444-feknfvn-3432dgg", "legalName": "Name Four" }],
                    "type": "shareholding"
                },
                {
                    "details": "bla bla",
                    "startDate": "2024-02-07",
                    "type": "otherInfluenceOrControl"
                }
            ]
        }
    ]
}
