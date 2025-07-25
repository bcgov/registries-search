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
"""This module wraps the solr classes/fields for using registries search solr."""
from dataclasses import asdict

from flask import Flask

from search_api.services.base_solr import Solr
from search_api.services.base_solr.utils import QueryBuilder, prep_query_str

from .doc_fields import BusinessField, PartyField
from .doc_models import BusinessDoc


class BusinessSolr(Solr):
    """Wrapper around the solr instance."""

    def __init__(self, config_prefix: str, app: Flask = None) -> None:
        super().__init__(config_prefix, app)
        self.query_builder = QueryBuilder(
            identifier_field_values=[BusinessField.IDENTIFIER.value, BusinessField.IDENTIFIER_Q.value],
            unique_parent_field=BusinessField.IDENTIFIER)

        # fields
        self.business_fields = [
            BusinessField.BN.value, BusinessField.IDENTIFIER.value, BusinessField.NAME.value,
            BusinessField.STATE.value, BusinessField.TYPE.value, BusinessField.GOOD_STANDING.value,
            BusinessField.MODERNIZED.value, BusinessField.SCORE.value
        ]
        self.business_with_parties_fields = [
            BusinessField.BN.value, BusinessField.IDENTIFIER.value, BusinessField.NAME.value,
            BusinessField.STATE.value, BusinessField.TYPE.value, BusinessField.GOOD_STANDING.value,
            BusinessField.PARTIES.value, BusinessField.MODERNIZED.value, "[child]", BusinessField.SCORE.value,
            PartyField.PARTY_NAME.value, PartyField.PARTY_ROLE.value, PartyField.PARTY_TYPE.value
        ]
        self.party_fields = [
            PartyField.PARENT_BN.value, PartyField.PARENT_IDENTIFIER.value,
            PartyField.PARENT_NAME.value, PartyField.PARENT_STATE.value, PartyField.PARENT_TYPE.value,
            PartyField.PARTY_NAME.value, PartyField.PARTY_ROLE.value, PartyField.PARTY_TYPE.value
        ]

    def create_or_replace_docs(self,
                               docs: list[BusinessDoc] | None = None,
                               raw_docs: list[dict] | None = None,
                               timeout=25,
                               additive=True):
        """Create or replace solr docs in the core."""
        update_list = raw_docs if raw_docs else [asdict(doc) for doc in docs]

        if not additive and not raw_docs:
            for business_dict in update_list:
                # parties
                if parties := business_dict.get(BusinessField.PARTIES.value, None):
                    business_dict[BusinessField.PARTIES.value] = {"set": parties}

        url = self.update_url if len(update_list) < 1000 else self.bulk_update_url  # noqa: PLR2004
        return self.call_solr("POST", url, json_data=update_list, timeout=timeout)

    @staticmethod
    def get_business_search_full_query_boost(query_value: str):
        """Return the list of full query boost information intended for business search."""
        full_query_boosts = [
            {
                "field": BusinessField.NAME_Q_EXACT,
                "value": prep_query_str(query_value),
                "boost": "3",
            },
            {
                "field": BusinessField.NAME_SINGLE,
                "value": prep_query_str(query_value),
                "boost": "2",
            },
            {
                "field": BusinessField.NAME_Q,
                "value": prep_query_str(query_value),
                "boost": "5",
                "fuzzy": "5"
            },
            {
                "field": BusinessField.NAME_STEM_AGRO,
                "value": prep_query_str(query_value),
                "boost": "3",
                "fuzzy": "10"
            },
            {
                "field": BusinessField.IDENTIFIER_Q_EDGE,
                "value": prep_query_str(query_value),
                "boost": "10",
            }
        ]
        # add more boost clauses if a dash is in the query
        if "-" in query_value:
            full_query_boosts += [
                {
                    "field": BusinessField.NAME_Q,
                    "value": prep_query_str(query_value, "remove"),
                    "boost": "3",
                    "fuzzy": "5"
                },
                {
                    "field": BusinessField.NAME_Q,
                    "value": prep_query_str(query_value, "pad"),
                    "boost": "7",
                    "fuzzy": "5"
                },
                {
                    "field": BusinessField.NAME_Q,
                    "value": prep_query_str(query_value, "tighten"),
                    "boost": "7",
                    "fuzzy": "5"
                },
                {
                    "field": BusinessField.NAME_Q,
                    "value": prep_query_str(query_value, "tighten-remove"),
                    "boost": "3",
                    "fuzzy": "5"
                }
            ]
        return full_query_boosts
