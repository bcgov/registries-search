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
"""Tests to assure the Solr Services."""
from search_api.services.solr.solr_docs import BusinessDoc, PartyDoc
from search_api.services.solr.solr_fields import SolrField


def create_solr_doc(identifier, name, state, legal_type, bn=None, parties=None) -> BusinessDoc:
    solr_parties = None
    if parties:
        solr_parties = []
        for party in parties:
            party_doc = {
                SolrField.PARENT_BN.value: bn,
                SolrField.PARENT_NAME.value: name,
                SolrField.PARENT_STATE.value: state,
                SolrField.PARENT_TYPE.value: legal_type,
                SolrField.PARTY_NAME.value: party[0],
                SolrField.PARTY_ROLE.value: [party[1]],
                SolrField.PARTY_TYPE.value: party[2],
            }
            solr_parties.append(PartyDoc(**party_doc))
    return BusinessDoc(
        identifier=identifier,
        legalType=legal_type,
        name=name,
        status=state,
        bn=bn,
        parties=solr_parties
    )


SOLR_TEST_DOCS = [
    create_solr_doc('CP1234567', 'test 1234', 'ACTIVE', 'CP', 'BN00012334'),
    create_solr_doc('CP0234567', 'tester 1111', 'HISTORICAL', 'CP', '09876K'),
    create_solr_doc('CP0034567', 'tests 2222', 'ACTIVE', 'CP'),
    create_solr_doc('BC0004567', 'test 3333', 'ACTIVE', 'BEN', '00987766800988'),
    create_solr_doc('BC0000567', '4444 test', 'HISTORICAL', 'BC', 'BN9000776557'),
    create_solr_doc('BC0000067', 'single', 'ACTIVE', 'BEN', '242217'),
    create_solr_doc('BC0000007', 'lots of words in here', 'ACTIVE', 'BEN', '124221'),
    create_solr_doc('BC0020047', 'NOt Case SENSitive', 'ACTIVE', 'BEN', '1255323221'),
    create_solr_doc('FM1000028', 'sp firm', 'ACTIVE', 'SP', '123', [('person 1', 'proprietor', 'person')]),
    create_solr_doc('FM1001118', 'gp firm', 'ACTIVE', 'GP', None, [('org 1', 'partner', 'organization')]),
    create_solr_doc('FM0004018', 'gp firm multiple parties', 'ACTIVE', 'GP', None, [('test org partner', 'partner', 'organization'), ('test person partner', 'partner', 'person')]),
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
    create_solr_doc('BC0030014', 'many special =&{}^%`#|<>,.@$;_chars', 'ACTIVE', 'BEN', '123456776BC0001'),
    create_solr_doc('BC0030015', 'special OR AND NOT operators', 'ACTIVE', 'BEN', '123456775BC0001'),
    create_solr_doc('BC0030016', 'DIVINE ÉBÉNISTERIE INC.', 'ACTIVE', 'BEN', 'BN00012388'),
    create_solr_doc('BC0030017', 'special and match 1', 'ACTIVE', 'BEN', '123456780BC0001'),
    create_solr_doc('BC0030018', 'special + match 2', 'ACTIVE', 'BEN', '123456781BC0001'),
    create_solr_doc('BC0030019', 'special+match 3', 'ACTIVE', 'BEN', '123456782BC0001'),
    create_solr_doc('BC0030020', 'special & match 4', 'ACTIVE', 'BEN', '123456783BC0001'),
    create_solr_doc('BC0030021', 'special&match 5', 'ACTIVE', 'BEN', '123456784BC0001'),
    create_solr_doc('BC0030023', 'special-dash match 1', 'ACTIVE', 'BEN', '123456785BC0001'),
    create_solr_doc('BC0030024', 'special - dash match 2', 'ACTIVE', 'BEN', '123456786BC0001'),
    create_solr_doc('BC0030025', 'special dash match 3', 'ACTIVE', 'BEN', '123456787BC0001'),
    create_solr_doc('BC0030026', 'special match nothing', 'ACTIVE', 'BEN', '123456788BC0001')
]
