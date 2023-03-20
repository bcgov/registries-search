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
"""Tests to assure the Solr Services."""
from typing import List

from bor_api.services.solr.bor_solr_docs import Address, Entity, EntityName, EntityRole
from bor_api.services.solr.bor_solr_fields import SolrField


def create_solr_doc(name: str,
                    addresses: List[Address] = None,
                    bn: str = None,
                    entityType: str = 'person',
                    identifier: str = None,
                    legal_type: str = None,
                    names: List[EntityName] = None,
                    parties: List[Entity] = None,
                    roles: List[EntityRole] = None,
                    state: str = 'ACTIVE') -> Entity:
    """Create a base entity doc."""
    if not names:
        names = []
    names.append(EntityName(name=name, nameType='primary'))
    return Entity(
        bn=bn,
        entityAddresses=addresses,
        entityType=entityType,
        identifier=identifier,
        legalType=legal_type,
        names=names,
        parties=parties,
        roles=roles,
        state=state
    )
