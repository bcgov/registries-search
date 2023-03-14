# Copyright © 2019 Province of British Columbia
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
"""This class enqueues messages for asynchronous events."""
from __future__ import annotations

from contextlib import suppress
from typing import Final, Union

from flask import Flask
from flask import current_app
# from flask_pub import FlaskPub
from google.cloud import pubsub


__version__ = '0.0.1'

EXTENSION_NAME: Final = 'FLASK_BCROS_PUBSUB'


class Queue():
    """Queue publishing services."""

    def __init__(
            self,
            app: Flask = None,
    ):
        """Initialize the queue services.

        If app is provided, then this is bound to that app instance.
        """
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(
                self,
                app: Flask = None,
                ):
        """Create callback used to initialize this.

        An application can be assigned for use with this queue setup.
        """
        # We intentionally don't set self.app = app, to support multiple
        # applications. If the app is passed in the constructor,
        # we set it and don't support multiple applications.

        if not app.config.get('FLASK_PUB_CONFIG'):
            raise RuntimeError(
                'FLASK_PUB_CONFIG needs to be set.'
            )

        app.config.setdefault('FLASK_PUB_DEFAULT_SUBJECT', None)

        try:
            self.driver = pubsub.PublisherClient()
            app.extensions[EXTENSION_NAME] = self.driver
        except Exception as err:  # noqa: B902
            app.logger.warn('flask_pub.init_app called but unable to create driver. %s', err)

        @app.teardown_appcontext
        def shutdown(response_or_exc):  # pylint: disable=W0612
            """Cleanup all state here as part of the Flask shutdown."""
            return response_or_exc

    def publish(self,
                msg: Union[str, bytes],
                subject: str = None):
        """Publish a message onto the queue subject."""
        if not (app := self.app):  # pylint: disable=C0325
            app = current_app

        topic_name = subject or app.config.get('FLASK_PUB_DEFAULT_SUBJECT')

        if app and topic_name and (_queue := self._get_queue(app)):

            data = msg
            if isinstance(msg, str):
                data = msg.encode('utf8')

            future = _queue.publish(subject, data)  # pylint: disable=W0612; # noqa: F841; an unused future, debugging

    @staticmethod
    def create_subject(
            project: str,
            topic: str,
    ) -> str:
        """Return a fully-qualified topic string."""
        return f'projects/{project}/topics/{topic}'

    @staticmethod
    def _get_queue(app):
        """Get the queue for the application."""
        if queue := app.extensions.get(EXTENSION_NAME):
            return queue

        with suppress(Exception):
            # throw a hail mary to see if we can initialize the driver
            driver = pubsub.PublisherClient()
            app.extensions[EXTENSION_NAME] = driver
            return driver

        raise RuntimeError('The Flask_Pub extension was not registered with the current app.')
