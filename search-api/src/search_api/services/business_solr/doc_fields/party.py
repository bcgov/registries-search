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
"""Manages party doc fields."""
from search_api.utils.base import BaseEnum


class PartyField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the party fields available."""

    # unique key for all docs
    UNIQUE_KEY = "id"
    # stored fields
    PARENT_BN = "parentBN"
    PARENT_IDENTIFIER = "parentIdentifier"
    PARENT_NAME = "parentName"
    PARENT_STATE = "parentStatus"
    PARENT_TYPE = "parentLegalType"
    PARTY_NAME = "partyName"
    PARTY_ROLE = "partyRoles"
    PARTY_TYPE = "partyType"
    # query fields
    PARTY_NAME_Q = "partyName_q"
    PARTY_NAME_SINGLE = "partyName_single_term"
    PARTY_NAME_STEM_AGRO = "partyName_stem_agro"
    PARTY_NAME_XTRA_Q = "partyName_xtra_q"
    PARENT_NAME_SINGLE = "parentName_single_term"
    PARENT_BN_Q = "parentBN_q"
    PARENT_IDENTIFIER_Q = "parentIdentifier_q"
    # common built in across docs
    SCORE = "score"
