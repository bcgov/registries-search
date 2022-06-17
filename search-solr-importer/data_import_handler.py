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

from flask import current_app
# from legal_api.models import Business
from search_api.services import solr
from search_api.services.solr import SolrDoc

from search_solr_importer import create_app, oracle_db


def collect_colin_data():
    """Collect data from COLIN."""
    current_app.logger.debug('Connecting to Oracle...')
    cursor = oracle_db.connection.cursor()
    current_app.logger.debug(f'Collecting COLIN data...')
    cursor.execute(
        f"""
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


def load_search_core():
    """Load data from LEAR and COLIN into the search core."""
    colin_data_cur = collect_colin_data()
    colin_data = colin_data_cur.fetchall()
    current_app.logger.debug(f'Collected {len(colin_data)} COLIN records for import. Updating SOLR core...')
    count = 0
    rows = current_app.config.get('BATCH_SIZE', 1000)
    # delete existing index
    # solr.delete_all_docs()
    # execute update to solr in batches
    while count < len(colin_data):
        offset = count
        limit = count + rows
        docs = []
        for business in colin_data[offset:limit]:
            bus_dict = dict(zip([x[0].lower() for x in colin_data_cur.description], business))
            docs.append(SolrDoc(bus_dict))
            count += 1
        solr.create_or_replace_docs(docs)

        current_app.logger.debug(f'Total records imported: {count}')
    current_app.logger.debug('COLIN import completed.')

if __name__ == '__main__':
    print('Starting data importer...')
    app = create_app()
    with app.app_context():
        load_search_core()