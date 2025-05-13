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
"""Manages util methods for updating business solr via the reg search api."""
import time
from http import HTTPStatus

import requests
from flask import current_app

from search_api.exceptions import SolrException
from search_api.services.authz import get_bearer_token


def _get_wait_interval(err: Exception):
    """Return the base wait interval for the exception."""
    if (isinstance(err.args, tuple | list) and
        err.args and
        isinstance(err.args[0], dict) and
        "408" in err.args[0].get("error", {}).get("detail", "")
    ):
        # increased base wait time for solr 408 error
        return 60
    return 20


def update_solr(docs: list[dict], data_name: str, partial=False) -> int:
    """Import data into solr."""
    current_app.logger.debug("Getting token for Import...")
    token = get_bearer_token()
    headers = {"Authorization": "Bearer " + token}
    current_app.logger.debug("Token set.")
    api_url = f'{current_app.config.get("SEARCH_API_URL")}{current_app.config.get("SEARCH_API_V1")}'
    count = 0
    offset = 0
    rows = current_app.config.get("BATCH_SIZE_SOLR", 1000)
    if data_name == "BTR":
        rows = current_app.config.get("BATCH_SIZE_SOLR_SI", 1000)
    retry_count = 0
    while count < len(docs) and rows > 0 and len(docs) - offset > 0:
        batch_amount = int(min(rows, len(docs) - offset) / (retry_count + 1))
        count += batch_amount
        # call api import endpoint
        try:
            current_app.logger.debug("Importing batch...")
            import_resp = requests.put(url=f"{api_url}/internal/solr/import",
                                       headers=headers,
                                       json={"businesses": docs[offset:count],
                                             "timeout": "60",
                                             "type": "partial" if partial else "full"},
                                       timeout=90)

            if import_resp.status_code != HTTPStatus.CREATED:
                if import_resp.status_code == HTTPStatus.UNAUTHORIZED:
                    # renew token for next try
                    current_app.logger.debug("Getting new token for Import...")
                    token = get_bearer_token()
                    headers = {"Authorization": "Bearer " + token}
                    current_app.logger.debug("New Token set.")
                # try again
                raise Exception({"error": import_resp.json(), "status_code": import_resp.status_code})  # noqa: E501; pylint: disable=broad-exception-raised
            retry_count = 0
        except Exception as err:
            current_app.logger.debug(err)
            if retry_count < 5:  # noqa: PLR2004
                # retry
                current_app.logger.debug("Failed to update solr with batch. Trying again (%s of 5)...", retry_count + 1)
                retry_count += 1
                # await some time before trying again
                base_wait_time = _get_wait_interval(err)
                current_app.logger.debug("Awaiting %s seconds before trying again...", base_wait_time * retry_count)
                time.sleep(base_wait_time * retry_count)
                # set count back
                count -= batch_amount
                continue
            if retry_count == 5:  # noqa: PLR2004
                # wait x minutes and then try one more time
                current_app.logger.debug(
                    "Max retries for batch exceeded. Awaiting 2 mins before trying one more time...")
                time.sleep(120)
                # renew token for next try
                current_app.logger.debug("Getting new token for Import...")
                token = get_bearer_token()
                headers = {"Authorization": "Bearer " + token}
                current_app.logger.debug("New Token set.")
                # try again
                retry_count += 1
                count -= batch_amount
                continue
            # log and raise error
            current_app.logger.error("Retry count exceeded for batch.")
            raise SolrException("Retry count exceeded for updating SOLR. Aborting import.") from err
        offset = count
        current_app.logger.debug(f"Total batch {data_name} doc records imported: {count}")
    return count


def resync():
    """Resync to catch any records that had an update during the import."""
    current_app.logger.debug("Getting token for Resync...")
    token = get_bearer_token()
    headers = {"Authorization": "Bearer " + token}

    current_app.logger.debug("Resyncing any overwritten docs during import...")
    api_url = f'{current_app.config.get("SEARCH_API_URL")}{current_app.config.get("SEARCH_API_V1")}'
    resync_resp = requests.post(url=f"{api_url}/internal/solr/update/resync",
                                headers=headers,
                                json={"minutesOffset": current_app.config.get("RESYNC_OFFSET")},
                                timeout=60)
    if resync_resp.status_code != HTTPStatus.CREATED:
        if resync_resp.status_code == HTTPStatus.GATEWAY_TIMEOUT:
            current_app.logger.debug("Resync timed out -- check api for any individual failures.")
        else:
            current_app.logger.error("Resync failed: %s, %s", resync_resp.status_code, resync_resp.json())
    else:
        current_app.logger.debug("Resync complete.")
