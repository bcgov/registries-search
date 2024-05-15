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
"""The class manages methods to validate a request."""
from flask import current_app, request

from bor_api.enums import SearchAccessLevel
from bor_api.exceptions import AuthorizationException
from bor_api.models import User
from bor_api.services import jwt, flags
from bor_api.services.authz import account_products
from bor_api.services.bor_solr.utils import get_search_field_group

from .util import get_str


def _validate_search_request() -> tuple[dict, list[dict]]:
    """Validate the search request headers / payload."""
    errors = []
    request_json = request.get_json()
    query_json = request_json.get('query', {})
    value = query_json.get('value', None)
    # TODO: validate the rest of the payload
    if not value or not isinstance(value, str):
        errors.append({'Invalid payload': "Expected a string for 'value'."})

    try:
        int(request_json.get('start', 0))
        int(request_json.get('rows', 0))
    except ValueError:  # catch invalid start/row entry
        errors.append({'Invalid payload': "Expected integer for params: 'start', 'rows'"})

    accepted_types = ['application/json', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    if (content_type := str(request.accept_mimetypes)) and not [x for x in accepted_types if x in content_type]:
        msg = f'Invalid Accept header. Expected {" or ".join(accepted_types)} but received {content_type}'
        errors.append({'Invalid header': msg})

    return request_json, errors


def _validate_search_access_level(user: User, access_level: SearchAccessLevel) -> tuple[bool, list[dict]]:
    """Validate the search access level for the user."""
    if access_level == SearchAccessLevel.PUBLIC:
        # never any access errors for public level access
        return False, []

    errors = []

    account_id = request.headers.get('Account-Id', None)
    if not request.headers.get('Account-Id', None):
        errors.append({'Missing header': 'Account-Id'})

    # check access
    current_app.logger.debug('Checking user access...')
    access_flag_name = None
    access_code = None
    if access_level == SearchAccessLevel.EXTENDED:
        access_flag_name = 'enable-comp-auth-search'
        access_code = 'CA_SEARCH'
    elif access_level == SearchAccessLevel.LIMITED:
        access_flag_name = 'enable-director-search'
        access_code = 'NDS'
    else:
        current_app.logger.error('Unhandled access level: %s', access_level)
        errors.append({'Error evaluating search access.'})

    has_direct_access = jwt.contains_role(['system']) or flags.value(access_flag_name, {'key': user.sub})
    if not has_direct_access:
        # Direct access not enabled for user so check if account has the product subscription.
        current_app.logger.debug('Direct access denied, checking account access...')
        products = account_products(token=jwt.get_token_auth_header(), account_id=account_id)
        if not isinstance(products, list):
            current_app.logger.debug(products)
            raise AuthorizationException(f'Error collecting information from Auth service. {products}')
        if not any(p['code'] == access_code and p['subscriptionStatus'] == 'ACTIVE' for p in products):
            raise AuthorizationException('This account is not authorized for this level of search.')
    current_app.logger.debug('Access granted.')

    return has_direct_access, errors


def validate_search(user: User, access_level: SearchAccessLevel) -> tuple[dict, list[str], bool, list[dict]]:
    """Validate the search request and user access."""
    request_json, request_errors = _validate_search_request()
    has_direct_access, access_errors = _validate_search_access_level(user, access_level)

    return request_json, get_search_field_group(access_level), has_direct_access, request_errors + access_errors


def validate_solr_update_request(request_json: dict):  # pylint: disable=too-many-branches,too-many-statements
    """Validate solr doc update request."""
    err = []
    # validate business info
    if not request_json.get('business'):
        err.append({'error': 'Business Object is required.', 'path': '/business'})
        return err

    identifier_path = '/business/identifier'
    if get_str(request_json, identifier_path) is None:
        err.append({'error': 'Identifier is required.', 'path': identifier_path})

    business_name_path = '/business/legalName'
    if get_str(request_json, business_name_path) is None:
        err.append({'error': 'Business Name is required.', 'path': business_name_path})

    business_type_path = '/business/legalType'
    if get_str(request_json, business_type_path) is None:
        err.append({'error': 'Business Type is required.', 'path': business_type_path})

    business_status_path = '/business/state'
    business_status = get_str(request_json, business_status_path)
    if business_status is None or business_status not in ['ACTIVE', 'HISTORICAL']:
        err.append({'error': 'A valid business state is required.', 'path': business_status_path})

    # validate address info
    # NOTE: uncomment below once business addresses are used
    # if not request_json.get('businessAddresses'):
    #     err.append({'error': 'Business Addresses are required.', 'path': '/businessAddresses'})
    #     return err
    # office_type = 'businessOffice' \
    #     if request_json['business'].get('legalType', '') in ['SP', 'GP'] \
    #     else 'registeredOffice'
    # if not request_json['businessAddresses'].get(office_type, {}).get('deliveryAddress'):
    #     err.append({'error': 'Business Delivery Address is required.',
    #                 'path': f'/businessAddresses/{office_type}/deliveryAddress'})
    #     return err
    # required_address_fields = ['addressType', 'addressCity', 'addressCountry', 'addressRegion',
    #                            'postalCode', 'streetAddress']
    # for field in required_address_fields:
    #     path = f'/businessAddresses/{office_type}/deliveryAddress/{field}'
    #     if not get_str(request_json, path):
    #         err.append({'error': f'{field} field is required.', 'path': path})

    # validate parties info
    for index, party in enumerate(request_json.get('parties', [])):
        if not party.get('source'):
            err.append({'error': 'Party Source is required.', 'path': f'/parties/{index}/source'})
        elif party['source'] not in ['LEAR', 'COLIN', 'BTR']:
            err.append({'error': 'A valid Party Source is required.', 'path': f'/parties/{index}/source'})

        if not party.get('roles'):
            err.append({'error': 'Party Roles is required.', 'path': f'/parties/{index}/roles'})
            return err
        for role_index, role in enumerate(party['roles']):
            if not role.get('roleType'):
                err.append(
                    {'error': 'Role Type is required.', 'path': f'/parties/{index}/roles/{role_index}/roleType'})

        officer_path = f'/parties/{index}/officer'
        officer = party.get('officer', {})

        if not officer.get('id'):
            err.append({'error': 'Party ID is required.', 'path': f'{officer_path}/id'})

        party_type = officer.get('partyType')
        if not party_type:
            err.append({'error': 'Party Type is required.', 'path': f'{officer_path}/partyType'})
            return err

        if party_type == 'organization':
            if not officer.get('organizationName'):
                err.append({'error': 'Organization name is required.',
                            'path': f'{officer_path}/organizationName'})
        elif party_type == 'person':
            if not (officer.get('firstName') or officer.get('middleInitial') or officer.get('lastName')):
                err.append({'error': 'First name or middle name or last name is required.',
                            'path': f'{officer_path}'})
        else:
            err.append({'error': 'Invalid party type.',
                        'path': f'{officer_path}/partyType'})
    return err
