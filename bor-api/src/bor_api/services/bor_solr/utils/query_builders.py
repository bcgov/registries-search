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
from bor_api.services.bor_solr.fields import AddressField, DateRangeField, EntityField, EntityRoleField, InterestField

IDENTIFIER_FIELD_VALUES: list[str] = [
    EntityField.IDENTIFIER_Q.value,
    EntityRoleField.RELATED_IDENTIFIER_Q.value,
    EntityRoleField.RELATED_Q.value,
]

PRE_CHILD_FILTER_CLAUSE = "{!parent which = '-_nest_path_:* " + EntityField.ENTITY_TYPE.value + ":*'}"

FIELD_SYNONYM_TYPE_MAP = {
    AddressField.ADDRESS_SYN_Q: SolrSynonymType.ADDRESS,
    EntityField.ALT_NAME_SYN_Q: SolrSynonymType.NAME,
    EntityField.LEGAL_NAME_SYN_Q: SolrSynonymType.NAME,
    EntityRoleField.RELATED_NAME_SYN_Q: SolrSynonymType.NAME,
}


def _create_clause(field_value: str, term: str, is_child=False) -> str:
    """Return the query clause for the field and term."""
    corp_prefix_regex = r"(^[aA-zZ]+)[0-9]+$"

    search_field = field_value
    if is_child:
        search_field = PRE_CHILD_FILTER_CLAUSE + search_field

    if field_value in IDENTIFIER_FIELD_VALUES and (identifier := re.search(corp_prefix_regex, term)):
        prefix = identifier.group(1)
        no_prefix_term = term.replace(prefix, "", 1)

        return f'({search_field}:"{no_prefix_term}" AND {search_field}:"{prefix.upper()}")'

    return f"{search_field}:{term}"


def _get_fuzzy_str(term: str, short: int, long: int) -> str:
    """Return the fuzzy string for the term."""
    if len(term) < 4:  # noqa: PLR2004
        return ""
    if len(term) < 7:  # noqa: PLR2004
        return f"~{short}"
    return f"~{long}"


def _get_filters(query: dict[str, str]) -> list[str]:
    """Return the filters for the query."""
    filters = []
    for key, value in query.items():
        if key in ["value"] or not value:
            continue
        terms = value.split()
        for term in terms:
            filters.append(_create_clause(key, term))
    return filters


def _get_base_term_clause(
    term: str,
    fields: dict[AddressField | EntityField | EntityRoleField | DateRangeField, str],
    boost_fields: dict[AddressField | EntityField | EntityRoleField, int],
    fuzzy_fields: dict[AddressField | EntityField | EntityRoleField, dict[str, int]],
) -> str:
    """Return the base term clause."""
    term_clause = ""
    for field, level in fields.items():
        field_clause = _create_clause(field.value, term, level == "child")
        pre_boost_clause = field_clause
        # add boost
        if field in boost_fields:
            field_clause += f"^{boost_fields[field]}"

        term_clause = _join_clause(term_clause, field_clause, "OR")
        # add fuzzy matching
        if field in fuzzy_fields and (
            fuzzy_str := _get_fuzzy_str(term, fuzzy_fields[field]["short"], fuzzy_fields[field]["long"])
        ):
            # add another with fuzzy (this one will give a lower score on a hit if the original has a boost)
            term_clause = _join_clause(term_clause, f"{pre_boost_clause}{fuzzy_str}", "OR")
    return term_clause


def _find_synonym_terms(
    start_term: str, start_term_index: int, terms: list[str], field: AddressField | EntityField | EntityRoleField
) -> list[str]:
    """Return the synonym terms that match the starting term and following query terms."""
    from bor_api.models import SolrSynonymList

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


def _join_clause(current_clause: str, new_clause: str, join_str: str):
    """Return the current clause added with the new clause."""
    if current_clause:
        current_clause += f" {join_str} "
    return current_clause + new_clause


def _join_synonym_clauses(
    term_clause: str,
    terms: list[str],
    term_index: int,
    synonym_info: dict,
    synonym_fields: dict[AddressField | EntityField | EntityRoleField, str],
):
    """Return the term clause with the added synonym clauses."""
    term = terms[term_index]
    for field, level in synonym_fields.items():
        if not synonym_info.get(field):
            synonym_info[field] = {"synonym_terms": [], "synonym_start_index": None}
        synonym_terms = synonym_info[field]["synonym_terms"]
        synonym_start_index = synonym_info[field]["synonym_start_index"]
        field_value = field.value
        if level == "child":
            field_value = PRE_CHILD_FILTER_CLAUSE + field.value
        synonym_clause = ""
        if synonym_terms and term_index < synonym_start_index + len(synonym_terms):
            # a synonym matched on a previous term and includes the current term (multi word synonym)
            synonym_clause = f"{field_value}:{' '.join(synonym_terms)}"
        elif new_synonym_terms := _find_synonym_terms(term, term_index, terms, field):
            synonym_info[field]["synonym_terms"] = new_synonym_terms
            synonym_info[field]["synonym_start_index"] = term_index
            synonym_clause = f"{field_value}:{' '.join(new_synonym_terms)}"

        if synonym_clause:
            term_clause = _join_clause(term_clause, f"({synonym_clause})", "OR")

    return term_clause


def build_child_query(child_query: dict[str, str]) -> str | None:
    """Return the child query fq."""
    # add filter clauses for child query items
    child_q = ""
    for key, value in child_query.items():
        if not value:
            continue

        terms = value.split()
        if not child_q:
            child_q = _create_clause(key, terms[0], True)
        else:
            child_q += f" AND {_create_clause(key, terms[0], True)}"

        for term in terms[1:]:
            child_q += f" AND {_create_clause(key, term, True)}"

    if not child_q:
        return None

    return f"({child_q})"


def build_facet(field: AddressField | EntityField | EntityRoleField, is_nested: bool) -> dict[str, dict]:
    """Return the facet dict for the field."""
    facet = {field.value: {"type": "terms", "field": field.value}}
    if is_nested:
        facet[field.value]["domain"] = {"blockChildren": "{!v=$parents}"}
        facet[field.value]["facet"] = {"by_parent": "uniqueBlock({!v=$parents})"}

    return facet


def build_facet_query(
    field: AddressField | EntityField | EntityRoleField | InterestField, values: list[str], is_nested: bool = False
) -> str:
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
        filter_q += ")"
    return filter_q


def build_base_query(
    query: dict[str, str],
    fields: dict[AddressField | EntityField | EntityRoleField | DateRangeField, str],
    boost_fields: dict[AddressField | EntityField | EntityRoleField, int],
    fuzzy_fields: dict[AddressField | EntityField | EntityRoleField, dict[str, int]],
    synonym_fields: dict[AddressField | EntityField | EntityRoleField, str],
) -> dict[str, list[str]]:
    """Return a solr query with filters for each subsequent term."""
    terms = query["value"].split()
    synonym_info = {}
    query_clause = ""
    # Each term in the searched 'value' must match on at least one of:
    # 'fields', 'fuzzy_fields' or 'synonym_fields' query clauses.
    # This loop adds clauses for the all the given fields for each term
    for term_index, term in enumerate(terms):
        # Get the base clause, which references the fields, fuzzy fields and adds the boost clause for ordering
        term_clause = _get_base_term_clause(term, fields, boost_fields, fuzzy_fields)

        # Add the synonym field clauses
        term_clause = _join_synonym_clauses(term_clause, terms, term_index, synonym_info, synonym_fields)

        # Join the term clause to the full query
        query_clause = _join_clause(query_clause, f"({term_clause})", "AND")

    # Add extra filters if applicable
    filters = _get_filters(query)

    if not query_clause:
        # handle empty string provided for query value
        query_clause = '""'

    return {"query": query_clause, "filter": filters}
