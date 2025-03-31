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
from bor_api.services.bor_solr.fields import EntityField


class BorSolr(Solr):
    """Wrapper around the solr instance for BOR."""

    def create_or_replace_docs(self, docs: list[Entity] | None = None, raw_docs: list[dict] | None = None, timeout=25, additive=True):
        """Create or replace solr docs in the core."""
        update_list = raw_docs if raw_docs else [asdict(doc) for doc in docs]

        if not additive and not raw_docs:
            # add in the set keyword to all roles / addresses / nationalities / tax residencies
            for entity_dict in update_list:
                # addresses
                if addresses := entity_dict.get(EntityField.ENTITY_ADDRESSES.value, None):
                    entity_dict[EntityField.ENTITY_ADDRESSES.value] = {"set": addresses}
                # roles
                if roles := entity_dict.get(EntityField.ROLES.value, None):
                    entity_dict[EntityField.ROLES.value] = {"set": roles}
                # nationalities
                if nationalities := entity_dict.get(EntityField.NATIONALITIES.value, None):
                    entity_dict[EntityField.NATIONALITIES.value] = {"set": nationalities}
                # tax residencies
                if tax_residencies := entity_dict.get(EntityField.TAX_RESIDENCIES.value, None):
                    entity_dict[EntityField.TAX_RESIDENCIES.value] = {"set": tax_residencies}

        url = self.update_url if len(update_list) < 1000 else self.bulk_update_url  # noqa: PLR2004

        response = self.call_solr("POST", url, json_data=update_list, timeout=timeout)
        return response
