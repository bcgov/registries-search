#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service for listening and handling Queue Messages.

This service registers interest in listening to a Queue and processing received messages.
"""
import asyncio
import functools
import getopt
import json
import os
import random
import signal
import sys
from datetime import datetime

from nats.aio.client import Client as NATS  # noqa N814; by convention the name is NATS
from stan.aio.client import Client as STAN  # noqa N814; by convention the name is STAN


async def run(loop, identifier):
    """Run the main application loop for the service.

    This runs the main top level service functions for working with the Queue.
    """
    from entity_queue_common.service_utils import error_cb, logger, signal_handler

    # NATS client connections
    nc = NATS()
    sc = STAN()

    async def close():
        """Close the stream and nats connections."""
        await sc.close()
        await nc.close()

    # Connection and Queue configuration.
    def nats_connection_options():
        return {
            'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
            'io_loop': loop,
            'error_cb': error_cb,
            'name': os.getenv('NATS_SEARCH_SOLR_CLIENT_NAME', 'search.solr.worker')
        }

    def stan_connection_options():
        return {
            'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
            'client_id': str(random.SystemRandom().getrandbits(0x58)),
            'nats': nc
        }

    def subscription_options():
        return {
            'subject': os.getenv('NATS_ENTITY_EVENTS_SUBJECT', 'entity.events'),
            'queue': os.getenv('NATS_SEARCH_SOLR_QUEUE', 'search-solr-worker'),
            'durable_name': os.getenv('NATS_SEARCH_SOLR_QUEUE', 'search-solr-worker') + '_durable'
        }

    try:
        # Connect to the NATS server, and then use that for the streaming connection.
        await nc.connect(**nats_connection_options())
        await sc.connect(**stan_connection_options())

        # register the signal handler
        for sig in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig),
                                    functools.partial(signal_handler, sig_loop=loop, sig_nc=nc, task=close)
                                    )
        payload = {
            'specversion': '1.0.1',
            'type': 'bc.registry.business.solr-update',
            'source': '/requests/6724165',
            'id': 1234,
            'time': str(datetime.now()),
            'datacontenttype': 'application/json',
            'identifier': identifier
        }

        await sc.publish(subject=subscription_options().get('subject'),
                         payload=json.dumps(payload).encode('utf-8'))

    except Exception as e:  # pylint: disable=broad-except
        # TODO tighten this error and decide when to bail on the infinite reconnect
        logger.error(e)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["id=", ])
    except getopt.GetoptError:
        print('q_cli.py -i <business_identifier>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('q_cli.py -i <business_identifier>')
            sys.exit()
        elif opt in ("-i", "--id"):
            identifier = arg

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run(event_loop, identifier))

# python3 q_cli.py -i BC1234567
