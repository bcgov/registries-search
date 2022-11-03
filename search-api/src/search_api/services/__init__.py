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
"""This module wraps the calls to external services used by the API."""

from .authz import BASIC_USER, SBC_STAFF, STAFF_ROLE, SYSTEM_ROLE, get_role, is_staff
from .document_storage.storage_service import GoogleStorageService
from .flags import Flags
from .queue import GoogleQueueService
from .solr import Solr


flags = Flags()  # pylint: disable=invalid-name; shared variables are lower case by Flask convention.
# TODO: uncomment after testing with running gcp service
# queue = GoogleQueueService()  # pylint: disable=invalid-name; shared variables are lower case by Flask convention.
solr = Solr()  # pylint: disable=invalid-name; shared variables are lower case by Flask convention.
# TODO: uncomment after testing with running gcp service
# storage = GoogleStorageService()  # pylint: disable=invalid-name; shared variables are lower case by Flask convention.
