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

import requests
from flask import current_app
from search_api.exceptions import SolrException
from search_api.services import search_solr
from search_api.services.solr.solr_docs import BusinessDoc

from search_solr_importer import create_app
from search_solr_importer.utils import collect_colin_data, collect_lear_data, prep_data


def update_solr(base_docs: list[BusinessDoc], data_name: str) -> int:
    """Import data into solr."""
    count = 0
    offset = 0
    rows = current_app.config.get('BATCH_SIZE', 1000)
    retry_count = 0
    erred_record_count = 0
    while count < len(base_docs) and rows > 0 and len(base_docs) - offset > 0:
        batch_amount = min(rows, len(base_docs) - offset)
        count += batch_amount
        # send batch to solr
        try:
            search_solr.create_or_replace_docs(base_docs[offset:count])
            retry_count = 0
        except SolrException as err:  # pylint: disable=bare-except;
            current_app.logger.debug(err)
            if retry_count < 3:
                # retry
                current_app.logger.debug('Failed to update solr. Trying again (%s of 3)...', retry_count + 1)
                retry_count += 1
                # set count back
                count -= batch_amount
                continue

            # log error and skip
            current_app.logger.error('Retry count exceeded for batch. Skipping batch.')
            # add number of records in failed batch to the erred count
            erred_record_count += (count - offset)

        offset = count
        current_app.logger.debug(f'Total {data_name} base doc records imported: {count - erred_record_count}')
    return count


def load_search_core():  # pylint: disable=too-many-statements
    """Load data from LEAR and COLIN into the search core."""
    try:
        colin_data_cur = collect_colin_data()
        colin_data = colin_data_cur.fetchall()
        current_app.logger.debug('Prepping COLIN data...')
        prepped_colin_data = prep_data(colin_data, colin_data_cur, 'COLIN')
        current_app.logger.debug(f'{len(prepped_colin_data)} COLIN records ready for import.')
        lear_data_cur = collect_lear_data()
        lear_data = lear_data_cur.fetchall()
        current_app.logger.debug('Prepping LEAR data...')
        prepped_lear_data = prep_data(lear_data, lear_data_cur, 'LEAR')
        current_app.logger.debug(f'{len(prepped_lear_data)} LEAR records ready for import.')
        if current_app.config.get('REINDEX_CORE', False):
            # delete existing index
            current_app.logger.debug('REINDEX_CORE set: deleting current solr index...')
            search_solr.delete_all_docs()
        # execute update to solr in batches
        current_app.logger.debug('Importing records from COLIN...')
        count = update_solr(prepped_colin_data, 'COLIN')
        current_app.logger.debug('COLIN import completed.')
        current_app.logger.debug('Importing records from LEAR...')
        count += update_solr(prepped_lear_data, 'LEAR')
        current_app.logger.debug('LEAR import completed.')
        current_app.logger.debug(f'Total records imported: {count}')

        if not current_app.config.get('PRELOADER_JOB', False):
            try:
                current_app.logger.debug('Resyncing any overwritten docs during import...')
                search_api_url = f'{current_app.config.get("SEARCH_API_URL")}{current_app.config.get("SEARCH_API_V1")}'
                resync_resp = requests.post(url=f'{search_api_url}/internal/solr/update/resync',
                                            json={'minutesOffset': 60},
                                            timeout=120)
                if resync_resp.status_code != HTTPStatus.CREATED:
                    if resync_resp.status_code == HTTPStatus.GATEWAY_TIMEOUT:
                        current_app.logger.debug('Resync timed out -- check api for any individual failures.')
                    else:
                        current_app.logger.error('Resync failed with status %s', resync_resp.status_code)
                current_app.logger.debug('Resync complete.')
            except Exception as error:  # noqa: B902
                current_app.logger.debug(error.with_traceback(None))
                current_app.logger.error('Resync failed.')

        if current_app.config.get('REINDEX_CORE', False):
            current_app.logger.debug('Building suggester...')
            try:
                search_solr.suggest('', 1, True)
            except SolrException as err:
                current_app.logger.debug(f'SOLR gave status code: {err.status_code}')
                if err.status_code in [HTTPStatus.BAD_GATEWAY, HTTPStatus.GATEWAY_TIMEOUT]:
                    current_app.logger.error('SOLR timeout most likely due to suggester build. ' +
                                             'Please wait a couple minutes and then verify import '
                                             'and suggester build manually in the solr admin UI.')
                    return
                raise err
            current_app.logger.debug('Suggester built.')
        current_app.logger.debug('SOLR import finished successfully.')

    except SolrException as err:
        current_app.logger.debug(f'SOLR gave status code: {err.status_code}')
        current_app.logger.error(err.error)
        current_app.logger.debug('SOLR import failed.')
        sys.exit(1)


if __name__ == '__main__':
    print('Starting data importer...')
    app = create_app()  # pylint: disable=invalid-name
    with app.app_context():
        load_search_core()
        sys.exit(0)
