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
"""The unique worker functionality for this service is contained here.

The entry-point is the **cb_nr_subscription_handler**

The design and flow leverage a few constraints that are placed upon it
by NATS Streaming and using AWAIT on the default loop.
- NATS streaming queues require one message to be processed at a time.
- AWAIT on the default loop effectively runs synchronously
"""
import json
import logging
import os
from contextlib import suppress
from http import HTTPStatus
from time import sleep
from typing import Dict

import nats
import requests
import sentry_sdk
from entity_queue_common.service import QueueServiceManager
from entity_queue_common.service_utils import QueueException
from flask import Flask  # pylint: disable=wrong-import-order
from requests import exceptions
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from search_solr_updater import config
from search_solr_updater.logging import logger
from search_solr_updater.utils import get_bearer_token, get_business_info, get_run_version


async def cb_nr_subscription_handler(msg: nats.aio.client.Msg):
    """Use Callback to process Queue Msg objects."""
    try:
        logger.info(APP_CONFIG)
        logger.info('Received raw message seq:%s, data=  %s', msg.sequence, msg.data.decode())
        event_message = json.loads(msg.data.decode('utf-8'))
        logger.debug('Event Message Received: %s', event_message)
        await process_event(event_message, FLASK_APP)
    except QueueException as err:
        logger.error('search-solr-updater: %s', err)
    except Exception as err:  # noqa pylint: disable=broad-except
        logger.debug(err.with_traceback(None))
        # NB: sentry breadcrumb will contain event msg already
        logger.error('search-solr-updater: Unhandled error')


async def process_event(event_message, flask_app):
    """Render the org status."""
    if not flask_app:
        raise QueueException('Flask App not available.')

    with flask_app.app_context():
        message_type = event_message.get('type', None)

        if 'bc.registry.business' in message_type:  # expecting bc.registry.business.<filing type>
            await process_business_event(event_message)


async def process_business_event(event_message: Dict[str, any]):  # pylint: disable=too-many-locals
    """Process business events.

    1. Get business data + parties data from legal-api
    2. Call search-api to update solr

    Args:
        event_message (object): cloud event message, format below.
            {
                'specversion': '1.0.1',
                'type': 'bc.registry.business.:filing_type',
                'source': '<str>',
                'id': :str(uuid.uuid4()),
                'time': ':datetime.utcnow().isoformat()',
                'datacontenttype': 'application/json',
                'identifier': ':identifier'
            }
    """
    logger.debug('>>>>>>>process_business_event>>>>>')
    # get identifier
    identifier = event_message.get('identifier')
    if not identifier:
        raise QueueException('Unable to parse identifier from message payload.')
    with suppress(Exception):
        if filings := event_message.get('data', {}).get('filing', {}).get('legalFilings', []):
            # if alteration, then give it 5 seconds (lear will still be processing it in some cases)
            if 'alteration' in filings:
                sleep(5)
    # get token
    token = get_bearer_token()
    headers = {'Authorization': 'Bearer ' + token}
    # get extra data from lear
    business_info_url = f'{APP_CONFIG.LEAR_SVC_URL}/businesses/{identifier}'
    parties_info_url = f'{APP_CONFIG.LEAR_SVC_URL}/businesses/{identifier}/parties'
    business_resp = get_business_info(business_info_url, headers)
    parties_resp = get_business_info(parties_info_url, headers)
    # only add parties that are currently stored in solr
    solr_party_roles = ['partner', 'proprietor']  # solr does not store other parties
    parties = []
    for party in parties_resp.json().get('parties'):
        valid_roles = [x for x in party.get('roles') if x['roleType'].lower() in solr_party_roles]
        if valid_roles:
            party['roles'] = valid_roles
            parties.append(party)

    # update solr via search-api
    try:
        update_payload = {**business_resp.json(), 'parties': parties}
        solr_update_url = f'{APP_CONFIG.SEARCH_API_URL}/internal/solr/update'
        update_resp = requests.put(url=solr_update_url, headers=headers, json=update_payload, timeout=30)
        if update_resp.status_code != HTTPStatus.OK:
            logger.debug(update_resp.json())
            raise QueueException(update_resp.status_code, 'Unable to update search solr via search api.')
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        logger.debug('SEARCH API connection failure: %s', err)
        raise QueueException(HTTPStatus.GATEWAY_TIMEOUT, 'Unable to update search solr via search api.')
    except QueueException as err:
        # pass along
        raise err
    except Exception as err:  # noqa: B902
        logger.debug('SEARCH API connection failure: %s', err.with_traceback(None))
        raise QueueException(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to update search solr via search api.')

    logger.debug('<<<<<<<process_business_event<<<<<<<<<<')


qsm = QueueServiceManager()  # pylint: disable=invalid-name
APP_CONFIG = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object(APP_CONFIG)

# Configure Sentry
if APP_CONFIG.SENTRY_DSN and APP_CONFIG.SENTRY_ENABLE.lower() == 'true':
    SENTRY_LOGGING = LoggingIntegration(
        event_level=logging.ERROR  # Send errors as events
    )
    sentry_sdk.init(
        dsn=APP_CONFIG.SENTRY_DSN,
        integrations=[FlaskIntegration(), SENTRY_LOGGING],
        environment=APP_CONFIG.POD_NAMESPACE,
        release=f'search-solr-updater@{get_run_version()}',
        traces_sample_rate=APP_CONFIG.SENTRY_TSR
    )
