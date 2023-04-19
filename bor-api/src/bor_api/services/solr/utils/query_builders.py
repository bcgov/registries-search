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
"""Manages solr class for using search solr."""
import re

from bor_api.services.solr.bor_solr_fields import SolrField as Field


IDENTIFIER_FIELDS = [Field.IDENTIFIER_Q, Field.RELATED_IDENTIFIER_Q]
PRE_CHILD_FILTER_CLAUSE = "{!parent which = '-_nest_path_:* " + Field.ENTITY_TYPE.value + ":*'}"


def _add_identifier(field: str, term: str):
    """Return a special identifier query."""
    corp_prefix_regex = r'(^[aA-zZ]+)[0-9]+$'
    if field in IDENTIFIER_FIELDS and (identifier := re.search(corp_prefix_regex, term)):
        prefix = identifier.group(1)
        new_term = term.replace(prefix, '', 1)
        return f'({field}:"{new_term}" AND {field}:"{prefix.upper()}")'
    return f'{field}:{term}'


def build_child_query(child_query: dict[str, str]) -> str | None:
    """Return the child query fq."""
    # add filter clauses for child query items
    child_q = ''
    for key in child_query:
        if not child_query[key]:
            continue
        terms = child_query[key].split()
        if not child_q:
            child_q = f'{PRE_CHILD_FILTER_CLAUSE}{key}:{terms[0]}'
        else:
            child_q += f' AND {PRE_CHILD_FILTER_CLAUSE}{key}:{terms[0]}'

        for term in terms[1:]:
            child_q += f' AND {PRE_CHILD_FILTER_CLAUSE}{key}:{term}'
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


def build_base_query(query: dict[str, str],
                     fields: list[Field],
                     boost_fields: dict[Field, int],
                     fuzzy_fields: dict[Field, int]) -> dict[str, list[str]]:
    """Return a solr query with filters for each subsequent term."""
    terms = query['value'].split()
    query_str = ''
    for term in terms:
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
                fuzzy_str += f'~{fuzzy_fields[field]}'
                term_str += f' OR {fuzzy_str}'
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
