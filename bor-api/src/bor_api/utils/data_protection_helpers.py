
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
"""Manages helper methods for removing visibility of old PROD data that exists in CDEV/CTEST."""
from flask import current_app

from bor_api.models import User
from bor_api.services.bor_solr.fields import EntityRoleField
from bor_api.services.bor_solr.utils import SearchParams


def add_prod_protection_params(params: SearchParams, user: User, has_individual_access: bool) -> SearchParams:
    """Return updated SearchParams for users in dev/test environments to prevent visibility of old PROD data."""
    is_trusted_tester = has_individual_access or user.idp_userid in current_app.config['TRUSTED_TESTER_IDS']
    is_prod = current_app.config['POD_NAMESPACE'] not in ['dev', 'test']
    if is_prod or is_trusted_tester:
        return params

    # Only search over businesses in LEAR or fake generated businesses
    if params.child_categories.get(EntityRoleField.RELATED_LEGAL_TYPE):
        current_app.logger.warn('Overwiting %s param setting to prevent old prod data visibility.',
                                EntityRoleField.RELATED_LEGAL_TYPE)
    params.child_categories[EntityRoleField.RELATED_LEGAL_TYPE] = ['BEN', 'CP', 'SP', 'GP', 'N/A']
    return params
