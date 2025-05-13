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
"""The Search solr data import service."""
import gc
import sys

from flask import current_app

from search_api.exceptions import SolrException
from search_solr_importer import create_app
from search_solr_importer.utils import (
    collect_btr_data,
    collect_colin_data,
    collect_lear_data,
    prep_data,
    prep_data_btr,
    reindex_post,
    reindex_prep,
    reindex_recovery,
    resync,
    update_solr,
)


def load_search_core():  # pylint: disable=too-many-statements,too-many-locals,too-many-branches; will update
    """Load data from LEAR and COLIN into the search core."""
    try:
        is_reindex = current_app.config.get("REINDEX_CORE")
        is_preload = current_app.config.get("PRELOADER_JOB")
        include_btr_load = current_app.config.get("INCLUDE_BTR_LOAD")
        include_colin_load = current_app.config.get("INCLUDE_COLIN_LOAD")
        include_lear_load = current_app.config.get("INCLUDE_LEAR_LOAD")
        final_record = None

        if is_reindex and current_app.config.get("IS_PARTIAL_IMPORT"):
            current_app.logger.error("Attempted reindex on partial data set.")
            current_app.logger.debug("Setting reindex to False to prevent potential data loss.")
            is_reindex = False

        if is_reindex:
            current_app.logger.debug("---------- Pre Reindex Actions ----------")
            reindex_prep(is_preload)

        try:
            colin_count = 0
            if include_colin_load:
                current_app.logger.debug("---------- Collecting/Importing COLIN Entities ----------")
                colin_data_cur = collect_colin_data()
                current_app.logger.debug("Fetching corp batch rows...")
                colin_data = colin_data_cur.fetchall()
                colin_data_descs = [desc[0].lower() for desc in colin_data_cur.description]
                colin_data_cur.close()
                # NB: need full data set under each corp num to collapse parties properly
                current_app.logger.debug("********** Mapping COLIN Entities **********")
                prepped_colin_data = prep_data(colin_data,
                                               colin_data_descs,
                                               "COLIN")
                current_app.logger.debug(f"COLIN businesses ready for import: {len(prepped_colin_data)}")
                # execute update to solr in batches
                current_app.logger.debug("********** Importing COLIN Entities **********")
                colin_count = update_solr(prepped_colin_data, "COLIN")
                # free up memory
                final_record = [prepped_colin_data[-1]], "COLIN", False
                del colin_data, prepped_colin_data
                gc.collect()
                current_app.logger.debug(f"COLIN import completed. Total COLIN businesses imported: {colin_count}.")

            lear_count = 0
            if include_lear_load:
                current_app.logger.debug("---------- Collecting LEAR Entities ----------")
                lear_data_cur = collect_lear_data()
                lear_data = lear_data_cur.fetchall()

                current_app.logger.debug("---------- Mapping LEAR data ----------")
                prepped_lear_data = prep_data(
                    data=lear_data,
                    data_descs=[desc[0].lower() for desc in lear_data_cur.description],
                    source="LEAR",
                )
                current_app.logger.debug(f"{len(prepped_lear_data)} LEAR records ready for import.")

                # execute update to solr in batches
                current_app.logger.debug("---------- Importing LEAR entities ----------")
                lear_count = update_solr(prepped_lear_data, "LEAR")
                # free up memory
                final_record = [prepped_lear_data[-1]], "LEAR", False
                del lear_data, prepped_lear_data
                gc.collect()
                current_app.logger.debug(f"LEAR import completed. Total LEAR businesses imported: {lear_count}")

            current_app.logger.debug(f"Total businesses imported: {colin_count + lear_count}")

            total_btr_count = 0
            if include_btr_load:
                current_app.logger.debug("---------- Collecting/Importing BTR Data ----------")
                btr_fetch_count = 0
                batch_limit = current_app.config.get("BTR_BATCH_LIMIT")
                btr_data_descs = []
                loop_count = 0

                while loop_count < 100:  # NOTE: should never get to this condition
                    loop_count += 1
                    current_app.logger.debug("********** Collecting BTR data **********")
                    btr_data_cur = collect_btr_data(batch_limit, btr_fetch_count)
                    btr_data = btr_data_cur.fetchall()
                    btr_fetch_count += len(btr_data)
                    btr_data_cur.close()
                    if not btr_data:
                        break

                    current_app.logger.debug("********** Mapping BTR data **********")
                    if not btr_data_descs:
                        # just need to do once
                        btr_data_descs = [desc[0].lower() for desc in btr_data_cur.description]
                    prepped_btr_data = prep_data_btr(btr_data, btr_data_descs)
                    current_app.logger.debug(f"{len(prepped_btr_data)} BTR records ready for import.")

                    current_app.logger.debug("********** Importing BTR entities **********")
                    total_btr_count += update_solr(prepped_btr_data, "BTR", True)
                    current_app.logger.debug(f"BTR batch import completed. Records imported: {total_btr_count}.")
                    # free up memory
                    final_record = [prepped_btr_data[-1]], "BTR", True
                    del btr_data, prepped_btr_data
                    gc.collect()

                current_app.logger.debug(f"BTR import completed. Total BTR partial records imported: {total_btr_count}")

        except Exception as err:
            if is_reindex and not is_preload:
                reindex_recovery()
            raise err  # pass along

        try:
            current_app.logger.debug("---------- Resync ----------")
            resync()
        except Exception as error:
            current_app.logger.debug(error.with_traceback(None))
            current_app.logger.error("Resync failed.")

        try:
            current_app.logger.debug("---------- Final Commit ----------")
            current_app.logger.debug("Triggering final commit on leader to make changes visible to search...")
            update_solr(final_record[0], final_record[1], final_record[2])
            current_app.logger.debug("Final commit complete.")

        except Exception as error:
            current_app.logger.debug(error.with_traceback(None))
            current_app.logger.error("Final commit failed. (This will only effect DEV).")

        if is_reindex and not is_preload:
            current_app.logger.debug("---------- Post Reindex Actions ----------")
            reindex_post()

        current_app.logger.debug("SOLR import finished successfully.")

    except SolrException as err:
        current_app.logger.debug(f"SOLR gave status code: {err.status_code}")
        current_app.logger.error(err.error)
        current_app.logger.debug("SOLR import failed.")
        sys.exit(1)


if __name__ == "__main__":
    print("Starting data importer...")
    app = create_app()  # pylint: disable=invalid-name
    with app.app_context():
        load_search_core()
        sys.exit(0)
