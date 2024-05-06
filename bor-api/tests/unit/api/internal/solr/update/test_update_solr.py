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
"""Test-Suite to ensure that the solr doc update enpoint works as expected."""
import json
import time
from copy import deepcopy
from http import HTTPStatus

import pytest
import requests_mock

from bor_api.enums import SolrDocEventStatus
from bor_api.services import solr
from bor_api.services.authz import SYSTEM_ROLE

from tests.unit.test_utils import (SOLR_UPDATE_REQUEST_TEMPLATE as REQUEST_TEMPLATE,
                                   SOLR_UPDATE_REQUEST_OWNER_TEMPLATE as REQUEST_OWNER_TEMPLATE,
                                   TEST_PERSONS, create_header)
from tests import integration_solr

from . import check_update_recorded


# setup SP version of REQUEST_TEMPLATE
SP_REQUEST_TEMPLATE = deepcopy(REQUEST_TEMPLATE)
SP_REQUEST_TEMPLATE['business']['identifier'] = 'FM1233334'
SP_REQUEST_TEMPLATE['business']['legalType'] = 'SP'
SP_REQUEST_TEMPLATE['business']['legalName'] = 'ABCD Prop'

REQUEST_TEMPLATE_PARTY_NO_DELIVERY = deepcopy(SP_REQUEST_TEMPLATE)
del REQUEST_TEMPLATE_PARTY_NO_DELIVERY['parties'][0]['deliveryAddress']

@pytest.mark.parametrize('test_name,request_json,role_info', [
    ('ben', REQUEST_TEMPLATE, [{'id': '1-1', '_nest_parent_': '1'}]),
    ('sp', SP_REQUEST_TEMPLATE, []),
    ('party_no_delivery', REQUEST_TEMPLATE_PARTY_NO_DELIVERY, []),
    ('si', REQUEST_OWNER_TEMPLATE, [{'id': '1-1', '_nest_parent_': '1'}, {'id': '2-1', '_nest_parent_': '2'}])
])
def test_update_solr_mocked(app, session, client, jwt, test_name, request_json, role_info):
    """Assert that update operation sends correct payload to solr."""
    solr_url_update = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commit=true&overwrite=true&wt=json'
    solr_url_query = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/query'

    with requests_mock.mock() as m:
        m.post(solr_url_update)
        m.post(solr_url_query, json={'response': {'docs': role_info}})
        
        api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.ACCEPTED
        # check business update
        business_identifier = request_json['business']['identifier']
        check_update_recorded(business_identifier)
        # check parties update
        for party in request_json.get('parties', []):
            for role in party['roles']:
                identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}".upper()
                check_update_recorded(identifier, True)
        # check SI update
        for owner in request_json.get('owners', []):
            identifier = owner['interestedParty']['describedByPersonStatement']
            check_update_recorded(identifier, True)
            
        # check did not call to solr mock (only updates the DB)
        assert m.called == False
        # call sync to update solr
        api_response = client.get(f'/api/v1/internal/solr/update/sync', headers={'content-type': 'application/json'})
        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check events were completed
        business_identifier = request_json['business']['identifier']
        check_update_recorded(business_identifier,
                              is_party=False,
                              status=SolrDocEventStatus.COMPLETE)
        for party in request_json.get('parties', []):
            for role in party['roles']:
                identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}".upper()
                check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE)
        for owner in request_json.get('owners', []):
            identifier = owner['interestedParty']['describedByPersonStatement']
            check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE)
        # check call to solr was correct
        assert m.called == True
        # in order: 1 for existing business query + 1 for record update + 1 for existing business role update
        assert m.call_count == 2 if not role_info else 3

        # query for business roles
        assert solr_url_query in m.request_history[0].url
        assert m.request_history[0].json() == {
            'query': f'((relatedIdentifier_q:"{business_identifier[2:]}" AND relatedIdentifier_q:"{business_identifier[:2]}"))',
            'filter': [],
            'fields': ['id', '_nest_parent_'],
            'offset': 0,
            'limit': 1000
        }

        # verify record update (should've been the 2nd call to solr)
        assert solr_url_update in m.request_history[1].url
        entity_addresses = None
        if request_json.get('parties', [{}])[0].get('deliveryAddress'):
            entity_addresses = [{
                'address_q': '1234-4818 Westwinds Dr NE Calgary Alberta Canada T3J 3Z5',
                'locationDescription': None,
                'postalCode': 'T3J 3Z5',
                'addressCity': 'Calgary',
                'addressType': 'DELIVERY',
                'addressRegion': 'AB',
                'parentDoc': 'entity',
                'streetAddress': '1234-4818 Westwinds Dr NE',
                'streetAdditional': None,
                'addressCountry': 'Canada'}]
        elif request_json.get('owners'):
            entity_addresses = [{
                'address_q': '123-720 Commonwealth Rd test street additional Kelowna British Columbia Canada V4V 1R8 test description',
                'locationDescription': 'test description',
                'postalCode': 'V4V 1R8',
                'addressCity': 'Kelowna',
                'addressType': 'RESIDENCE',
                'addressRegion': 'BC',
                'parentDoc': 'entity',
                'streetAddress': '123-720 Commonwealth Rd',
                'streetAdditional': 'test street additional',
                'addressCountry': 'Canada'}]
        expectedRelatedAddresses = None
        if bus_addresses := request_json['business'].get('addresses'):
            expectedRelatedAddresses = []
            for address_json in bus_addresses:
                expectedRelatedAddresses.append({
                    'address_q': None,
                    'locationDescription': address_json['deliveryInstructions'],
                    'postalCode': address_json['postalCode'],
                    'addressCity': address_json['addressCity'],
                    'addressType': address_json['addressType'].upper(),
                    'addressRegion': address_json['addressRegion'],
                    'parentDoc': 'entityRole',
                    'streetAddress': address_json['streetAddress'],
                    'streetAdditional': address_json['streetAddressAdditional'],
                    'addressCountry': 'Canada'
                })

        if request_json.get('parties'):
            assert m.request_history[1].json() == [
                {
                    'entityAddresses': {'set': entity_addresses} if entity_addresses else None,
                    'entityType': 'PERSON',
                    'externalInfluence': None,
                    'id': f'LEAR570343{business_identifier}DIRECTOR',
                    'legalName': 'BCREG2 LIANG FORTY',
                    'alternateName': None,
                    'name_q': 'BCREG2 LIANG FORTY',
                    'info_q': entity_addresses[0]['address_q'] if entity_addresses else None,
                    'birthDate': None,
                    'bn': None,
                    'deathDate': None,
                    'email': None,
                    'identifier': None,
                    'isPermanentResident': None,
                    'legalType': None,
                    'nationalities': None,
                    'roles': {'set': [{
                        'id': f'LEAR570343{business_identifier}DIRECTOR/roles0',
                        'relatedAddresses': expectedRelatedAddresses,
                        'roleType': 'DIRECTOR',
                        'relatedBN': '123456789',
                        'relatedEmail': 'test@email.com',
                        'roleDates': [{'active': True, 'end': None, 'start': '2023-03-06'}],
                        'relatedName': request_json['business']['legalName'],
                        'relatedState': 'ACTIVE',
                        'related_q': f"{request_json['business']['legalName']} {request_json['business']['identifier']} 123456789",
                        'relatedLegalType': request_json['business']['legalType'],
                        'relatedEntityType': 'BUSINESS',
                        'relatedInterests': None,
                        'relatedIdentifier': request_json['business']['identifier'],}]},
                    'state': None,
                    'taxNumber': None,
                    'taxResidencies': None
                },
                {
                    'entityAddresses': {'set': [{
                        'address_q': 'W-558 Rue Saint-Vallier O Québec Quebec Canada G1N 1C1',
                        'locationDescription': None,
                        'postalCode': 'G1N 1C1',
                        'addressCity': 'Québec',
                        'addressType': 'DELIVERY',
                        'addressRegion': 'QC',
                        'parentDoc': 'entity',
                        'streetAddress': 'W-558 Rue Saint-Vallier O',
                        'streetAdditional': None,
                        'addressCountry': 'Canada'}]},
                    'entityType': 'PERSON',
                    'externalInfluence': None,
                    'id': f'LEAR570721{business_identifier}DIRECTOR',
                    'legalName': 'BLIPPITY BOP',
                    'alternateName': None,
                    'name_q': 'BLIPPITY BOP',
                    'info_q': 'W-558 Rue Saint-Vallier O Québec Quebec Canada G1N 1C1',
                    'bn': None,
                    'birthDate': None,
                    'deathDate': None,
                    'isPermanentResident': None,
                    'nationalities': None,
                    'email': None,
                    'identifier': None,
                    'legalType': None,
                    'roles': {'set': [{
                        'id': f'LEAR570721{business_identifier}DIRECTOR/roles0',
                        'relatedAddresses': expectedRelatedAddresses,
                        'roleType': 'DIRECTOR',
                        'relatedBN': '123456789',
                        'relatedEmail': 'test@email.com',
                        'roleDates': [{'active': True, 'end': None, 'start': '2023-03-20'}],
                        'relatedName': request_json['business']['legalName'],
                        'relatedState': 'ACTIVE',
                        'related_q': f"{request_json['business']['legalName']} {request_json['business']['identifier']} 123456789",
                        'relatedLegalType': request_json['business']['legalType'],
                        'relatedEntityType': 'BUSINESS',
                        'relatedInterests': None,
                        'relatedIdentifier': request_json['business']['identifier'],}]},
                    'state': None,
                    'taxNumber': None,
                    'taxResidencies': None
                }
            ]
        else:
            assert m.request_history[1].json() == [
                {
                    'entityAddresses': {'set': entity_addresses},
                    'entityType': 'PERSON',
                    'externalInfluence': 'CanBeInfluenced',
                    'id': '7f0511ba-9621-4134-8363-462c61b9162a',
                    'legalName': 'Kial Jinnah',
                    'alternateName': 'wallaby willow',
                    'name_q': 'Kial Jinnah wallaby willow',
                    'info_q': f"402931299 test@test.com {entity_addresses[0]['address_q']}",
                    'birthDate': '1997-02-05',
                    'bn': None,
                    'deathDate': None,
                    'email': 'test@test.com',
                    'identifier': None,
                    'isPermanentResident': False,
                    'legalType': None,
                    'nationalities': {'set': ['CA']},
                    'roles': {'set': [{
                        'id': '7f0511ba-9621-4134-8363-462c61b9162aBC1233335SIGNIFICANT_INDIVIDUAL',
                        'relatedAddresses': [{
                            'address_q': None,
                            'parentDoc': 'entityRole',
                            'postalCode': 'W2R 1C1',
                            'addressCity': 'Ladysmith',
                            'addressType': 'DELIVERY',
                            'addressRegion': 'BC',
                            'streetAddress': '123456 Lalalane',
                            'addressCountry': 'Canada',
                            'streetAdditional': 'additional info',
                            'locationDescription': 'bla bla'}],
                        'roleType': 'SIGNIFICANT INDIVIDUAL',
                        'relatedBN': '123456788BC001',
                        'relatedEmail': 'test@email.com',
                        'roleDates': [{'active': True, 'end': None, 'start': '2024-02-07'}],
                        'relatedName': request_json['business']['legalName'],
                        'relatedState': 'ACTIVE',
                        'related_q': f"{request_json['business']['legalName']} {request_json['business']['identifier']} 123456788BC001",
                        'relatedLegalType': request_json['business']['legalType'],
                        'relatedEntityType': 'BUSINESS',
                        'relatedInterests': [
                            {'details': 'controlType.sharesOrVotes.registeredOwner',
                            'directOrIndirect': 'direct',
                            'interestType': 'votingRights',
                            'otherReason': None,
                            'sharesExact': None,
                            'sharesMax': 45,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.registeredOwner',
                            'directOrIndirect': 'direct',
                            'interestType': 'shareholding',
                            'otherReason': None,
                            'sharesExact': None,
                            'sharesMax': 33,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.indirectControl',
                            'directOrIndirect': 'indirect',
                            'interestType': 'votingRights',
                            'otherReason': None,
                            'sharesExact': None,
                            'sharesMax': 45,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.indirectControl',
                            'directOrIndirect': 'indirect',
                            'interestType': 'shareholding',
                            'otherReason': None,
                            'sharesExact': None,
                            'sharesMax': 33,
                            'sharesMin': None},
                            {'details': 'other',
                            'directOrIndirect': None,
                            'otherReason': 'bla bla',
                            'interestType': 'otherInfluenceOrControl',
                            'sharesExact': None,
                            'sharesMax': None,
                            'sharesMin': None}],
                        'relatedIdentifier': request_json['business']['identifier'],}]},
                    'state': None,
                    'taxNumber': '402 931 299',
                    'taxResidencies': {'set': ['CA']}
                }
            ]

        # update per existing business role_info 
        if role_info:
            # for index, role_info in enumerate(role_info):
            assert solr_url_update in m.request_history[2].url
            for index, role_ids in enumerate(role_info):
                assert m.request_history[2].json()[index] == {
                    '_root_': role_ids['_nest_parent_'],
                    'id': role_ids['id'],
                    'relatedAddresses': {'set': expectedRelatedAddresses},
                    'relatedBN': {'set': request_json['business']['taxId']},
                    'relatedEmail': {'set': request_json['business']['email']},
                    'relatedLegalType': {'set': request_json['business']['legalType']},
                    'relatedName': {'set': request_json['business']['legalName']},
                    'relatedState': {'set': request_json['business']['state']},
                    'related_q': {'set': f"{request_json['business']['legalName']} {business_identifier} {request_json['business']['taxId']}"},
                }


@integration_solr
@pytest.mark.parametrize('test_name,request_json,existing_entities', [
    ('ben', REQUEST_TEMPLATE, []),
    ('si', REQUEST_OWNER_TEMPLATE, []),
    ('partial', deepcopy(REQUEST_TEMPLATE), TEST_PERSONS[-4:])
])
def test_update_solr(session, client, jwt, test_name, request_json, existing_entities):
    """Assert that update operation is successful."""
    # setup -- start with no docs
    solr.delete_all_docs()
    time.sleep(2)  # wait for solr to register update
    # setup -- add existing docs
    if existing_entities:
        # set the request_json identifier to match one of the existing entities (ensures a partial update will occur)
        request_json['business']['identifier'] = existing_entities[0].roles[0].relatedIdentifier
        # check integrity of the test (if fails then alter the test data)
        assert request_json['business']['legalName'] != existing_entities[0].roles[0].relatedName
        # add existing docs
        solr.create_or_replace_docs(existing_entities)
    time.sleep(1)  # wait for solr to register update
    # update
    api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))
    # check
    assert api_response.status_code == HTTPStatus.ACCEPTED
    business_identifier = request_json['business']['identifier']
    party_ids = []
    si_ids = []
    # check business update
    check_update_recorded(business_identifier)
    # check parties update
    for party in request_json.get('parties', []):
        for role in party['roles']:
            party_id = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}".upper()
            party_ids.append(party_id)
            check_update_recorded(party_id, True)
    # check si update
    for owner in request_json.get('owners', []):
        si_id = owner['interestedParty']['describedByPersonStatement']
        si_ids.append(si_id)
        check_update_recorded(si_id, True)
    # verify update has NOT synced to solr yet
    for entity_id in party_ids:
        search_response = solr.query(payload={'query': f'id:{entity_id}', 'fields': '*'})
        assert search_response['response']
        assert len(search_response['response']['docs']) == 0
    # call sync to update solr
    api_response = client.get(f'/api/v1/internal/solr/update/sync', headers={'content-type': 'application/json'})
    # check success
    assert api_response.status_code == HTTPStatus.OK
    # check events were completed
    check_update_recorded(business_identifier,
                          is_party=False,
                          status=SolrDocEventStatus.COMPLETE)
    for party in request_json.get('parties', []):
        for role in party['roles']:
            identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}".upper()
            check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE)
    for owner in request_json.get('owners', []):
        si_id = owner['interestedParty']['describedByPersonStatement']
        check_update_recorded(si_id, True, status=SolrDocEventStatus.COMPLETE)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    # verify search returns updated records
    for entity_id in party_ids + si_ids:
        search_response = solr.query(payload={'query': f'id:{entity_id}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1
    # verify existing entities with the same business were updated
    for entity in existing_entities:
        for role in entity.roles:
            if role.relatedIdentifier == business_identifier:
                resp = solr.query(payload={'query': f'id:{role.id}', 'fields': '*'})
                assert len(resp['response']['docs']) == 1
                doc = resp['response']['docs'][0]
                assert doc['relatedIdentifier'] == business_identifier
                assert doc['relatedName'] == request_json['business']['legalName']
                assert doc['relatedState'] == request_json['business']['state']
                assert doc['relatedLegalType'] == request_json['business']['legalType']
                assert doc['relatedEmail'] == request_json['business']['email']
                assert doc['relatedBN'] == request_json['business']['taxId']

@pytest.mark.skip  # NOTE: unskip once serving businesses in search
@integration_solr
def test_update_business_no_tax_id(session, client, jwt):
    """Assert that update operation is successful when the business has no tax id."""
    # setup -- start with no docs
    solr.delete_all_docs()
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
    assert api_response.status_code == HTTPStatus.ACCEPTED
    # check business update
    check_update_recorded(business_identifier)
    # call sync to update solr
    api_response = client.get(f'/api/v1/internal/solr/update/sync', headers={'content-type': 'application/json'})
    # check success
    assert api_response.status_code == HTTPStatus.OK
    # check events were completed
    check_update_recorded(business_identifier,
                          is_party=False,
                          status=SolrDocEventStatus.COMPLETE)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    search_response = solr.query(payload={'query': f'identifier:{business_identifier}', 'fields': '*'})
    assert search_response['response']
    assert search_response['response']['docs']
    assert len(search_response['response']['docs']) == 1


@pytest.mark.skip  # NOTE: skip until serving business updates
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
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commit=true&overwrite=true&wt=json'

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
        assert api_response.status_code == HTTPStatus.ACCEPTED
        # check business update in model with altered identfier
        check_update_recorded(expected)


@pytest.mark.parametrize('test_name,path,replacement', [
    ('missing_business', ['business'], None),
    ('missing_business_identifier', ['business','identifier'], None),
    ('missing_business_name', ['business','legalName'], None),
    ('missing_business_type', ['business','legalType'], None),
    ('missing_business_state', ['business','state'], None),
    # Uncomment once using business address info and address info becomes required
    # ('missing_business_addresses', ['businessAddresses'], None),
    # ('missing_business_addresses_RO', ['businessAddresses', 'registeredOffice'], None),
    # ('missing_business_addresses_RO_delivery', ['businessAddresses', 'registeredOffice', 'deliveryAddress'], None),
    # ('missing_business_addresses_RO_delivery_city', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressCity'], None),
    # ('missing_business_addresses_RO_delivery_country', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressCountry'], None),
    # ('missing_business_addresses_RO_delivery_region', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressRegion'], None),
    # ('missing_business_addresses_RO_delivery_pc', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'postalCode'], None),
    # ('missing_business_addresses_RO_delivery_type', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'addressType'], None),
    # ('missing_business_addresses_RO_delivery_street', ['businessAddresses', 'registeredOffice', 'deliveryAddress', 'streetAddress'], None),
    ('missing_parties_source', ['parties', 0, 'source'], None),
    ('missing_parties_officer', ['parties', 0, 'officer'], None),
    ('missing_parties_officer_type', ['parties', 0, 'officer', 'partyType'], None),
    ('missing_parties_officer_id', ['parties', 0, 'officer', 'id'], None),
    ('missing_parties_roles', ['parties', 0, 'roles'], None),
    ('missing_parties_roles_type', ['parties', 0, 'roles', 0, 'roleType'], None),
    ('invalid_parties_source', ['parties', 0, 'source'], 'invalid'),
    ('invalid_parties_officer_type', ['parties', 0, 'officer', 'partyType'], 'invalid'),
])
def test_update_solr_invalid_data(app, session, client, jwt, test_name, path, replacement):
    """Assert that error is returned if data missing."""
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commit=true&overwrite=true&wt=json'

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
