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
"""Centralized setup of logging for the service."""
from __future__ import annotations

import logging
import logging.config
import sys
from os import path
from typing import Union

from flask import current_app

from search_api.services.flags import Flags

from .base import BaseEnum, auto


def setup_logging(conf):
    """Create the services logger.

    TODO should be reworked to load in the proper loggers and remove others
    """
    # pylint: disable=consider-using-f-string
    # log_file_path = path.join(path.abspath(path.dirname(__file__)), conf)

    if conf and path.isfile(conf):
        logging.config.fileConfig(conf)
        print('Configure logging, from conf:{}'.format(conf), file=sys.stdout)
    else:
        print('Unable to configure logging, attempted conf:{}'.format(conf), file=sys.stderr)


class Level(BaseEnum):
    """Enum for the Business state."""

    CRITICAL = auto()
    DEBUG = auto()
    ERROR = auto()
    INFO = auto()
    WARNING = auto()


def get_logging_flag_name():
    """Get the name of the FFlag to lookup."""
    try:
        return current_app.config.get('OPS_LOGGER_LEVEL')
    except:  # pylint: disable=bare-except; # noqa: E722, B901
        return f'ops-{__name__}-log-level'


def set_log_level_by_flag():
    """Set the logging level if the FF has a different level than what is currently set."""
    try:
        flag_name = get_logging_flag_name()
        flag_value = Flags.value(flag_name, user={'key': flag_name})
        if flag_value and (level_name := logging.getLevelName(logging.getLogger().level)) \
                and flag_value != level_name:  # pylint: disable=E0601; linter hates the walrus
            set_logging_level(flag_value)
    except Exception:  # noqa: B902
        return


def set_logging_level(level: Union(Level, str)):
    """Set the logging level of the top logger."""
    _logger = logging.getLogger()

    match level:
        case Level.CRITICAL:
            _logger.setLevel(logging.CRITICAL)
        case Level.DEBUG:
            _logger.setLevel(logging.DEBUG)
        case Level.ERROR:
            _logger.setLevel(logging.ERROR)
        case Level.INFO:
            _logger.setLevel(logging.INFO)
        case Level.WARNING:
            _logger.setLevel(logging.WARNING)

        case _:
            _logger.setLevel(logging.INFO)
