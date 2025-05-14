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
"""Manages util methods for reindexing."""
from datetime import UTC, datetime
from http import HTTPStatus
from time import sleep

from flask import current_app

from search_api.exceptions import SolrException
from search_api.services import business_solr


def get_replication_detail(field: str, leader: bool):
    """Return the replication detail for the core."""
    details: dict = (business_solr.replication("details", leader)).json()["details"]
    # remove data unwanted in the logs
    if field != "commits" and "commits" in details:
        del details["commits"]
    if not leader and field != "leaderDetails" and "leaderDetails" in details["follower"]:
        del details["follower"]["leaderDetails"]

    # log full details and return data element
    current_app.logger.debug("Full replication details: %s", details)
    if leader:
        return details.get(field)
    return details["follower"].get(field)


def reindex_prep(is_preload: bool):
    """Execute reindex operations needed before index is reloaded."""
    if not is_preload:
        # backup leader index
        backup_trigger_time = (datetime.utcnow()).replace(tzinfo=UTC)
        backup = business_solr.replication("backup", True)
        current_app.logger.debug(backup.json())
        if current_app.config.get("HAS_FOLLOWER", True):
            # disable follower polling during reindex
            disable_polling = business_solr.replication("disablepoll", False)
            current_app.logger.debug(disable_polling.json())
        # await 60 seconds in case a poll was in progress and to give time for backup to complete
        current_app.logger.debug("Pausing 60s for SOLR to complete reindex prep...")
        sleep(60)
        # verify current backup is from just now and was successful in case of failure
        current_app.logger.debug("Verifying SOLR reindex prep...")
        backup_succeeded = False
        for i in range(20):
            current_app.logger.debug(f"Checking new backup {i + 1} of 20...")
            if backup_detail := get_replication_detail("backup", True):
                backup_start_time = datetime.fromisoformat(backup_detail["startTime"])
                if backup_detail["status"] == "success" and backup_trigger_time < backup_start_time:
                    backup_succeeded = True
                    break
            # retry repeatedly (new backup in prod will take a couple minutes)
            sleep(30 + (i*2))
        if not backup_succeeded:
            raise SolrException("Failed to backup leader index", HTTPStatus.INTERNAL_SERVER_ERROR)
        current_app.logger.debug("Backup succeeded. Checking polling disabled...")
        if current_app.config.get("HAS_FOLLOWER", True):
            # verify follower polling disabled so it doesn't update until reindex is complete
            is_polling_disabled = get_replication_detail("isPollingDisabled", False)
            if not bool(is_polling_disabled):
                current_app.logger.debug("is_polling_disabled: %s", is_polling_disabled)
                raise SolrException("Failed disable polling on follower",
                                    str(is_polling_disabled),
                                    HTTPStatus.INTERNAL_SERVER_ERROR)
            current_app.logger.debug("Polling disabled. Disabling leader replication...")
            # disable leader replication for reindex duration (important to do this after polling disabled)
            disable_replication = business_solr.replication("disablereplication", True)
            current_app.logger.debug(disable_replication.json())

    # delete existing index
    current_app.logger.debug("REINDEX_CORE set: deleting current solr index...")
    business_solr.delete_all_docs()


def reindex_post():
    """Execute post reindex operations on the follower index."""
    if current_app.config.get("HAS_FOLLOWER", True):
        # reenable leader replication
        enable_replication = business_solr.replication("enablereplication", True)
        current_app.logger.debug(enable_replication.json())
        sleep(5)
        # force the follwer to fetch the new index
        fetch_new_idx = business_solr.replication("fetchindex", False)
        current_app.logger.debug(fetch_new_idx.json())
        sleep(10)
        # renable polling
        enable_polling = business_solr.replication("enablepoll", False)
        current_app.logger.debug(enable_polling.json())


def reindex_recovery():
    """Restore the index on the leader and renable polling on the follower."""
    restore = business_solr.replication("restore", True)
    current_app.logger.debug(restore.json())
    current_app.logger.debug("awaiting restore completion...")
    for i in range(100):
        current_app.logger.debug(f"Checking restore status ({i + 1} of 100)...")
        status = business_solr.replication("restorestatus", True)
        current_app.logger.debug(status)
        current_app.logger.debug(status.json())
        if (status.json())["restorestatus"]["status"] == "success":
            current_app.logger.debug("restore complete.")
            enable_replication = business_solr.replication("enablereplication", True)
            current_app.logger.debug(enable_replication.json())
            sleep(5)
            enable_polling = business_solr.replication("enablepolling", False)
            current_app.logger.debug(enable_polling.json())
            return
        if (status.json())["status"] == "failed":
            break
        sleep(10 + (i*2))
    current_app.logger.error("Possible failure to restore leader index. Manual intervention required.")
