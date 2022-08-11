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
"""The SEARCH API service.

This module is the API for the BC Registries Registry Search system.
"""
import sys
from http import HTTPStatus
from typing import Dict, List, Optional

import psycopg2
from flask import current_app
from search_api.exceptions import SolrException
from search_api.services import solr
from search_api.services.solr import SolrDoc

from search_solr_importer import create_app, oracle_db
from search_solr_importer.enums import ColinPartyTypeCode


def collect_colin_data():
    """Collect data from COLIN."""
    current_app.logger.debug('Connecting to Oracle instance...')
    cursor = oracle_db.connection.cursor()
    current_app.logger.debug('Collecting COLIN data...')
    cursor.execute("""
        SELECT c.corp_num as identifier, c.corp_typ_cd as legal_type, c.bn_15 as tax_id,
            cn.corp_nme as legal_name, cp.business_nme as organization_name, cp.first_nme as first_name,
            cp.last_nme as last_name, cp.middle_nme as middle_initial, cp.party_typ_cd, cp.corp_party_id as party_id,
            CASE cos.state_typ_cd
                when 'ACT' then 'ACTIVE' when 'HIS' then 'HISTORICAL'
                else 'ACTIVE' END as state
        FROM corporation c
        join corp_state cs on cs.corp_num = c.corp_num
        join corp_op_state cos on cos.state_typ_cd = cs.state_typ_cd
        join corp_name cn on cn.corp_num = c.corp_num
        left join (select business_nme, first_nme, last_nme, middle_nme, corp_num, party_typ_cd, corp_party_id
                from corp_party
                where end_event_id is null and party_typ_cd in ('FIO','FBO')
            ) cp on cp.corp_num = c.corp_num
        WHERE c.corp_typ_cd not in ('BEN','CP','GP','SP')
            and cs.end_event_id is null
            and cn.end_event_id is null
            and cn.corp_name_typ_cd in ('CO', 'NB')
        """)
    return cursor


def collect_lear_data():
    """Collect data from LEAR."""
    current_app.logger.debug('Connecting to Postgres instance...')
    conn = psycopg2.connect(host=current_app.config.get('DB_HOST'),
                            port=current_app.config.get('DB_PORT'),
                            database=current_app.config.get('DB_NAME'),
                            user=current_app.config.get('DB_USER'),
                            password=current_app.config.get('DB_PASSWORD'))
    cur = conn.cursor()
    current_app.logger.debug('Collecting LEAR data...')
    cur.execute("""
        SELECT b.identifier,b.legal_name,b.legal_type,b.tax_id, pr.role, p.first_name,
            p.middle_initial, p.last_name, p.organization_name, p.party_type, p.id as party_id,
            CASE when b.state = 'LIQUIDATION' then 'ACTIVE' else b.state END state
        FROM businesses b
            LEFT JOIN (SELECT * FROM party_roles WHERE cessation_date is null
                       AND role in ('partner', 'proprietor')) as pr on pr.business_id = b.id
            LEFT JOIN parties p on p.id = pr.party_id
        WHERE b.legal_type in ('BEN', 'CP', 'SP', 'GP')
        """)
    return cur


def prep_data(data: List, cur) -> List[SolrDoc]:
    """Return the list of SolrDocs for the given raw db data."""
    prepped_data = {}

    def get_party_name(doc_info: Dict) -> str:
        """Return the parsed name of the party in the given doc info."""
        if doc_info['organization_name']:
            return doc_info['organization_name'].strip()
        person_name = ''
        if doc_info['first_name']:
            person_name += doc_info['first_name'].strip()
        if doc_info['middle_initial']:
            person_name += ' ' + doc_info['middle_initial'].strip()
        if doc_info['last_name']:
            person_name += ' ' + doc_info['last_name'].strip()
        return person_name.strip()

    def get_party_role(type_cd: str, legal_type: str) -> Optional[str]:
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

    for item in data:
        item_dict = dict(zip([x[0].lower() for x in cur.description], item))
        base_doc_already_added = item_dict['identifier'] in prepped_data
        has_party = item_dict.get('party_id')
        if has_party:
            # prep party fields
            if not item_dict.get('role'):
                item_dict['role'] = get_party_role(item_dict.get('party_typ_cd'), item_dict['legal_type'])
            if not item_dict.get('party_type'):
                item_dict['party_type'] = 'organization' if item_dict['organization_name'] else 'person'

        if base_doc_already_added and has_party:
            # base doc already added, add extra party doc
            if item_dict['party_id'] in prepped_data[item_dict['identifier']]['parties']:
                # party doc already added, add extra role
                party_roles = prepped_data[item_dict['identifier']]['parties'][item_dict['party_id']]['partyRoles']
                party_roles.append(item_dict['role'])
            else:
                # add party doc to base doc
                prepped_data[item_dict['identifier']]['parties'][item_dict['party_id']] = {
                    'parentBN': item_dict['tax_id'],
                    'parentLegalType': item_dict['legal_type'],
                    'parentName': item_dict['legal_name'],
                    'parentStatus': item_dict['state'],
                    'partyName': get_party_name(item_dict),
                    'partyRoles': [item_dict['role']],
                    'partyType': item_dict['party_type']
                }

        elif not base_doc_already_added:
            # add new base doc
            prepped_data[item_dict['identifier']] = {
                'identifier': item_dict['identifier'],
                'name': item_dict['legal_name'],
                'legaltype': item_dict['legal_type'],
                'status': item_dict['state'],
                'bn': item_dict['tax_id']
            }
            if has_party:
                # add party doc to base doc
                prepped_data[item_dict['identifier']]['parties'] = {
                    item_dict['party_id']: {
                        'parentBN': item_dict['tax_id'],
                        'parentLegalType': item_dict['legal_type'],
                        'parentName': item_dict['legal_name'],
                        'parentStatus': item_dict['state'],
                        'partyName': get_party_name(item_dict),
                        'partyRoles': [item_dict['role']],
                        'partyType': item_dict['party_type']
                    }
                }
    # flatten the data to a list of solr docs (also flatten the parties to a list)
    solr_docs = []
    for identifier in prepped_data:
        base_doc = prepped_data[identifier]
        if base_doc.get('parties'):
            flattened_parties = []
            for party_key in base_doc['parties']:
                flattened_parties.append(base_doc['parties'][party_key])
            base_doc['parties'] = flattened_parties
        solr_docs.append(SolrDoc(base_doc))
    return solr_docs


def update_solr(base_docs: List[SolrDoc], data_name: str) -> int:
    """Import data into solr."""
    count = 0
    offset = 0
    rows = current_app.config.get('BATCH_SIZE', 1000)
    while count < len(base_docs) and rows > 0 and len(base_docs) - offset > 0:
        count += min(rows, len(base_docs) - offset)
        # send batch to solr
        solr.create_or_replace_docs(base_docs[offset:count])
        offset = count
        current_app.logger.debug(f'Total {data_name} base doc records imported: {count}')
    return count


def load_search_core():
    """Load data from LEAR and COLIN into the search core."""
    try:
        colin_data_cur = collect_colin_data()
        colin_data = colin_data_cur.fetchall()
        current_app.logger.debug('Prepping COLIN data...')
        prepped_colin_data = prep_data(colin_data, colin_data_cur)
        current_app.logger.debug(f'{len(prepped_colin_data)} COLIN records ready for import.')
        lear_data_cur = collect_lear_data()
        lear_data = lear_data_cur.fetchall()
        current_app.logger.debug('Prepping LEAR data...')
        prepped_lear_data = prep_data(lear_data, lear_data_cur)
        current_app.logger.debug(f'{len(prepped_lear_data)} LEAR records ready for import.')
        if current_app.config.get('REINDEX_CORE', False):
            # delete existing index
            current_app.logger.debug('REINDEX_CORE set: deleting current solr index...')
            solr.delete_all_docs()
        # execute update to solr in batches
        current_app.logger.debug('Importing records from COLIN...')
        count = update_solr(prepped_colin_data, 'COLIN')
        current_app.logger.debug('COLIN import completed.')
        current_app.logger.debug('Importing records from LEAR...')
        count += update_solr(prepped_lear_data, 'LEAR')
        current_app.logger.debug('LEAR import completed.')
        current_app.logger.debug(f'Total records imported: {count}')
        if current_app.config.get('REINDEX_CORE', False):
            current_app.logger.debug('Building suggester...')
            solr.suggest('', 1, True)
            current_app.logger.debug('Suggester built.')
        current_app.logger.debug('SOLR import finished successfully.')

    except SolrException as err:
        current_app.logger.debug(f'SOLR gave status code: {err.status_code}')
        if err.status_code == HTTPStatus.BAD_GATEWAY:
            current_app.logger.error('SOLR timeout most likely due to suggester build. ' +
                                     'Please wait a couple minutes and then verify import '
                                     'and suggester build manually in the solr admin UI.')
            sys.exit(0)
        else:
            current_app.logger.error(err.error)
            current_app.logger.debug('SOLR import failed.')
        sys.exit(1)


if __name__ == '__main__':
    print('Starting data importer...')
    app = create_app()  # pylint: disable=invalid-name
    with app.app_context():
        load_search_core()
        sys.exit(0)
