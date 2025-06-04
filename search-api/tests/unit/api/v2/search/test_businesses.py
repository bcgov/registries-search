# Copyright © 2024 Province of British Columbia
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
"""Test-Suite to ensure that the business search endpoints/functions work as expected."""
import time
from http import HTTPStatus

import pytest

from search_api.services import business_solr
from search_api.services.business_solr.doc_fields import BusinessField

from tests import integration_solr
from tests.unit.utils import SOLR_TEST_DOCS


@pytest.mark.parametrize('test_name,query,categories', [
    ('test_basic', {'value': '123'}, {}),
    ('test_filters',
     {'value': 'test filters', BusinessField.NAME.value: 'name', BusinessField.IDENTIFIER.value: 'BC23', BusinessField.BN.value: '023'},
     {}
    ),
    ('test_categories',
     {'value': 'test categories'},
     {BusinessField.STATE.value:['ACTIVE'], BusinessField.TYPE.value: ['BC', 'CP', 'SP']}
    ),
    ('test_all_combined',
     {
        'value': 'test all combined',
        BusinessField.NAME.value: 'name',
        BusinessField.IDENTIFIER.value: 'BC23',
        BusinessField.BN.value: '023'
     },
     {
        BusinessField.STATE.value:['ACTIVE'],
        BusinessField.TYPE.value: ['BC', 'CP', 'SP']
     })
])
def test_businesses_solr_mock(app, session, client, requests_mock, test_name, query, categories):
    """Assert that the entities search call works returns successfully."""
    # setup mocks
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'response': {'docs': [], 'numFound': 0, 'start': 0}})
    # call search
    resp = client.post('/api/v2/search/businesses',
                       headers={'content-type': 'application/json'},
                       json={'query': query, 'categories': categories})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets'] == {'fields': {}}
    assert resp_json['searchResults']['queryInfo']['rows'] == 10
    assert resp_json['searchResults']['queryInfo']['start'] == 0
    assert resp_json['searchResults']['results'] == []
    assert resp_json['searchResults']['totalResults'] == 0


@integration_solr
@pytest.mark.parametrize('test_name,query,categories,expected', [
    ('test_basic_name',  # NOTE: test setup checks for 'test_basic_name' on the first run
     {'value': 'business one'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_case',
     {'value': 'BusIness ONE'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_partial_1',
     {'value': 'bus one'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_partial_2',
     {'value': 'siness on'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_partial_3',
     {'value': 'IVINE STERI'},
     {},
     [{'bn': 'BN00012388', 'identifier': 'BC0030016', 'legalType': 'BEN', 'name': 'DIVINE ÉBÉNISTERIE INC.', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_spellcheck',
     {'value': 'basiness thrae'},
     {},
     [{'goodStanding': True, 'identifier': 'CP0034567', 'legalType': 'CP', 'name': 'business three 3', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_stem_1',
     {'value': 'business eights'},
     {},
     [{'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_stem_2',
     {'value': 'businessing one'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_stem_3',
     {'value': 'businessed one'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_mix',
     {'value': 'one business'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_mix_partial',
     {'value': 'STERI IVINE'},
     {},
     [{'bn': 'BN00012388', 'identifier': 'BC0030016', 'legalType': 'BEN', 'name': 'DIVINE ÉBÉNISTERIE INC.', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_mix_stem',
     {'value': 'one businesses'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_adv_chars',
     {'value': 'b*s o?e "1"'},
     {},
     [{'bn': 'BN00012334', 'goodStanding': True, 'identifier': 'CP1234567', 'legalType': 'CP', 'name': 'business one 1', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_spec_char',
     {'value': 'b!u(si)ness fou}l{rt-een ~`@#$%^-_=[]|\\;:\'",<>./'},
     {},
     [{'bn': '123456776BC0001', 'identifier': 'BC0030014', 'legalType': 'BEN', 'name': 'b!u(si)ness fou}l{rt-een ~`@#$%^-_=[]|\\;:\'",<>./', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_and_and',
     {'value': 'special and match'},
     {},
     [{'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_and_&_1',
     {'value': 'special & match'},
     {},
     [{'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_and_&_2',
     {'value': 'special&match'},
     {},
     [{'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_and_+_1',
     {'value': 'special + match'},
     {},
     [{'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_and_+_2',
     {'value': 'special+match'},
     {},
     [{'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_._1',
     {'value': 'firm eleven y.z.'},
     {},
     [{'identifier': 'FM0004018', 'legalType': 'GP', 'name': 'firm eleven 11 periods y.z. xk', 'parties': [{'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}, {'partyName': 'person two', 'partyRoles': ['partner'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_._2',
     {'value': 'firm eleven yz'},
     {},
     [{'identifier': 'FM0004018', 'legalType': 'GP', 'name': 'firm eleven 11 periods y.z. xk', 'parties': [{'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}, {'partyName': 'person two', 'partyRoles': ['partner'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_._3',
     {'value': 'firm eleven x.k.'},
     {},
     [{'identifier': 'FM0004018', 'legalType': 'GP', 'name': 'firm eleven 11 periods y.z. xk', 'parties': [{'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}, {'partyName': 'person two', 'partyRoles': ['partner'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_._4',
     {'value': 'firm eleven xk'},
     {},
     [{'identifier': 'FM0004018', 'legalType': 'GP', 'name': 'firm eleven 11 periods y.z. xk', 'parties': [{'partyName': 'organization two y.z. xk', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}, {'partyName': 'person two', 'partyRoles': ['partner'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_-_1',
     {'value': 'special - match'},
     {},
     [{'bn': '123456786BC0001', 'identifier': 'BC0030024', 'legalType': 'BEN', 'name': 'business thirteen 13 special - match', 'status': 'ACTIVE'},
      {'bn': '123456785BC0001', 'identifier': 'BC0030023', 'legalType': 'BEN', 'name': 'business twelve 12 special-match', 'status': 'ACTIVE'},
      {'bn': '123456791BC0001', 'identifier': 'BC0030026', 'legalType': 'BEN', 'name': 'business special match', 'status': 'ACTIVE'},
      {'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'},
      {'bn': '123456790BC0001', 'identifier': 'BC0030025', 'legalType': 'BEN', 'name': 'business specialmatch', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_-_2',
     {'value': 'special-match'},
     {},
     [{'bn': '123456785BC0001', 'identifier': 'BC0030023', 'legalType': 'BEN', 'name': 'business twelve 12 special-match', 'status': 'ACTIVE'},
      {'bn': '123456786BC0001', 'identifier': 'BC0030024', 'legalType': 'BEN', 'name': 'business thirteen 13 special - match', 'status': 'ACTIVE'},
      {'bn': '123456791BC0001', 'identifier': 'BC0030026', 'legalType': 'BEN', 'name': 'business special match', 'status': 'ACTIVE'},
      {'bn': '123456790BC0001', 'identifier': 'BC0030025', 'legalType': 'BEN', 'name': 'business specialmatch', 'status': 'ACTIVE'},
      {'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_-_3',
     {'value': 'special match'},
     {},
     [{'bn': '123456791BC0001', 'identifier': 'BC0030026', 'legalType': 'BEN', 'name': 'business special match', 'status': 'ACTIVE'},
      {'bn': '242217', 'identifier': 'BC0000067', 'legalType': 'BEN', 'name': 'business six 6 special and match', 'status': 'ACTIVE'},
      {'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'},
      {'bn': '1255323221', 'identifier': 'BC0020047', 'legalType': 'BEN', 'name': 'business eight 8 special&match', 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'},
      {'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'},
      {'bn': '123456786BC0001', 'identifier': 'BC0030024', 'legalType': 'BEN', 'name': 'business thirteen 13 special - match', 'status': 'ACTIVE'},
      {'bn': '123456790BC0001', 'identifier': 'BC0030025', 'legalType': 'BEN', 'name': 'business specialmatch', 'status': 'ACTIVE'},
      {'bn': '123456785BC0001', 'identifier': 'BC0030023', 'legalType': 'BEN', 'name': 'business twelve 12 special-match', 'status': 'ACTIVE'}]
    ),
    ('test_basic_name_-_4',
     {'value': 'specialmatch'},
     {},
     [{'bn': '123456790BC0001', 'identifier': 'BC0030025', 'legalType': 'BEN', 'name': 'business specialmatch', 'status': 'ACTIVE'},
      {'bn': '123456785BC0001', 'identifier': 'BC0030023', 'legalType': 'BEN', 'name': 'business twelve 12 special-match', 'status': 'ACTIVE'}]
    ),
    ('test_basic_identifier',
     {'value': 'BC0004567'},
     {},
     [{'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_identifier_partial',
     {'value': 'BC00045'},
     {},
     [{'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_identifier_order_1',
     {'value': 'C000456'},
     {},
     [{'bn': '111111111BC0001', 'identifier': 'C0004569', 'legalType': 'C', 'name': 'c_identifier', 'status': 'ACTIVE'},
      {'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_identifier_order_2',
     {'value': 'C0004'},
     {},
     [{'bn': '111111111BC0001', 'identifier': 'C0004569', 'legalType': 'C', 'name': 'c_identifier', 'status': 'ACTIVE'},
      {'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'},
      {'bn': '123456786BC0001', 'identifier': 'BC0030004', 'legalType': 'BEN', 'name': '04 solr special + char', 'status': 'ACTIVE'}]
    ),
    ('test_basic_identifier_no_spellcheck',
     {'value': 'BC1004567'},
     {},
     []
    ),
    ('test_basic_bn',
     {'value': '00987766800988'},
     {},
     [{'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_bn_partial',
     {'value': '00987766'},
     {},
     [{'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_bn_no_spellcheck',
     {'value': '00987766800989'},
     {},
     []
    ),
    ('test_basic_combined',
     {'value': 'business BC0004567 00987766800988'},
     {},
     [{'bn': '00987766800988', 'goodStanding': False, 'identifier': 'BC0004567', 'legalType': 'BEN', 'name': 'business four 4', 'status': 'ACTIVE'}]
    ),
    ('test_basic_no_match', {'value': 'zzz no match here qljrb'}, {},[]),
    ('test_basic_name_space', {'value': ' '}, {}, []),
    ('test_filters_name',
     {'value': 'business', BusinessField.NAME.value: 'three'},
     {},
     [{'goodStanding': True, 'identifier': 'CP0034567', 'legalType': 'CP', 'name': 'business three 3', 'status': 'ACTIVE'}]
    ),
    ('test_filters_name_&',
     {'value': 'business seven 7 special & match', BusinessField.NAME.value: 'special & match'},
     {},
     [{'bn': '124221', 'identifier': 'BC0000007', 'legalType': 'BEN', 'name': 'business seven 7 special & match', 'status': 'ACTIVE'}]
    ),
    ('test_filters_name_+',
     {'value': '04 solr special + char', BusinessField.NAME.value: 'special + char'},
     {},
     [{'bn': '123456786BC0001', 'identifier': 'BC0030004', 'legalType': 'BEN', 'name': '04 solr special + char', 'status': 'ACTIVE'}]
    ),
    ('test_filters_parties_1',
     {'value': '0', 'parties': {'partyName': 'test'}},
     {},
     [{'bn': 'BN9000776557', 'identifier': 'BC0000567', 'legalType': 'BC', 'name': 'business five 5', 'parties': [{'partyName': 'test si', 'partyRoles': ['significant individual'], 'partyType': 'person', 'score': 0.0}], 'status': 'HISTORICAL'}]
    ),
    ('test_filters_parties_2',
     {'value': '0', 'parties': {'partyName': 'one'}},
     {},
     [{'identifier': 'FM1001118', 'legalType': 'GP', 'name': 'firm ten 10 special+match', 'parties': [{'partyName': 'organization one', 'partyRoles': ['partner'], 'partyType': 'organization', 'score': 0.0}], 'status': 'ACTIVE'},
      {'bn': '123', 'identifier': 'FM1000028', 'legalType': 'SP', 'name': 'firm nine 9 special + match', 'parties': [{'partyName': 'person one', 'partyRoles': ['proprietor'], 'partyType': 'person', 'score': 0.0}], 'status': 'ACTIVE'}]
    ),
    # ('test_filters_no_match',
    #  {'value': 'business', BusinessField.NAME.value: 'threa'},
    #  {},
    #  []
    # ),
    ('test_categories_state',
     {'value': 'business two'},
     {BusinessField.TYPE.value: ['CP']},
     [{'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'}]
    ),
    ('test_categories_no_match',
     {'value': 'business two'},
     {BusinessField.TYPE.value: ['BEN']},
     []
    ),
    ('test_all_combined',
     {
        'value': 'business',
        BusinessField.NAME.value: 'two',
        BusinessField.IDENTIFIER.value: 'CP0234567',
        BusinessField.BN.value: '09876K',
     },
     {
        BusinessField.STATE.value: ['HISTORICAL'],
        BusinessField.TYPE.value: ['CP']
     },
     [{'bn': '09876K', 'goodStanding': True, 'identifier': 'CP0234567', 'legalType': 'CP', 'name': 'business two 2', 'status': 'HISTORICAL'}]
    )
])
def test_businesses(app, session, client, test_name, query, categories, expected):
    """Assert that the business search call works returns successfully."""
    # test setup
    if test_name == 'test_basic_name':
        # setup solr data for test (only needed the first time)
        business_solr.delete_all_docs()
        time.sleep(1)
        business_solr.create_or_replace_docs(SOLR_TEST_DOCS)
        time.sleep(2)

    # call search
    resp = client.post('/api/v2/search/businesses',
                       headers={'content-type': 'application/json'},
                       json={'query': query, 'categories': categories})
    # test
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.json
    assert resp_json['facets']
    assert resp_json['searchResults']
    results = resp_json['searchResults']['results']
    for result in results:
        del result['score']
    assert resp_json['searchResults']['totalResults'] == len(expected)
    assert results == expected


def test_search_error(app, session, client, requests_mock):
    """Assert that the business search call error handling works as expected."""
    # setup solr error mock
    mocked_error_msg = 'mocked error'
    mocked_status_code = HTTPStatus.BAD_GATEWAY
    requests_mock.post(f"{app.config.get('SOLR_SVC_BUS_LEADER_URL')}/business/query", json={'error': {'msg': mocked_error_msg}}, status_code=mocked_status_code)
    # call search
    resp = client.post('/api/v2/search/businesses',
                       headers={'content-type': 'application/json'},
                       json={'query': {'value': 'test'}})
    # test
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    resp_json = resp.json
    assert resp_json.get('detail') == f'{mocked_error_msg}, {mocked_status_code}'
    assert resp_json.get('message') == 'Solr service error while processing request.'


@pytest.mark.parametrize('test_name,query,errors', [
    ('test_no_query', {}, [{'Invalid payload': "Expected an object for 'query'."}]),
    ('test_invalid_query', {'query': 'wrong'}, [{'Invalid payload': "Expected an object for 'query'."}]),
    ('test_no_value', {'query': {'notValue': 'bla'}}, [{'Invalid payload': "Expected a string for 'query/value'."}]),
    ('test_invalid_value', {'query': {'value': 1}}, [{'Invalid payload': "Expected a string for 'query/value'."}]),
    ('test_invalid_parties', {'query': {'value': 'test', 'parties': 'wrong'}}, [{'Invalid payload': "Expected an object for 'query/parties'."}]),
    ('test_invalid_category', {'query': {'value': 'test'}, 'categories': {'status': 'CP'}}, [{'Invalid payload': "Expected a list for 'categories/status'."}]),
    ('test_invalid_start_1',
     {'query': {'value': 'test'}, 'start': -10},
     [{'Invalid payload': "Expected 'start' to be >= 0."}]),
    ('test_invalid_start_2',
     {'query': {'value': 'test'}, 'start': 'lala'},
     [{'Invalid payload': "Expected integer for params: 'start', 'rows'"}]),
    ('test_invalid_rows_1',
     {'query': {'value': 'test'}, 'rows': -22},
     [{'Invalid payload': "Expected 'rows' to be between 0 and 10000."}]),
    ('test_invalid_rows_2',
     {'query': {'value': 'test'}, 'rows': 200000},
     [{'Invalid payload': "Expected 'rows' to be between 0 and 10000."}]),
    ('test_invalid_rows_2',
     {'query': {'value': 'test'}, 'rows': '&899'},
     [{'Invalid payload': "Expected integer for params: 'start', 'rows'"}]),
])
def test_search_bad_request(app, session, client, test_name, query, errors):
    """Assert that the business search call validates the payload."""
    # call search
    resp = client.post('/api/v2/search/businesses',
                       headers={'content-type': 'application/json'},
                       json=query)
    # test
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp_json = resp.json
    assert resp_json.get('message') == 'Errors processing request.'
    assert resp_json.get('details') == errors

