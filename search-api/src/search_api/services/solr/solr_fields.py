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
"""Manages solr fields for search solr."""
from search_api.utils.base import BaseEnum


class SolrField(BaseEnum):
    """Enum of the fields available in the solr search core."""

    # base doc stored fields
    BN = 'bn'
    IDENTIFIER = 'identifier'
    NAME = 'name'
    PARTIES = 'parties'
    SCORE = 'score'
    STATE = 'status'
    TYPE = 'legalType'

    # child parties doc stored fields
    PARENT_BN = 'parentBN'
    PARENT_IDENTIFIER = 'parentIdentifier'
    PARENT_NAME = 'parentName'
    PARENT_STATE = 'parentStatus'
    PARENT_TYPE = 'parentLegalType'
    PARTY_NAME = 'partyName'
    PARTY_ROLE = 'partyRoles'
    PARTY_TYPE = 'partyType'

    # business query fields
    BN_Q = 'bn_q'
    IDENTIFIER_Q = 'identifier_q'
    NAME_Q = 'name_q'
    NAME_SINGLE = 'name_single_term'
    NAME_STEM_AGRO = 'name_stem_agro'
    NAME_SUGGEST = 'name_suggest'
    # party query fields
    PARTY_NAME_Q = 'partyName_q'
    PARTY_NAME_SINGLE = 'partyName_single_term'
    PARTY_NAME_STEM_AGRO = 'partyName_stem_agro'
    PARTY_NAME_SUGGEST = 'partyName_suggest'
    PARENT_NAME_Q = 'parentName_q'
    PARENT_NAME_SINGLE = 'parentName_single_term'
    PARENT_NAME_STEM_AGRO = 'parentName_stem_agro'
    PARENT_BN_Q = 'parentBN_q'
    PARENT_IDENTIFIER_Q = 'parentIdentifier_q'
