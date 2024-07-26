# Copyright © 2022 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Business suggest methods."""
from search_api.services.business_solr import BusinessSolr
from search_api.services.business_solr.doc_fields import BusinessField


def business_suggest(query: str, solr: BusinessSolr, rows = 5) -> list:
    """Return the list of business suggestions from Solr from given text."""

    # 1st solr query (names)
    name_suggestions = solr.suggest(query, rows, True)
    print(name_suggestions)
    # 2nd solr query (extra names)
    extra_name_suggestions = []
    if len(name_suggestions) < rows:
        name_select_payload = solr.query_builder.build_base_query({'value': query}, {BusinessField.NAME_SINGLE: 'parent'}, {}, {})
        name_select_payload['fields'] = solr.business_fields
        print(name_select_payload)
        name_docs = solr.query(name_select_payload, rows).get('response', {}).get('docs', [])
        extra_name_suggestions = [x.get(BusinessField.NAME.value).upper() for x in name_docs if x.get(BusinessField.NAME.value)]
    # remove dups
    name_suggestions = name_suggestions + list(set(extra_name_suggestions) - set(name_suggestions))
    query = query.upper()  # NOTE: needed for bn/identifier processing too

    # 3rd solr query (bns + identifiers)
    identifier_suggestions = []
    bn_suggestions = []
    if len(name_suggestions) < rows:
        bn_id_payload = {
            'query': f'{BusinessField.IDENTIFIER_Q.value}:{query} OR {BusinessField.BN_Q.value}:{query}',
            'fields': solr.business_fields}
        bn_id_docs = solr.query(bn_id_payload, 0, rows).get('response', {}).get('docs', [])

        identifier_suggestions = [
            x.get(BusinessField.IDENTIFIER.value) for x in bn_id_docs if query in x.get(BusinessField.IDENTIFIER.value)]
        bn_suggestions = [
            x.get(BusinessField.BN.value) for x in bn_id_docs
            if x.get(BusinessField.BN.value) and query in x.get(BusinessField.BN.value, '')]

    # format/combine response
    suggestions = [{'type': BusinessField.NAME.value, 'value': x} for x in name_suggestions]
    suggestions += [{'type': BusinessField.IDENTIFIER.value, 'value': x} for x in identifier_suggestions]
    suggestions += [{'type': BusinessField.BN.value, 'value': x} for x in bn_suggestions]
    return suggestions[:rows]
