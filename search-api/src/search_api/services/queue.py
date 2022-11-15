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

import json
from typing import Final, Union

from flask import _app_ctx_stack
from flask import Flask
from flask import current_app
from flask_pub import FlaskPub
from google.cloud import pubsub

__version__ = '0.0.1'

EXTENSION_NAME: Final = 'FLASK_BCROS_PUBSUB'


class Queue():
    """Queue publishing services."""

    def __init__(
        self,
        app=None,
    ):
        """Initialize the queue services.
        
        If app is provided, then this is bound to that app instance.
        """
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app=None,
        ):
        """This callback can be used to initialize an application for the
        use with this queue setup.
        """
        # We intentionally don't set self.app = app, to support multiple
        # applications. If the app is passed in the constructor,
        # we set it and don't support multiple applications.

        if not (
            app.config.get('FLASK_PUB_CONFIG')
        ):
            raise RuntimeError(
                'FLASK_PUB_CONFIG needs to be set.'
            )

        app.config.setdefault('FLASK_PUB_DEFAULT_SUBJECT', None)

        self.driver = pubsub.PublisherClient()

        app.extensions[EXTENSION_NAME] = self.driver

        @app.teardown_appcontext
        def shutdown(response_or_exc):
            """Cleanup all state here as part of the Flask shutdown."""

            return response_or_exc
    
    def publish(self,
                msg: Union[str, bytes],
                subject: str = None):

        if not (app := self.app):
                app = current_app
  
        topic_name = subject or app.config.get('FLASK_PUB_DEFAULT_SUBJECT')
        
        if app and topic_name and (_queue := self._get_queue(app)):

            data = msg
            if isinstance(msg, str):
                data = msg.encode("utf8")
            
            future = _queue.publish(subject, data)

    @staticmethod
    def create_subject(
        project: str,
        topic: str,
    ) -> str:
        """Returns a fully-qualified topic string."""
        return "projects/{project}/topics/{topic}".format(
            project=project,
            topic=topic,
        )

    def _get_queue(self, app):
        """Gets the queue for the application"""
        if queue := app.extensions.get(EXTENSION_NAME):
            return queue
        
        raise RuntimeError('The Flask_Pub extension was not registered with the current app.')
