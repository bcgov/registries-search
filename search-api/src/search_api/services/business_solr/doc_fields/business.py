# Copyright © 2024 Province of British Columbia
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
"""Manages business doc fields."""
from search_api.utils.base import BaseEnum


class BusinessField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the business fields available."""

    # unique key for all docs
    UNIQUE_KEY = 'id'
    # stored fields
    BN = 'bn'
    IDENTIFIER = 'identifier'
    NAME = 'name'
    PARTIES = 'parties'
    STATE = 'status'
    TYPE = 'legalType'
    # query fields
    BN_Q = 'bn_q'
    IDENTIFIER_Q = 'identifier_q'
    NAME_Q = 'name_q'
    NAME_SINGLE = 'name_single_term'
    NAME_STEM_AGRO = 'name_stem_agro'
    NAME_SUGGEST = 'name_suggest'
    NAME_XTRA_Q = 'name_xtra_q'
    GOOD_STANDING = 'goodStanding'
    # common built in across docs
    SCORE = 'score'
