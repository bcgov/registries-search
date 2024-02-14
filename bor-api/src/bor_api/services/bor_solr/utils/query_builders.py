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
"""Manages common solr query building methods."""
import re

from bor_api.enums import SolrSynonymType
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField
from bor_api.services.solr.utils.formatting_helpers import prep_query_str


IDENTIFIER_FIELDS: list[str] = [EntityField.IDENTIFIER_Q.value, EntityRoleField.RELATED_IDENTIFIER_Q.value,
                                EntityRoleField.RELATED_Q.value]
PRE_CHILD_FILTER_CLAUSE = "{!parent which = '-_nest_path_:* " + EntityField.ENTITY_TYPE.value + ":*'}"
FIELD_SYNONYM_TYPE_MAP = {
    AddressField.ADDRESS_SYN_Q: SolrSynonymType.ADDRESS,
    EntityField.LEGAL_NAME_SYN_Q: SolrSynonymType.NAME,
    EntityRoleField.RELATED_NAME_SYN_Q: SolrSynonymType.NAME
}


def _get_terms(query: dict[str, str]) -> tuple[list[str], list[str]]:
    """Return the terms and email_terms."""
    terms = query['value'].split()
    raw_email_terms = query['email_value'].split()

    if len(terms) == len(raw_email_terms):
        return terms, raw_email_terms

    email_terms = []
    term_index = 0
    email_term_index = 0
    long_email_term_words = []
    long_email_term_found = False

    while term_index < len(terms):
        if long_email_term_found:
            email_terms.append(raw_email_terms[email_term_index])
            # remove the first appearance of terms[term_index] from the long_email_term_words list
            if terms[term_index] in long_email_term_words:
                long_email_term_words.remove(terms[term_index])
            # if long_email_term_words is empty, set long_email_term_found to False and increment email_term_index
            if not long_email_term_words:
                long_email_term_found = False
                email_term_index += 1
            term_index += 1
        elif terms[term_index] == raw_email_terms[email_term_index]:
            email_terms.append(raw_email_terms[email_term_index])
            email_term_index += 1
            term_index += 1
        else:
            long_email_term_found = True
            long_email_term_words = prep_query_str(raw_email_terms[email_term_index]).split()

    return terms, email_terms


def _add_identifier(field: str, term: str, is_child=False) -> str:
    """Return a special identifier query."""
    corp_prefix_regex = r'(^[aA-zZ]+)[0-9]+$'
    identifier_field = EntityField.IDENTIFIER_Q.value
    if field in IDENTIFIER_FIELDS and (identifier := re.search(corp_prefix_regex, term)):
        prefix = identifier.group(1)
        new_term = term.replace(prefix, '', 1)
        if is_child:
            field = PRE_CHILD_FILTER_CLAUSE + field
            identifier_field = PRE_CHILD_FILTER_CLAUSE + EntityRoleField.RELATED_IDENTIFIER_Q.value

        return f'({field}:"{new_term}" AND {identifier_field}:"{prefix.upper()}")'
    if is_child:
        field = PRE_CHILD_FILTER_CLAUSE + field

    return f'{field}:{term}'


def _get_fuzzy_str(term: str, short: int, long: int) -> str:
    """Return the fuzzy string for the term."""
    if len(term) < 4:
        return ''
    if len(term) < 7:
        return f'~{short}'
    return f'~{long}'


def _find_synonym_terms(start_term: str,
                        start_term_index: int,
                        terms: list[str],
                        field: AddressField | EntityField | EntityRoleField) -> list[str]:
    """Return the synonym terms that match the starting term and following query terms."""
    from bor_api.models import SolrSynonymList  # pylint: disable=import-outside-toplevel;

    # the best match will be the one with the most words (i.e. british columbia > british)
    best_synonym_match_terms = []
    # check if term exists inside a synonym
    if synonyms := SolrSynonymList.find_all_beginning_with_phrase(start_term, FIELD_SYNONYM_TYPE_MAP[field]):
        for synonym_terms in [syn.synonym.split() for syn in synonyms]:
            if len(synonym_terms) > len(terms[start_term_index:]) or len(synonym_terms) == 0:
                # not possible to be this synonym
                continue
            if len(synonym_terms) < len(best_synonym_match_terms):
                # this is a shorter synonym than one thats already matched so skip
                continue

            # see if all terms of the synonym are in the query
            full_synonym_in_query = True
            for i, synonym_term in enumerate(synonym_terms):
                if terms[start_term_index + i].lower() != synonym_term.lower():
                    full_synonym_in_query = False
                    break
            if full_synonym_in_query:
                best_synonym_match_terms = synonym_terms

    return best_synonym_match_terms


def _update_clause(current_clause: str, new_clause: str, join_str: str):
    """Return the current clause added with the new clause."""
    if current_clause:
        current_clause += f' {join_str} '
    return current_clause + new_clause


def build_child_query(child_query: dict[str, str]) -> str | None:
    """Return the child query fq."""
    # add filter clauses for child query items
    child_q = ''
    for key in child_query:
        if not child_query[key]:
            continue

        terms = child_query[key].split()
        if not child_q:
            child_q = _add_identifier(key, terms[0], True)
        else:
            child_q += f' AND {_add_identifier(key, terms[0], True)}'

        for term in terms[1:]:
            child_q += f' AND {_add_identifier(key, term, True)}'

    if not child_q:
        return None

    return f'({child_q})'


def build_facet(field: AddressField | EntityField | EntityRoleField, is_nested: bool) -> dict[str, dict]:
    """Return the facet dict for the field."""
    facet = {field.value: {'type': 'terms', 'field': field.value}}
    if is_nested:
        facet[field.value]['domain'] = {'blockChildren': '{!v=$parents}'}
        facet[field.value]['facet'] = {'by_parent': 'uniqueBlock({!v=$parents})'}

    return facet


def build_facet_query(field: AddressField | EntityField | EntityRoleField,
                      values: list[str], is_nested: bool = False) -> str:
    """Return the facet filter clause for the given params."""
    filter_q = f'{field.value}:("{values[0]}"'
    if is_nested:
        filter_q = PRE_CHILD_FILTER_CLAUSE + f'{field.value}:"{values[0]}"'
    for val in values[1:]:
        if is_nested:
            filter_q += f' OR {field.value}: "{val}"'
        else:
            filter_q += f' OR "{val}"'
    if not is_nested:
        filter_q += ')'
    return filter_q


def build_base_query(query: dict[str, str],  # pylint: disable=too-many-arguments,too-many-branches
                     fields: list[AddressField | EntityField | EntityRoleField | DateRangeField],
                     nested_fields: list[AddressField | EntityField | EntityRoleField | DateRangeField],
                     boost_fields: dict[AddressField | EntityField | EntityRoleField, int],
                     fuzzy_fields: dict[AddressField | EntityField | EntityRoleField, dict[str, int]],
                     synonym_fields: dict[AddressField | EntityField | EntityRoleField, str]) -> dict[str, list[str]]:
    """Return a solr query with filters for each subsequent term."""
    terms, email_terms = _get_terms(query)

    synonym_info = {}
    for syn_field in synonym_fields:
        synonym_info[syn_field] = {'synonym_terms': [], 'synonym_start_index': None}
    query_clause = ''
    for term_index, term in enumerate(terms):
        # each term only needs to match one of the given fields, but all terms must match at least 1
        term_clause = ''
        for field in fields:
            field_clause = _add_identifier(field.value, term)
            pre_boost_clause = field_clause
            # add boost
            if field in boost_fields:
                field_clause += f'^{boost_fields[field]}'

            term_clause = _update_clause(term_clause, field_clause, 'OR')
            # add fuzzy matching
            if field in fuzzy_fields and (fuzzy_str := _get_fuzzy_str(term,
                                                                      fuzzy_fields[field]['short'],
                                                                      fuzzy_fields[field]['long'])):
                # add another with fuzzy (this one will give a lower score on a hit if the original has a boost)
                term_clause = _update_clause(term_clause, f'{pre_boost_clause}{fuzzy_str}', 'OR')

        # add nested field clauses
        for nested_field in nested_fields:
            nested_field_clause = build_child_query({nested_field.value: term})
            if nested_field in fuzzy_fields and (fuzzy_str := _get_fuzzy_str(term,
                                                                             fuzzy_fields[nested_field]['short'],
                                                                             fuzzy_fields[nested_field]['long'])):
                # add fuzzy match chars before ending bracket
                nested_field_clause = f'{nested_field_clause[:-1]}{fuzzy_str})'

            term_clause = _update_clause(term_clause, nested_field_clause, 'OR')

        # add synonym field clauses
        for field in synonym_fields:
            synonym_terms = synonym_info[field]['synonym_terms']
            synonym_start_index = synonym_info[field]['synonym_start_index']
            field_value = field.value
            if synonym_fields[field] == 'child':
                field_value = PRE_CHILD_FILTER_CLAUSE + field.value
            synonym_clause = ''
            if synonym_terms and term_index < synonym_start_index + len(synonym_terms):
                # a synonym matched on a previous term and includes the current term (multi word synonym)
                synonym_clause = f"{field_value}:{' '.join(synonym_terms)}"
            elif new_synonym_terms := _find_synonym_terms(term, term_index, terms, field):
                synonym_info[field]['synonym_terms'] = new_synonym_terms
                synonym_info[field]['synonym_start_index'] = term_index
                synonym_clause = f"{field_value}:{' '.join(new_synonym_terms)}"

            if synonym_clause:
                term_clause = _update_clause(term_clause, f'({synonym_clause})', 'OR')

        # add special nested clause for related email
        nested_email_field_clause = build_child_query({EntityRoleField.RELATED_EMAIL_Q.value: email_terms[term_index]})
        # Add fuzzy matching for email if desired
        if EntityRoleField.RELATED_EMAIL_Q in fuzzy_fields and (
            fuzzy_str := _get_fuzzy_str(email_terms[term_index],
                                        fuzzy_fields[EntityRoleField.RELATED_EMAIL_Q]['short'],
                                        fuzzy_fields[EntityRoleField.RELATED_EMAIL_Q]['long'])):
            # add fuzzy match chars before ending bracket
            nested_email_field_clause = f'{nested_email_field_clause[:-1]}{fuzzy_str})'
        term_clause = _update_clause(term_clause, f'({nested_email_field_clause})', 'OR')

        query_clause = _update_clause(query_clause, f'({term_clause})', 'AND')

    # extra filters
    filters = []
    for key in query:
        if key in ['value', 'email_value'] or not query[key]:
            continue
        terms = query[key].split()
        for term in terms:
            filters.append(_add_identifier(key, term))

    return {'query': query_clause, 'filter': filters}
