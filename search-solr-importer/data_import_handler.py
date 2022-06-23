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
from http import HTTPStatus
from typing import List

import psycopg2
from flask import current_app
from search_api.exceptions import SolrException
from search_api.services import solr
from search_api.services.solr import SolrDoc

from search_solr_importer import create_app, oracle_db


def collect_colin_data():
    """Collect data from COLIN."""
    current_app.logger.debug('Connecting to Oracle instance...')
    cursor = oracle_db.connection.cursor()
    current_app.logger.debug('Collecting COLIN data...')
    cursor.execute("""
        SELECT c.corp_num as identifier, c.corp_typ_cd as legaltype, c.bn_15 as bn,
          CASE cs.state_typ_cd
            when 'ACT' then 'ACTIVE' when 'HIS' then 'HISTORICAL' when 'HLD' then 'LIQUIDATION'
            else cs.state_typ_cd END as status,
          cn.corp_nme as name
        FROM corporation c
          join corp_state cs on cs.corp_num = c.corp_num
          join corp_name cn on cn.corp_num = c.corp_num
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
        SELECT identifier,legal_name as name,legal_type as legalType,state as status,tax_id as bn
        FROM businesses
        WHERE legal_type in ('BEN', 'CP', 'SP', 'GP')
        """)
    return cur


def update_solr(data: List, data_name: str, cur):
    """Import data into solr."""
    count = 0
    rows = current_app.config.get('BATCH_SIZE', 1000)
    # execute update to solr in batches
    while count < len(data):
        offset = count
        limit = count + rows
        docs = []
        for business in data[offset:limit]:
            bus_dict = dict(zip([x[0].lower() for x in cur.description], business))
            docs.append(SolrDoc(bus_dict))
            count += 1
        if count == offset:
            break  # something went wrong

        solr.create_or_replace_docs(docs)
        current_app.logger.debug(f'Total {data_name} records imported: {count}')
    return count


def load_search_core():
    """Load data from LEAR and COLIN into the search core."""
    try:
        colin_data_cur = collect_colin_data()
        colin_data = colin_data_cur.fetchall()
        current_app.logger.debug(f'Collected {len(colin_data)} COLIN records for import.')
        lear_data_cur = collect_lear_data()
        lear_data = lear_data_cur.fetchall()
        current_app.logger.debug(f'Collected {len(lear_data)} LEAR records for import.')
        if current_app.config.get('REINDEX_CORE', False):
            # delete existing index
            current_app.logger.debug('REINDEX_CORE set: deleting current solr index...')
            solr.delete_all_docs()
        # execute update to solr in batches
        current_app.logger.debug('Importing collected records from COLIN...')
        count = update_solr(colin_data, 'COLIN', colin_data_cur)
        current_app.logger.debug('COLIN import completed.')
        current_app.logger.debug('Importing collected records from LEAR...')
        count += update_solr(lear_data, 'LEAR', lear_data_cur)
        current_app.logger.debug('LEAR import completed.')
        current_app.logger.debug(f'Total records imported: {count}')
        if current_app.config.get('REINDEX_CORE', False):
            current_app.logger.debug('Building suggester...')
            solr.suggest('', 1, True)
            current_app.logger.debug('Suggester built.')
        current_app.logger.debug('SOLR import finished successfully.')

    except SolrException as err:
        current_app.logger.error(f'SOLR gave status code: {err.status_code}')
        if err.status_code == HTTPStatus.BAD_GATEWAY:
            current_app.logger.debug('SOLR timeout most likely due to suggester build. ' +
                                     'Please wait a couple minutes and then verify import '
                                     'and suggester build manually in the solr admin UI.')
        else:
            current_app.logger.error(err.error)
            current_app.logger.error('SOLR import failed.')


if __name__ == '__main__':
    print('Starting data importer...')
    app = create_app()  # pylint: disable=invalid-name
    with app.app_context():
        load_search_core()
