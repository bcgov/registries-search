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

from bor_api.models import SolrSynonymList
from bor_api.services.solr.bor_solr_fields import SolrField as Field


IDENTIFIER_FIELDS: list[str] = [Field.IDENTIFIER_Q.value, Field.RELATED_IDENTIFIER_Q.value, Field.RELATED_Q.value]
PRE_CHILD_FILTER_CLAUSE = "{!parent which = '-_nest_path_:* " + Field.ENTITY_TYPE.value + ":*'}"


def _add_identifier(field: str, term: str, is_child=False) -> str:
    """Return a special identifier query."""
    corp_prefix_regex = r'(^[aA-zZ]+)[0-9]+$'
    identifier_field = Field.IDENTIFIER_Q.value
    if field in IDENTIFIER_FIELDS and (identifier := re.search(corp_prefix_regex, term)):
        prefix = identifier.group(1)
        new_term = term.replace(prefix, '', 1)
        if is_child:
            field = PRE_CHILD_FILTER_CLAUSE + field
            identifier_field = PRE_CHILD_FILTER_CLAUSE + Field.RELATED_IDENTIFIER_Q.value

        return f'({field}:"{new_term}" AND {identifier_field}:"{prefix.upper()}")'
    if is_child:
        field = PRE_CHILD_FILTER_CLAUSE + field

    return f'{field}:{term}'


def _find_synonym_terms(start_term: str, start_term_index: int, terms: list[str]) -> list[str]:
    """Return the synonym terms that match the starting term and following query terms."""
    # the best match will be the one with the most words (i.e. british columbia > british)
    best_synonym_match_terms = []
    # check if term exists inside a synonym
    if synonyms := SolrSynonymList.find_all_beginning_with_phrase(start_term):
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


def build_facet(field: Field, is_nested: bool) -> dict[str, dict]:
    """Return the facet dict for the field."""
    facet = {field.value: {'type': 'terms', 'field': field.value}}
    if is_nested:
        facet[field.value]['domain'] = {'blockChildren': '{!v=$parents}'}
        facet[field.value]['facet'] = {'by_parent': 'uniqueBlock({!v=$parents})'}

    return facet


def build_facet_query(field: Field, values: list[str], is_nested: bool = False) -> str:
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
                     fields: list[Field],
                     nested_fields: list[Field],
                     boost_fields: dict[Field, int],
                     fuzzy_fields: dict[Field, dict[str, int]],
                     synonym_fields: dict[Field, str]) -> dict[str, list[str]]:
    """Return a solr query with filters for each subsequent term."""
    terms = query['value'].split()
    synonym_terms = []
    synonym_start_index = None
    query_str = ''
    for term_index, term in enumerate(terms):
        # each term only needs to match one of the given fields, but all terms must match at least 1
        term_str = ''
        for field in fields:
            field_str = _add_identifier(field.value, term)
            # fuzzy_str used later (need it without boost)
            fuzzy_str = field_str
            # add boost
            if field in boost_fields:
                field_str += f'^{boost_fields[field]}'
            if term_str:
                term_str += ' OR '
            term_str += field_str
            # add fuzzy matching
            if field in fuzzy_fields and len(term) > 3:
                # add another with fuzzy (this one will give a lower score on a hit if the original has a boost)
                if len(term) < 7:
                    fuzzy_str += f"~{fuzzy_fields[field]['short']}"
                else:
                    fuzzy_str += f"~{fuzzy_fields[field]['long']}"
                term_str += f' OR {fuzzy_str}'

        # add nested field clauses
        for nested_field in nested_fields:
            nested_field_str = build_child_query({nested_field.value: term})
            if nested_field in fuzzy_fields and len(term) > 3:
                # add fuzzy match chars before ending bracket
                if len(term) < 7:
                    nested_field_str = f"{nested_field_str[:-1]}~{fuzzy_fields[nested_field]['short']})"
                else:
                    nested_field_str = f"{nested_field_str[:-1]}~{fuzzy_fields[nested_field]['long']})"

            if term_str:
                term_str += ' OR '
            term_str += nested_field_str

        # add synonym field clauses
        for field in synonym_fields:
            field_value = field.value
            if synonym_fields[field] == 'child':
                field_value = PRE_CHILD_FILTER_CLAUSE + field.value
            synonym_str = ''
            if synonym_terms and term_index < synonym_start_index + len(synonym_terms):
                # a synonym matched on a previous term and includes the current term (multi word synonym)
                synonym_str = f"{field_value}:{' '.join(synonym_terms)}"
            elif synonym_terms := _find_synonym_terms(term, term_index, terms):
                synonym_start_index = term_index
                synonym_str = f"{field_value}:{' '.join(synonym_terms)}"

            if synonym_str:
                # add synonym clause to query
                if term_str:
                    term_str += ' OR '
                term_str += f'({synonym_str})'

        if query_str:
            query_str += ' AND '
        query_str += f'({term_str})'

    # extra filters
    filters = []
    for key in query:
        if key == 'value' or not query[key]:
            continue
        terms = query[key].split()
        for term in terms:
            filters.append(_add_identifier(key, term))

    return {'query': query_str, 'filter': filters}
