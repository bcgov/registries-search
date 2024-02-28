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
"""Manages bor solr class."""
from dataclasses import asdict

from bor_api.services.base_solr import Solr
from bor_api.services.bor_solr.doc_models import Entity
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField


class BorSolr(Solr):
    """Wrapper around the solr instance for BOR."""

    entity_fields: list[str] = [
        EntityField.BN.value, EntityField.EMAIL.value, EntityField.ENTITY_ADDRESSES.value,
        EntityField.ENTITY_TYPE.value, EntityField.IDENTIFIER.value, EntityField.LEGAL_NAME.value,
        EntityField.LEGAL_TYPE.value, EntityField.ROLES.value,
        EntityField.STATE.value, EntityField.SCORE.value, '[child]'
    ]
    address_fields: list[str] = [
        AddressField.ADDRESS_CITY.value, AddressField.ADDRESS_COUNTRY.value,
        AddressField.ADDRESS_REGION.value, AddressField.ADDRESS_TYPE.value,
        AddressField.POSTAL_CODE.value, AddressField.STREET_ADDRESS.value
    ]
    entity_role_fields: list[str] = [
        EntityRoleField.RELATED_BN.value, EntityRoleField.RELATED_EMAIL.value,
        EntityRoleField.RELATED_ENTITY_TYPE.value, EntityRoleField.RELATED_IDENTIFIER.value,
        EntityRoleField.RELATED_NAME.value, EntityRoleField.RELATED_STATE.value, EntityRoleField.ROLE_DATES.value,
        EntityRoleField.ROLE_TYPE.value, EntityRoleField.RELATED_LEGAL_TYPE.value
    ]
    date_fields: list[str] = [DateRangeField.ACTIVE.value, DateRangeField.START.value, DateRangeField.END.value]

    def create_or_replace_docs(self, docs: list[Entity], timeout=25, additive=True):
        """Create or replace solr docs in the core."""
        update_list = [asdict(doc) for doc in docs]
        if not additive:
            # add in the set keyword to all roles / addresses / nationalities / tax residencies
            for entity_dict in update_list:
                # addresses
                addresses = entity_dict.get('entityAddresses', [])
                entity_dict['entityAddresses'] = {'set': addresses}
                # roles
                roles = entity_dict.get('roles', [])
                entity_dict['roles'] = {'set': roles}
                # nationalities
                nationalities = entity_dict.get('nationalities', [])
                entity_dict['nationalities'] = {'set': nationalities}
                # tax residencies
                tax_residencies = entity_dict.get('taxResidencies', [])
                entity_dict['taxResidencies'] = {'set': tax_residencies}

        response = self.call_solr('POST', self.update_url, json_data=update_list, timeout=timeout)
        return response
