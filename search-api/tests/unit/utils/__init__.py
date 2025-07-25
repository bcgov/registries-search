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
from search_api.services.business_solr.doc_fields import BusinessField, PartyField
from search_api.services.business_solr.doc_models import BusinessDoc, PartyDoc


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
        "modernized": True,
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

def create_solr_doc(identifier, name, state, legal_type, bn=None, parties=None, goodStanding=None, modernized=None) -> BusinessDoc:
    solr_parties = None
    if parties:
        solr_parties = []
        for index, party in enumerate(parties):
            party_doc = {
                PartyField.UNIQUE_KEY.value: identifier + '_' + str(index),
                PartyField.PARENT_BN.value: bn,
                PartyField.PARENT_IDENTIFIER.value: identifier,
                PartyField.PARENT_NAME.value: name,
                PartyField.PARENT_STATE.value: state,
                PartyField.PARENT_TYPE.value: legal_type,
                PartyField.PARTY_NAME.value: party[0],
                PartyField.PARTY_ROLE.value: [party[1]],
                PartyField.PARTY_TYPE.value: party[2],
            }
            solr_parties.append(PartyDoc(**party_doc))
    return BusinessDoc(
        id=identifier,
        identifier=identifier,
        legalType=legal_type,
        name=name,
        status=state,
        goodStanding=goodStanding,
        bn=bn,
        parties=solr_parties,
        modernized=modernized
    )


SOLR_TEST_DOCS = [
    create_solr_doc('CP1234567', 'business one 1', 'ACTIVE', 'CP', 'BN00012334', None, True),
    create_solr_doc('CP0234567', 'business two 2', 'HISTORICAL', 'CP', '09876K', None, True),
    create_solr_doc('CP0034567', 'business three 3', 'ACTIVE', 'CP', None, None, True),
    create_solr_doc('BC0004567', 'business four 4', 'ACTIVE', 'BEN', '00987766800988', None, False),
    create_solr_doc('BC0000567', 'business five 5', 'HISTORICAL', 'BC', 'BN9000776557', [('test si', 'significant individual', 'person')]),
    create_solr_doc('BC0000067', 'business six 6 special and match', 'ACTIVE', 'BEN', '242217'),
    create_solr_doc('BC0000007', 'business seven 7 special & match', 'ACTIVE', 'BEN', '124221'),
    create_solr_doc('BC0020047', 'business eight 8 special&match', 'ACTIVE', 'BEN', '1255323221'),
    create_solr_doc('FM1000028', 'firm nine 9 special + match', 'ACTIVE', 'SP', '123', [('person one', 'proprietor', 'person')]),
    create_solr_doc('FM1001118', 'firm ten 10 special+match', 'ACTIVE', 'GP', None, [('organization one', 'partner', 'organization')]),
    create_solr_doc('FM0004018', 'firm eleven 11 periods y.z. xk', 'ACTIVE', 'GP', None, [('organization two y.z. xk', 'partner', 'organization'), ('person two', 'partner', 'person')]),
    create_solr_doc('BC0030023', 'business twelve 12 special-match', 'ACTIVE', 'BEN', '123456785BC0001'),
    create_solr_doc('BC0030024', 'business thirteen 13 special - match', 'ACTIVE', 'BEN', '123456786BC0001'),
    create_solr_doc('BC0030014', 'b!u(si)ness fou}l{rt-een ~`@#$%^-_=[]|\\;:\'",<>./', 'ACTIVE', 'BEN', '123456776BC0001'),
    create_solr_doc('BC0030025', 'business specialmatch', 'ACTIVE', 'BEN', '123456790BC0001'),
    create_solr_doc('BC0030026', 'business special match', 'ACTIVE', 'BEN', '123456791BC0001'),
    # TODO: uncomment for 29043
    # create_solr_doc('BC0030027', 'business special.period.match.', 'ACTIVE', 'BEN', '123456792BC0001'),
    # create_solr_doc('BC0030028', 'business special. period. match.', 'ACTIVE', 'BEN', '123456793BC0001'),
    # create_solr_doc('BC0030029', 'business specialperiodmatch', 'ACTIVE', 'BEN', '123456794BC0001'),
    # create_solr_doc('BC0030030', 'business special period match', 'ACTIVE', 'BEN', '123456795BC0001'),
    create_solr_doc('BC0030001', '01 solr special && char', 'ACTIVE', 'BEN', '123456789BC0001'),
    create_solr_doc('BC0030002', '02 solr special || char', 'ACTIVE', 'BEN', '123456788BC0001'),
    create_solr_doc('BC0030003', '03 solr special: char', 'ACTIVE', 'BEN', '123456787BC0001'),
    create_solr_doc('BC0030004', '04 solr special + char', 'ACTIVE', 'BEN', '123456786BC0001'),
    create_solr_doc('BC0030005', '05 solr special - char', 'ACTIVE', 'BEN', '123456785BC0001'),
    create_solr_doc('BC0030006', '06 solr special ! char', 'ACTIVE', 'BEN', '123456784BC0001'),
    create_solr_doc('BC0030007', '07 solr special \ char', 'ACTIVE', 'BEN', '123456783BC0001'),
    create_solr_doc('BC0030008', '08 solr special (char)', 'ACTIVE', 'BEN', '123456782BC0001'),
    create_solr_doc('BC0030009', '09 solr special " char"', 'ACTIVE', 'BEN', '123456781BC0001'),
    create_solr_doc('BC0030010', '10 solr special ~ char', 'ACTIVE', 'BEN', '123456780BC0001'),
    create_solr_doc('BC0030011', '11 solr special* char', 'ACTIVE', 'BEN', '123456779BC0001'),
    create_solr_doc('BC0030012', '12 solr special? char', 'ACTIVE', 'BEN', '123456778BC0001'),
    create_solr_doc('BC0030013', '13 solr special / char', 'ACTIVE', 'BEN', '123456777BC0001'),
    create_solr_doc('BC0030015', 'special OR AND NOT operators', 'ACTIVE', 'BEN', '123456775BC0001'),
    create_solr_doc('BC0030016', 'DIVINE ÉBÉNISTERIE INC.', 'ACTIVE', 'BEN', 'BN00012388'),
    create_solr_doc('C0004569', 'c_identifier', 'ACTIVE', 'C', '111111111BC0001'),
    create_solr_doc('BC0030017', 'Modernized flag set', 'ACTIVE', 'BC', '111111112BC0001', None, True, True)
]
