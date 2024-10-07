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
"""Handles the Document Access Request updates."""
from search_api.models import DocumentAccessRequest
from search_api.models.errors import DbRowNotFound


def update_document_access_request_status_by_id(dar_id: int, status: str):
    dar = DocumentAccessRequest.find_by_id(dar_id)

    if not dar:
        raise DbRowNotFound()

    dar.status = status
    dar.save()
