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
# from search_api.utils.util import get_str


def validate_solr_update_payload(request_json: dict):  # pylint: disable=too-many-branches
    """Validate solr business update request."""
    err = []
    # uncomment / alter when payload is finalized
    # if not request_json.get('business'):
    #     err.append({'error': 'Business Object is required.', 'path': '/business'})
    #     return err

    # identifier_path = '/business/identifier'
    # if get_str(request_json, identifier_path) is None:
    #     err.append({'error': 'Identifier is required.', 'path': identifier_path})

    # business_name_path = '/business/legalName'
    # if get_str(request_json, business_name_path) is None:
    #     err.append({'error': 'Business Name is required.', 'path': business_name_path})

    # business_type_path = '/business/legalType'
    # if get_str(request_json, business_type_path) is None:
    #     err.append({'error': 'Business Type is required.', 'path': business_type_path})

    # business_status_path = '/business/state'
    # business_status = get_str(request_json, business_status_path)
    # if business_status is None or business_status not in ['ACTIVE', 'HISTORICAL']:
    #     err.append({'error': 'A valid business state is required.', 'path': business_status_path})

    # for index, party in enumerate(request_json.get('parties', [])):

    #     if not party.get('roles'):
    #         err.append({'error': 'Party Roles is required.', 'path': f'/parties/{index}/roles'})
    #     for role_index, role in enumerate(party.get('roles', [])):
    #         if not role.get('roleType'):
    #             err.append(
    #                 {'error': 'Role Type is required.', 'path': f'/parties/{index}/roles/{role_index}/roleType'})
    #         elif role.get('roleType').lower() not in ['partner', 'proprietor']:
    #             err.append(
    #                 {'error': 'Only Partner or Proprietor roles are accepted.',
    #                     'path': f'/parties/{index}/roles/{role_index}/roleType'})

    #     officer_path = f'/parties/{index}/officer'
    #     officer = party.get('officer', {})

    #     party_type = officer.get('partyType')
    #     if not party_type:
    #         err.append({'error': 'Party Type is required.', 'path': f'{officer_path}/partyType'})

    #     if party_type:
    #         if party_type == 'organization':
    #             if not officer.get('organizationName'):
    #                 err.append({'error': 'Organization name is required.',
    #                             'path': f'{officer_path}/organizationName'})
    #         elif party_type == 'person':
    #             if not (officer.get('firstName') or officer.get('middleInitial') or officer.get('lastName')):
    #                 err.append({'error': 'First name or middle name or last name is required.',
    #                             'path': f'{officer_path}'})
    #         else:
    #             err.append({'error': 'Invalid party type.',
    #                         'path': f'{officer_path}/partyType'})
    return err
