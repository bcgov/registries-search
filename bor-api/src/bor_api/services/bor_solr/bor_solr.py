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
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField, InterestField


class BorSolr(Solr):
    """Wrapper around the solr instance for BOR."""

    # TODO: split the field lists by access groups once we know who is allowed to see what
    entity_fields: list[str] = [
        EntityField.EMAIL.value, EntityField.ENTITY_ADDRESSES.value,
        EntityField.ENTITY_TYPE.value, EntityField.LEGAL_NAME.value,
        EntityField.ROLES.value, EntityField.SCORE.value, '[child]'
    ]
    entity_extended_fields: list[str] = [
        EntityField.ALT_NAME.value, EntityField.BIRTH_DATE.value, EntityField.EMAIL.value,
        EntityField.IS_PR.value, EntityField.NATIONALITIES.value, EntityField.EXTERNAL_INFLUENCE.value,
        EntityField.TAX_NUMBER.value, EntityField.TAX_RESIDENCIES.value
    ]
    address_fields: list[str] = [
        AddressField.ADDRESS_CITY.value, AddressField.ADDRESS_COUNTRY.value,
        AddressField.ADDRESS_REGION.value, AddressField.ADDRESS_TYPE.value,
        AddressField.POSTAL_CODE.value, AddressField.STREET_ADDRESS.value,
        AddressField.LOCATION_DESC.value
    ]
    entity_role_fields: list[str] = [
        EntityRoleField.RELATED_BN.value, EntityRoleField.RELATED_EMAIL.value,
        EntityRoleField.RELATED_ENTITY_TYPE.value, EntityRoleField.RELATED_IDENTIFIER.value,
        EntityRoleField.RELATED_NAME.value, EntityRoleField.RELATED_STATE.value, EntityRoleField.ROLE_DATES.value,
        EntityRoleField.ROLE_TYPE.value, EntityRoleField.RELATED_LEGAL_TYPE.value
    ]
    entity_role_extended_fields = [EntityRoleField.RELATED_INTERESTS.value]
    date_fields: list[str] = [DateRangeField.ACTIVE.value, DateRangeField.START.value, DateRangeField.END.value]
    interest_fields: list[str] = [
        InterestField.DETAILS.value, InterestField.DIRECT_INDIRECT.value,
        InterestField.OTHER_REASON.value, InterestField.SHARE_EXACT.value,
        InterestField.SHARE_MAX.value, InterestField.SHARE_MIN.value, InterestField.TYPE.value
    ]

    def create_or_replace_docs(self, docs: list[Entity] = None, raw_docs: list[dict] = None, timeout=25, additive=True):
        """Create or replace solr docs in the core."""
        update_list = raw_docs if raw_docs else [asdict(doc) for doc in docs]

        if not additive:
            # add in the set keyword to all roles / addresses / nationalities / tax residencies
            for entity_dict in update_list:
                # addresses
                if addresses := entity_dict.get('entityAddresses', None):
                    entity_dict['entityAddresses'] = {'set': addresses}
                # roles
                if roles := entity_dict.get('roles', None):
                    entity_dict['roles'] = {'set': roles}
                # nationalities
                if nationalities := entity_dict.get('nationalities', None):
                    entity_dict['nationalities'] = {'set': nationalities}
                # tax residencies
                if tax_residencies := entity_dict.get('taxResidencies', None):
                    entity_dict['taxResidencies'] = {'set': tax_residencies}

        url = self.update_url if len(update_list) < 1000 else self.bulk_update_url

        response = self.call_solr('POST', url, json_data=update_list, timeout=timeout)
        return response
