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
"""Data parsing functions."""
from datetime import datetime, timezone

from datedelta import datedelta
from flask import current_app
from search_api.services.business_solr.doc_fields import PartyField

from search_solr_importer.enums import ColinPartyTypeCode


def _is_good_standing(item_dict: dict, source: str) -> bool:  # pylint: disable=too-many-return-statements;
    """Return the good standing value of the business."""
    if item_dict['state'] != 'ACTIVE':
        # Good standing is irrelevant to non-active businesses
        return None
    if source == 'LEAR':
        if item_dict['legal_type'] in ['SP', 'GP']:
            # Good standing is irrelevant to FIRMS
            return None
        if item_dict.get('restoration_expiry_date'):
            # A business in limited restoration is not in good standing according to LEAR
            return False
        # rule directly from LEAR code
        last_file_date = item_dict['last_ar_date'] or item_dict['founding_date']
        return last_file_date + datedelta(years=1, months=2, days=1) > datetime.now(tz=timezone.utc)
    # source == COLIN
    if item_dict['corp_class'] in ['BC'] or item_dict['legal_type'] in ['LLC', 'LIC', 'A', 'B']:
        if item_dict.get('state_type') in ['D1A', 'D1F', 'D1T', 'D2A', 'D2F', 'D2T', 'LIQ', 'LRL', 'LRS']:
            # Dissolution state or Liquidation or Limited Restoration or is NOT in good standing
            #   - updates into Dissolution states occur irregularly via batch job
            #   - updates out of these states occur immediately when filing is processed
            #     (can rely on this for a business being NOT in good standing only)
            return False
        if item_dict.get('xpro_jurisdiction') in ['AB', 'MB', 'SK']:
            # NWPTA don't need to file ARs so we can't verify good standing
            return None
        requires_transition = item_dict['founding_date'] and item_dict['founding_date'] < datetime(2004, 3, 29)
        if requires_transition and item_dict['transition_dt'] is None:
            # Businesses incorporated prior to March 29th, 2004 must file a transition filing
            if restoration_date := item_dict['restoration_date']:
                # restored businesses that require transition have 1 year to do so
                return restoration_date + datedelta(years=1) > datetime.utcnow()
            return False
        if last_file_date := (item_dict['last_ar_date'] or item_dict['founding_date']):
            # return if the last AR or founding date was within a year and 2 months
            return last_file_date + datedelta(years=1, months=2, days=1) > datetime.utcnow()
        # shouldn't get here unless there's a data issue
        current_app.logger.debug(
            'Business %s has no last_ar_filed_dt or recognition_dts in their corporation record.',
            item_dict['identifier'])
    # requirements unclear/untested for other COLIN cases
    return None


def _get_business_name(doc_info: dict) -> str:
    """Return the parsed name of the business in the given doc info."""
    if doc_info['legal_name']:
        return doc_info['legal_name'].strip()
    return doc_info.get('legal_name_alt', '').strip()


def _get_party_name(doc_info: dict) -> str:
    """Return the parsed name of the party in the given doc info."""
    if doc_info['organization_name']:
        return doc_info['organization_name'].strip()
    if doc_info.get('organization_name_alt'):
        return doc_info['organization_name_alt'].strip()
    if doc_info.get('organization_name_colin'):
        return doc_info['organization_name_colin'].strip()
    person_name = ''
    if doc_info['first_name']:
        person_name += doc_info['first_name'].strip()
    if doc_info['middle_initial']:
        person_name += ' ' + doc_info['middle_initial'].strip()
    if doc_info['last_name']:
        person_name += ' ' + doc_info['last_name'].strip()
    return person_name.strip()


def _get_party_role(type_cd: str, legal_type: str) -> str:
    """Return the lear party_type given the colin party type code."""
    if type_cd == ColinPartyTypeCode.DIRECTOR:
        return 'director'
    if type_cd == ColinPartyTypeCode.FIRM_COMP_PARTY:
        return 'completing_party'
    if type_cd == ColinPartyTypeCode.INCORPORATOR:
        return 'incorporator'
    if type_cd in [ColinPartyTypeCode.FIRM_BUS_OWNER.value, ColinPartyTypeCode.FIRM_IND_OWNER.value]:
        if legal_type == 'SP':
            return 'proprietor'
        return 'partner'
    return 'unknown'


def prep_data(data: list, data_descs: list[str], source: str) -> list[dict]:  # pylint: disable=too-many-branches
    """Return the list of BusinessDocs for the given raw db data."""
    prepped_data = {}

    for item in data:
        item_dict = dict(zip(data_descs, item))
        # NOTE: if a business has > 1 restoration filing it will have a record per restoration
        #  - code will ignore duplicates below (expects most relevant restoration to come first)
        base_doc_already_added = item_dict['identifier'] in prepped_data
        party_id = item_dict.get('party_id') or item_dict.get('party_id_colin')

        if party_id and source == 'COLIN':
            # prep party fields
            if not item_dict.get('role'):
                item_dict['role'] = _get_party_role(item_dict.get('party_typ_cd'), item_dict['legal_type'])
            if not item_dict.get('party_type'):
                item_dict['party_type'] = 'organization' if item_dict['organization_name'] else 'person'

        if base_doc_already_added and party_id:
            # base doc already added, update with party doc info
            if party_id in prepped_data[item_dict['identifier']]['parties']:
                # party doc already added, add extra role
                party_roles = prepped_data[item_dict['identifier']]['parties'][party_id]['partyRoles']
                if item_dict['role'] not in party_roles:
                    party_roles.append(item_dict['role'])
            else:
                # add party doc to base doc
                prepped_data[item_dict['identifier']]['parties'][party_id] = {
                    'id': f"{item_dict['identifier']}_{party_id}",
                    'parentBN': item_dict['tax_id'],
                    'parentIdentifier': item_dict['identifier'],
                    'parentLegalType': item_dict['legal_type'],
                    'parentName': _get_business_name(item_dict),
                    'parentStatus': item_dict['state'],
                    'partyName': _get_party_name(item_dict),
                    'partyRoles': [item_dict['role']],
                    'partyType': item_dict['party_type']
                }

        elif not base_doc_already_added:
            # add new base doc
            identifier = item_dict['identifier']
            if source == 'COLIN' and item_dict['legal_type'] in ['BC', 'CC', 'ULC']:
                identifier = f'BC{identifier}'
            prepped_data[identifier] = {
                'goodStanding': _is_good_standing(item_dict, source),
                'legalType': item_dict['legal_type'],
                'id': identifier,
                'identifier': identifier,
                'name': _get_business_name(item_dict),
                'status': item_dict['state'],
                'bn': item_dict['tax_id']
            }
            if party_id:
                # add party doc to base doc
                prepped_data[identifier]['parties'] = {
                    party_id: {
                        'id': f'{identifier}_{party_id}',
                        'parentBN': item_dict['tax_id'],
                        'parentIdentifier': identifier,
                        'parentLegalType': item_dict['legal_type'],
                        'parentName': _get_business_name(item_dict),
                        'parentStatus': item_dict['state'],
                        'partyName': _get_party_name(item_dict),
                        'partyRoles': [item_dict['role']],
                        'partyType': item_dict['party_type']
                    }
                }
    # flatten the data to a list of solr docs (also flatten the parties to a list)
    solr_docs = []
    for identifier, base_doc in prepped_data.items():
        if base_doc.get('parties'):
            flattened_parties = []
            for party_key in base_doc['parties']:
                if party := base_doc['parties'][party_key]:
                    flattened_parties.append(party)
            if flattened_parties:
                base_doc['parties'] = flattened_parties
        solr_docs.append(base_doc)
    return solr_docs


def prep_data_btr(data: list[dict]) -> list[dict]:
    """Return the list of partial business docs containing the SI party information."""
    prepped_data: list[dict] = []

    for item in data:
        submission = item[0]
        identifier = submission['businessIdentifier']

        business = {'id': identifier, 'parties': {'add': []}}

        # collect current SIs.
        for person in submission.get('personStatements', []):
            party_name = ''
            for name in person.get('names'):
                if name.get('type') == 'individual':  # expecting this to be 'individual' or 'alternative'
                    party_name = name.get('fullName')
                    break
            if not party_name:
                current_app.logger.debug('Person names: %s', person.get('names'))
                current_app.logger.error('Error parsing SI name for %s', identifier)

            business['parties']['add'].append({
                PartyField.UNIQUE_KEY.value: identifier + '_' + person['uuid'],
                PartyField.PARTY_NAME.value: party_name,
                PartyField.PARTY_ROLE.value: ['significant individual'],
                PartyField.PARENT_TYPE.value: 'person'
            })

        prepped_data.append(business)

    return prepped_data
