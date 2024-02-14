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
"""Manages entity role doc fields for BOR solr."""
from bor_api.enums.base import BaseEnum


class EntityRoleField(BaseEnum):  # pylint: disable=too-few-public-methods
    """Enum of the entity role fields available in the BOR solr search core."""

    # unique key for all docs
    UNIQUE_KEY = 'id'
    # entity role doc stored fields
    RELATED_BN = 'relatedBN'
    RELATED_EMAIL = 'relatedEmail'
    RELATED_ENTITY_TYPE = 'relatedEntityType'
    RELATED_IDENTIFIER = 'relatedIdentifier'
    RELATED_LEGAL_TYPE = 'relatedLegalType'
    RELATED_INTERESTS = 'relatedInterests'
    RELATED_NAME = 'relatedName'
    RELATED_STATE = 'relatedState'
    ROLE_DATES = 'roleDates'
    ROLE_TYPE = 'roleType'
    # entity role doc query fields
    RELATED_BN_Q = 'relatedBN_q'
    RELATED_EMAIL_Q = 'relatedEmail_q'
    RELATED_IDENTIFIER_Q = 'relatedIdentifier_q'
    RELATED_NAME_Q = 'relatedName_q'
    RELATED_NAME_AGRO_Q = 'relatedName_stem_agro_q'
    RELATED_NAME_SINGLE_Q = 'relatedName_single_term_q'
    RELATED_NAME_SYN_Q = 'relatedName_synonym_q'
    RELATED_Q = 'related_q'
    # common built in across docs
    SCORE = 'score'
