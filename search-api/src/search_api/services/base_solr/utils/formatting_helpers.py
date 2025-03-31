# Copyright © 2023 Province of British Columbia
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
"""Solr formatting functions."""
import re


def parse_facets(facet_data: dict) -> dict:
    """Return formatted solr facet response data."""
    facet_info = facet_data.get("facets", {})
    facets = {}
    for category in facet_info:
        if category == "count":
            continue
        facets[category] = []
        for item in facet_info[category]["buckets"]:
            new_category = {"value": item["val"], "count": item["count"]}
            if parent_count := item.get("by_parent", None):
                new_category["parentCount"] = parent_count
            facets[category].append(new_category)

    return {"fields": facets}


def prep_query_str(query: str, replace_specials=False) -> str:
    r"""Return the query string prepped for solr call (more advanced method).

    Rules:
        - no doubles: &,+
        - escape beginning: +,-,/,!
        - escape everywhere: ",:,[,],*,~,<,>,?,\
        - remove: (,),^,{,},|,\
        - lowercase: all
    """
    if not query:
        return ""

    rmv_doubles = r"([&+]){2,}"
    rmv_all = r"([()^{}|\\])"
    esc_begin = r"(^|\s)([+\-/!])"
    esc_all = r'([:~<>?\"\[\]])'
    special_and = r"([&+])"
    special_dash = r"(\S)(-)(\S)"

    query = re.sub(rmv_doubles, r"\1", query.lower())
    query = re.sub(rmv_all, "", query)
    if replace_specials:
        query = re.sub(special_and, r" and ", query)
        query = re.sub(special_dash, r" - ", query)
    query = re.sub(esc_begin, r"\1\\\2", query)
    query = re.sub(esc_all, r"\\\1", query)
    return query.lower().replace("  ", " ").strip()
