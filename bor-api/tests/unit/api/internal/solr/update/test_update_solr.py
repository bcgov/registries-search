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
from bor_api.services import solr, solr_temp
from bor_api.services.authz import SYSTEM_ROLE

from tests.unit.test_utils import (SOLR_UPDATE_REQUEST_TEMPLATE as REQUEST_TEMPLATE,
                                   SOLR_UPDATE_REQUEST_OWNER_TEMPLATE as REQUEST_OWNER_TEMPLATE,
                                   create_header)
from tests import integration_solr

from . import check_update_recorded


# setup SP version of REQUEST_TEMPLATE
SP_REQUEST_TEMPLATE = deepcopy(REQUEST_TEMPLATE)
SP_REQUEST_TEMPLATE['business']['identifier'] = 'FM1233334'
SP_REQUEST_TEMPLATE['business']['legalType'] = 'SP'
SP_REQUEST_TEMPLATE['business']['legalName'] = 'ABCD Prop'
SP_REQUEST_TEMPLATE['businessAddresses']['businessOffice'] = SP_REQUEST_TEMPLATE['businessAddresses']['registeredOffice']
del SP_REQUEST_TEMPLATE['businessAddresses']['registeredOffice']
del SP_REQUEST_TEMPLATE['businessAddresses']['recordsOffice']

REQUEST_TEMPLATE_PARTY_NO_DELIVERY = deepcopy(SP_REQUEST_TEMPLATE)
del REQUEST_TEMPLATE_PARTY_NO_DELIVERY['parties'][0]['deliveryAddress']

@pytest.mark.parametrize('test_name,request_json', [
    ('ben', REQUEST_TEMPLATE),
    ('sp', SP_REQUEST_TEMPLATE),
    ('party_no_delivery', REQUEST_TEMPLATE_PARTY_NO_DELIVERY),
    ('si', REQUEST_OWNER_TEMPLATE)
])
def test_update_solr_mocked(app, session, client, jwt, test_name, request_json):
    """Assert that update operation sends correct payload to solr."""
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'
    temp_solr_url = app.config.get('TEMP_SOLR_SVC_URL') + '/bo/update?commitWithin=1000&overwrite=true&wt=json'

    with requests_mock.mock() as m:
        m.post(solr_url)
        m.post(temp_solr_url)
        
        api_response = client.put(f'/api/v1/internal/solr/update',
                              data=json.dumps(request_json),
                              headers=create_header(jwt, [SYSTEM_ROLE], **{'Accept-Version': 'v1',
                                                                           'content-type': 'application/json'}))

        # check success
        assert api_response.status_code == HTTPStatus.ACCEPTED
        # check business update
        business_identifier = request_json['business']['identifier']
        # check_update_recorded(business_identifier)
        # check parties update
        for party in request_json.get('parties', []):
            for count, role in enumerate(party['roles']):
                identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}{count}".upper()
                check_update_recorded(identifier, True)
        # check SI update
        for owner in request_json.get('owners', []):
            identifier = owner['interestedParty']['describedByPersonStatement']
            check_update_recorded(identifier, True, is_owner=True)
            
        # check did not call to solr mock (only updates the DB)
        assert m.called == False
        # call sync to update solr
        api_response = client.get(f'/api/v1/internal/solr/update/sync', headers={'content-type': 'application/json'})
        # check success
        assert api_response.status_code == HTTPStatus.OK
        # check events were completed
        business_identifier = request_json['business']['identifier']
        # check_update_recorded(business_identifier,
        #                       is_party=False,
        #                       status=SolrDocEventStatus.COMPLETE)
        for party in request_json.get('parties', []):
            for count, role in enumerate(party['roles']):
                identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}{count}".upper()
                check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE)
        for owner in request_json.get('owners', []):
            identifier = owner['interestedParty']['describedByPersonStatement']
            check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE, is_owner=True)
        # check call to solr was correct
        assert m.called == True
        if request_json.get('parties'):
            assert m.call_count == 2
            assert solr_url in m.request_history[0].url
            assert temp_solr_url in m.request_history[1].url
        else:
            assert m.call_count == 1
            assert temp_solr_url in m.request_history[0].url

        entity_addresses = None
        if request_json.get('parties', [{}])[0].get('deliveryAddress'):
            entity_addresses = [{
                'address_q': '1234-4818 Westwinds Dr NE Calgary Alberta Canada T3J 3Z5',
                'locationDescription': None,
                'postalCode': 'T3J 3Z5',
                'addressCity': 'Calgary',
                'addressType': 'DELIVERY',
                'addressRegion': 'AB',
                'streetAddress': '1234-4818 Westwinds Dr NE',
                'streetAdditional': None,
                'addressCountry': 'Canada'}]
        elif request_json.get('owners'):
            entity_addresses = [{
                'address_q': '123-720 Commonwealth Rd test street additional Kelowna BC V4V 1R8 test description',
                'locationDescription': 'test description',
                'postalCode': 'V4V 1R8',
                'addressCity': 'Kelowna',
                'addressType': 'RESIDENCE',
                'addressRegion': 'BC',
                'streetAddress': '123-720 Commonwealth Rd',
                'streetAdditional': 'test street additional',
                'addressCountry': ''}]

        if request_json.get('parties'):
            assert m.request_history[0].json() == [
                # NOTE: uncomment once serving business updates
                # {
                #     'entityAddresses': [{
                #         'address_q': 'Bc-435 North Rd Coquitlam British Columbia Canada V3K 3V9',
                #         'postalCode': 'V3K 3V9',
                #         'addressCity': 'Coquitlam',
                #         'addressType': 'delivery',
                #         'addressRegion': 'BC',
                #         'streetAddress': 'Bc-435 North Rd',
                #         'addressCountry': 'Canada'}],
                #     'entityType': 'BUSINESS',
                #     'id': request_json['business']['identifier'],
                #     'identifier': request_json['business']['identifier'],
                #     'legalName': request_json['business']['legalName'],
                #     'bn': '123456789',
                #     'email': 'test@email.com',
                #     'legalType': request_json['business']['legalType'],
                #     'roles': None,
                #     'state': 'ACTIVE'
                # },
                {
                    'entityAddresses': entity_addresses,
                    'entityType': 'PERSON',
                    'externalInfluence': None,
                    'id': f'LEAR570343{business_identifier}DIRECTOR0',
                    'legalName': 'BCREG2 LIANG FORTY',
                    'alternateName': None,
                    'birthDate': None,
                    'bn': None,
                    'deathDate': None,
                    'email': None,
                    'identifier': None,
                    'isPermanentResident': None,
                    'legalType': None,
                    'nationalities': None,
                    'roles': [{
                        'id': f'LEAR570343{business_identifier}DIRECTOR0/roles0',
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
                        'relatedIdentifier': request_json['business']['identifier'],}],
                    'state': None,
                    'taxNumber': None,
                    'taxResidencies': None
                },
                {
                    'entityAddresses': [{
                        'address_q': 'W-558 Rue Saint-Vallier O Québec Quebec Canada G1N 1C1',
                        'locationDescription': None,
                        'postalCode': 'G1N 1C1',
                        'addressCity': 'Québec',
                        'addressType': 'DELIVERY',
                        'addressRegion': 'QC',
                        'streetAddress': 'W-558 Rue Saint-Vallier O',
                        'streetAdditional': None,
                        'addressCountry': 'Canada'}],
                    'entityType': 'PERSON',
                    'externalInfluence': None,
                    'id': f'LEAR570721{business_identifier}DIRECTOR0',
                    'legalName': 'BLIPPITY BOP',
                    'alternateName': None,
                    'bn': None,
                    'birthDate': None,
                    'deathDate': None,
                    'isPermanentResident': None,
                    'nationalities': None,
                    'email': None,
                    'identifier': None,
                    'legalType': None,
                    'roles': [{
                        'id': f'LEAR570721{business_identifier}DIRECTOR0/roles0',
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
                        'relatedIdentifier': request_json['business']['identifier'],}],
                    'state': None,
                    'taxNumber': None,
                    'taxResidencies': None
                }
            ]
        else:
            assert m.request_history[0].json() == [
                {
                    'entityAddresses': {'set': entity_addresses},
                    'entityType': 'PERSON',
                    'externalInfluence': 'CanBeInfluenced',
                    'id': '7f0511ba-9621-4134-8363-462c61b9162a',
                    'legalName': 'Kial Jinnah',
                    'alternateName': 'wallaby willow',
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
                            'sharesExact': None,
                            'sharesMax': 45,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.registeredOwner',
                            'directOrIndirect': 'direct',
                            'interestType': 'shareholding',
                            'sharesExact': None,
                            'sharesMax': 33,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.indirectControl',
                            'directOrIndirect': 'indirect',
                            'interestType': 'votingRights',
                            'sharesExact': None,
                            'sharesMax': 45,
                            'sharesMin': None},
                            {'details': 'controlType.sharesOrVotes.indirectControl',
                            'directOrIndirect': 'indirect',
                            'interestType': 'shareholding',
                            'sharesExact': None,
                            'sharesMax': 33,
                            'sharesMin': None},
                            {'details': 'bla bla',
                            'directOrIndirect': None,
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


@integration_solr
@pytest.mark.parametrize('test_name,request_json', [
    ('ben', REQUEST_TEMPLATE),
    ('si', REQUEST_OWNER_TEMPLATE)
])
def test_update_solr(session, client, jwt, test_name, request_json):
    """Assert that update operation is successful."""
    # setup -- start with no docs
    solr.delete_all_docs()
    time.sleep(2)  # wait for solr to register update
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
    # check business update - NOTE: uncomment once serving business updates
    # check_update_recorded(business_identifier)
    # check parties update
    for party in request_json.get('parties', []):
        for role in party['roles']:
            party_id = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}0".upper()
            party_ids.append(party_id)
            check_update_recorded(party_id, True)
    # check si update
    for owner in request_json.get('owners', []):
        si_id = owner['interestedParty']['describedByPersonStatement']
        si_ids.append(si_id)
        check_update_recorded(si_id, True, is_owner=True)
    # verify update has NOT synced to solr yet
    for entity_id in [business_identifier] + party_ids:
        search_response = solr.query(payload={'query': f'id:{entity_id}', 'fields': '*'})
        assert search_response['response']
        assert len(search_response['response']['docs']) == 0
    # call sync to update solr
    api_response = client.get(f'/api/v1/internal/solr/update/sync', headers={'content-type': 'application/json'})
    # check success
    assert api_response.status_code == HTTPStatus.OK
    # check events were completed - NOTE: uncomment once serving business updates
    # check_update_recorded(business_identifier,
    #                       is_party=False,
    #                       status=SolrDocEventStatus.COMPLETE)
    for party in request_json.get('parties', []):
        for role in party['roles']:
            identifier = f"{party['source']}{party['officer']['id']}{business_identifier}{role['roleType'].replace(' ', '_')}0".upper()
            check_update_recorded(identifier, True, status=SolrDocEventStatus.COMPLETE)
    for owner in request_json.get('owners', []):
        si_id = owner['interestedParty']['describedByPersonStatement']
        check_update_recorded(si_id, True, status=SolrDocEventStatus.COMPLETE, is_owner=True)
    # check solr for updated records
    time.sleep(2)  # wait for solr to register update
    for entity_id in party_ids:
        search_response = solr.query(payload={'query': f'id:{entity_id}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1
    for entity_id in party_ids + si_ids:
        search_response = solr_temp.query(payload={'query': f'id:{entity_id}', 'fields': '*'})
        assert search_response['response']
        assert search_response['response']['docs']
        assert len(search_response['response']['docs']) == 1


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
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'

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
    solr_url = app.config.get('SOLR_SVC_LEADER_URL') + '/bor/update?commitWithin=1000&overwrite=true&wt=json'

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
