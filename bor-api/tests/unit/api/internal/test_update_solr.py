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
"""Test-Suite to ensure that the solr business update endpoints/functions work as expected."""
import json
import time
from copy import deepcopy
from http import HTTPStatus

import pytest
import requests_mock

from bor_api.enums import SolrDocEventStatus, SolrDocEventType
from bor_api.models import SolrDoc
from bor_api.services import bor_solr
from bor_api.services.authz import SYSTEM_ROLE
from bor_api.services.solr.solr_docs import Entity

from tests.unit.utils import SOLR_UPDATE_REQUEST_TEMPLATE as REQUEST_TEMPLATE, create_header
from tests import integration_solr


# setup SP version of REQUEST_TEMPLATE
SP_REQUEST_TEMPLATE = deepcopy(REQUEST_TEMPLATE)
SP_REQUEST_TEMPLATE['business']['identifier'] = 'FM1233334'
SP_REQUEST_TEMPLATE['business']['legalType'] = 'SP'
SP_REQUEST_TEMPLATE['business']['legalName'] = 'ABCD Prop'
SP_REQUEST_TEMPLATE['businessAddresses']['businessOffice'] = SP_REQUEST_TEMPLATE['businessAddresses']['registeredOffice']
del SP_REQUEST_TEMPLATE['businessAddresses']['registeredOffice']
del SP_REQUEST_TEMPLATE['businessAddresses']['recordsOffice']

def check_update_recorded(identifier: str, is_party: bool = False):
    """Assert the given identifier was recorded for an update."""
    solr_doc = SolrDoc.find_most_recent_by_identifier(identifier)
    assert solr_doc.identifier == identifier
    assert Entity(**solr_doc.doc).identifier == identifier
    identifier_q_set = Entity(**solr_doc.doc).identifier_q == identifier
    assert not identifier_q_set if is_party else identifier_q_set
    assert solr_doc._submitter_id is not None
    doc_events = solr_doc.solr_doc_events.all()
    assert len(doc_events) == 1
    assert doc_events[0].event_status == SolrDocEventStatus.COMPLETE
    assert doc_events[0].event_type == SolrDocEventType.UPDATE


@pytest.mark.parametrize('test_name,request_json', [
    ('ben', REQUEST_TEMPLATE),
    ('sp', SP_REQUEST_TEMPLATE),
])
def test_update_solr_mocked(app, session, client, jwt, test_name, request_json):
    """Assert that update operation sends correct payload to solr."""
    solr_url = app.config.get('SOLR_SVC_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url)
        
        api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check business update
        check_update_recorded(request_json['business']['identifier'])
        # check parties update
        for party in request_json['parties']:
            identifier = f"{party['source']}{party['officer']['id']}"
            check_update_recorded(identifier, True)
        
        # check call to solr mock
        assert m.called == True
        assert m.call_count == 3  # 1 for business plus 1 for each party
        assert solr_url in m.request_history[0].url
        assert solr_url in m.request_history[1].url
        assert solr_url in m.request_history[2].url
        assert m.request_history[0].json() == [{
            'entityAddresses': [{'address_q': 'Bc-435 North Rd Coquitlam BC CA V3K 3V9',
                                  'postalCode': 'V3K 3V9',
                                  'addressCity': 'Coquitlam',
                                  'addressType': 'delivery',
                                  'addressRegion': 'BC',
                                  'streetAddress': 'Bc-435 North Rd',
                                  'addressCountry': 'CA'}],
            'entityType': 'BUSINESS',
            'identifier': request_json['business']['identifier'],
            'legalName': request_json['business']['legalName'],
            'bn': '123456789',
            'bnSP': None,
            'identifier_q': request_json['business']['identifier'],
            'legalType': request_json['business']['legalType'],
            'operatingName': None,
            'roles': None,
            'state': 'ACTIVE'
        }]
        
        assert m.request_history[1].json() == [{
            'entityAddresses': [{
                'address_q': '1234-4818 Westwinds Dr NE Calgary AB CA T3J 3Z5',
                'postalCode': 'T3J 3Z5',
                'addressCity': 'Calgary',
                'addressType': '',
                'addressRegion': 'AB',
                'streetAddress': '1234-4818 Westwinds Dr NE',
                'addressCountry': 'CA'}],
            'entityType': 'PERSON',
            'identifier': 'LEAR570343',
            'legalName': 'BCREG2 LIANG FORTY',
            'bn': None,
            'bnSP': None,
            'identifier_q': None,
            'legalType': None,
            'operatingName': None,
            'roles': [{
                'roleType': 'Director',
                'relatedBN': '123456789',
                'roleDates': [{'active': True, 'end': None, 'start': '2023-03-06'}],
                'relatedName': request_json['business']['legalName'],
                'relatedState': 'ACTIVE',
                'related_q': f"{request_json['business']['legalName']} {request_json['business']['identifier']} 123456789",
                'relatedLegalType': request_json['business']['legalType'],
                'relatedEntityType': 'BUSINESS',
                'relatedIdentifier': request_json['business']['identifier'],}],
            'state': None}]
        
        assert m.request_history[2].json() == [{
            'entityAddresses': [{
                'address_q': 'W-558 Rue Saint-Vallier O Québec QC CA G1N 1C1',
                'postalCode': 'G1N 1C1',
                'addressCity': 'Québec',
                'addressType': '',
                'addressRegion': 'QC',
                'streetAddress': 'W-558 Rue Saint-Vallier O',
                'addressCountry': 'CA'}],
            'entityType': 'PERSON',
            'identifier': 'LEAR570721',
            'legalName': 'BLIPPITY BOP',
            'bn': None,
            'bnSP': None,
            'identifier_q': None,
            'legalType': None,
            'operatingName': None,
            'roles': [{
                'roleType': 'Director',
                'relatedBN': '123456789',
                'roleDates': [{'active': True, 'end': None, 'start': '2023-03-20'}],
                'relatedName': request_json['business']['legalName'],
                'relatedState': 'ACTIVE',
                'related_q': f"{request_json['business']['legalName']} {request_json['business']['identifier']} 123456789",
                'relatedLegalType': request_json['business']['legalType'],
                'relatedEntityType': 'BUSINESS',
                'relatedIdentifier': request_json['business']['identifier'],}],
            'state': None}]


@integration_solr
def test_update_solr(session, client, jwt):
    """Assert that update operation is successful."""
    # setup -- start with no docs
    bor_solr.delete_all_docs()
    # update
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(REQUEST_TEMPLATE),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.OK
    business_identifier = REQUEST_TEMPLATE['business']['identifier']
    party_identifiers = []
    # check business update
    check_update_recorded(business_identifier)
    # check parties update
    for party in REQUEST_TEMPLATE['parties']:
        identifier = f"{party['source']}{party['officer']['id']}"
        party_identifiers.append(identifier)
        check_update_recorded(identifier, True)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    for identifier in [business_identifier] + party_identifiers:
        search_response = bor_solr.query(payload={'query': f'identifier:{identifier}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1


@integration_solr
def test_update_business_no_tax_id(session, client, jwt):
    """Assert that update operation is successful when the business has no tax id."""
    # setup -- start with no docs
    bor_solr.delete_all_docs()
    # setup - remove tax id from template
    no_tax_id = deepcopy(REQUEST_TEMPLATE)
    del no_tax_id['business']['taxId']
    business_identifier = 'FM1111111'
    no_tax_id['business']['identifier'] = business_identifier
    # update
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(no_tax_id),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

    # check
    assert api_response.status_code == HTTPStatus.OK
    # check business update
    check_update_recorded(business_identifier)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    search_response = bor_solr.query(payload={'query': f'identifier:{business_identifier}', 'fields': '*'})
    assert search_response['response']
    assert search_response['response']['docs']
    assert len(search_response['response']['docs']) == 1


@pytest.mark.parametrize('test_name,legal_type,identifier,expected', [
    ('test_bc_add_prfx', 'BC', '0123456', 'BC0123456'),
    ('test_cc_add_prfx', 'CC', '1234567', 'BC1234567'),
    ('test_ulc_add_prfx', 'ULC', '2345678', 'BC2345678'),
    ('test_ben_add_prfx', 'BEN', '0000001', 'BC0000001'),
    ('test_bc_prfx_given', 'BC', 'BC0123466', 'BC0123466'),
    ('test_cc_prfx_given', 'CC', 'BC1234577', 'BC1234577'),
    ('test_ulc_prfx_given', 'ULC', 'BC234588', 'BC234588'),
    ('test_ben_add_prfx', 'BEN', 'BC0000002', 'BC0000002'),
    ('test_wrong_type_no_prfx', 'S', '0000003', '0000003'),
    ('test_wrong_type_prfx_given', 'S', 'S3456790', 'S3456790')
])
def test_update_bc_class_adds_prefix(app, session, client, jwt, test_name, legal_type, identifier, expected):
    """Assert prefixes are added to BC, ULC and CC identifiers and only when no prefix is given."""
    solr_url = app.config.get('SOLR_SVC_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url)

        request_json = deepcopy(REQUEST_TEMPLATE)
        request_json['parties'] = []
        request_json['business']['legalType'] = legal_type
        request_json['business']['identifier'] = identifier

        api_response = client.put(f'/api/v1/internal/solr/update',
                                data=json.dumps(request_json),
                                headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                            'content-type': 'application/json'}))
        # check
        assert api_response.status_code == HTTPStatus.OK
        # check business update in model with altered identfier
        check_update_recorded(expected)
        # check call to solr mock
        assert m.called == True
        assert m.call_count == 1
        assert solr_url in m.request_history[0].url
        # check update payload set expected identifier
        m.request_history[0].json()[0]['identifier'] == expected


@pytest.mark.parametrize('test_name,path,replacement', [
    ('missing_business', ['business'], None),
    ('missing_business_identifier', ['business','identifier'], None),
    ('missing_business_name', ['business','legalName'], None),
    ('missing_business_type', ['business','legalType'], None),
    ('missing_business_state', ['business','state'], None),
    ('missing_business_addresses', ['businessAddresses'], None),
    ('missing_business_addresses_RO', ['businessAddresses', 'registeredOffice'], None),
    ('missing_business_addresses_RO_delivery', ['businessAddresses', 'registeredOffice', 'deliveryAddress'], None),
    ('missing_business_addresses_RO_delivery_city', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressCity'], None),
    ('missing_business_addresses_RO_delivery_country', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressCountry'], None),
    ('missing_business_addresses_RO_delivery_region', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressRegion'], None),
    ('missing_business_addresses_RO_delivery_pc', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'postalCode'], None),
    ('missing_business_addresses_RO_delivery_type', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressType'], None),
    ('missing_business_addresses_RO_delivery_street', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'streetAddress'], None),
    ('missing_parties_address', ['parties', 0, 'deliveryAddress'], None),
    ('missing_parties_source', ['parties', 0, 'source'], None),
    ('missing_parties_officer', ['parties', 0, 'officer'], None),
    ('missing_parties_officer_type', ['parties', 0, 'officer', 'partyType'], None),
    ('missing_parties_officer_id', ['parties', 0, 'officer', 'id'], None),
    ('missing_parties_roles', ['parties', 0, 'roles'], None),
    ('missing_parties_roles_type', ['parties', 0, 'roles', 0, 'roleType'], None),
    ('missing_parties_roles_app_date', ['parties', 0, 'roles', 0, 'appointmentDate'], None),
    ('invalid_parties_source', ['parties', 0, 'source'], 'invalid'),
    ('invalid_parties_officer_type', ['parties', 0, 'officer', 'partyType'], 'invalid'),
])
def test_update_solr_invalid_data(app, session, client, jwt, test_name, path, replacement):
    """Assert that error is returned if data missing."""
    solr_url = app.config.get('SOLR_SVC_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url)

        request_json = deepcopy(REQUEST_TEMPLATE)
        # remove field
        if len(path) == 1:
            if replacement:
                request_json[path[0]] = replacement
            else:
                del request_json[path[0]]
        elif len(path) == 2:
            if replacement:
                request_json[path[0]][path[1]] = replacement
            else:
                del request_json[path[0]][path[1]]
        elif len(path) == 3:
            if replacement:
                request_json[path[0]][path[1]][path[2]] = replacement
            else:
                del request_json[path[0]][path[1]][path[2]]
        elif len(path) == 4:
            if replacement:
                request_json[path[0]][path[1]][path[2]][path[3]] = replacement
            else:
                del request_json[path[0]][path[1]][path[2]][path[3]]
        else:
            if replacement:
                request_json[path[0]][path[1]][path[2]][path[3]][path[4]] = replacement
            else:
                del request_json[path[0]][path[1]][path[2]][path[3]][path[4]]

        api_response = client.put(f'/api/v1/internal/solr/update',
                                data=json.dumps(request_json),
                                headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                            'content-type': 'application/json'}))
        # check
        assert m.called == False
        assert api_response.status_code == HTTPStatus.BAD_REQUEST


def test_update_solr_unauthorized(client, jwt):
    """Assert that error is returned if unauthorized."""
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(REQUEST_TEMPLATE),
                              headers=create_header(jwt, [], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.UNAUTHORIZED
