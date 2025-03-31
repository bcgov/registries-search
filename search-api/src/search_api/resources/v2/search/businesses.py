# Copyright © 2024 Province of British Columbia
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
"""API endpoints for Search."""
from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_cors import cross_origin

import search_api.resources.utils as resource_utils
from search_api.exceptions import SolrException
from search_api.services import business_solr
from search_api.services.base_solr.utils import QueryParams, parse_facets, prep_query_str
from search_api.services.business_solr.doc_fields import BusinessField, PartyField
from search_api.services.business_solr.utils import business_search
from search_api.utils.validators import validate_search_request

bp = Blueprint("BUSINESSES", __name__, url_prefix="/businesses")


@bp.post("")
@cross_origin(origins="*")
def businesses():
    """Return a list of business results."""
    try:
        request_json, errors = validate_search_request()
        if errors:
            return resource_utils.bad_request_response("Errors processing request.", errors)
        # set base query params
        query_json: dict = request_json.get("query", {})
        query = {
            "value": prep_query_str(query_json["value"], True),
            BusinessField.NAME_SINGLE.value: prep_query_str(query_json.get(BusinessField.NAME.value, ""), True),
            BusinessField.IDENTIFIER_Q.value: prep_query_str(query_json.get(BusinessField.IDENTIFIER.value, "")),
            BusinessField.BN_Q.value: prep_query_str(query_json.get(BusinessField.BN.value, ""))
        }
        # set child query params
        child_query = {
            PartyField.PARTY_NAME_SINGLE.value: query_json.get("parties", {}).get(PartyField.PARTY_NAME.value, "")
        }
        # set faceted category params
        categories_json: dict = request_json.get("categories", {})
        categories = {
            BusinessField.TYPE: categories_json.get(BusinessField.TYPE.value, None),
            BusinessField.STATE: categories_json.get(BusinessField.STATE.value, None)
        }

        # set doc fields to return
        fields = business_solr.business_with_parties_fields
        # create solr search params obj from parsed params
        params = QueryParams(query=query,
                             start=request_json.get("start", business_solr.default_start),
                             rows=request_json.get("rows", business_solr.default_rows),
                             categories=categories,
                             fields=fields,
                             query_fields={
                                 BusinessField.NAME_Q: "parent",
                                 BusinessField.NAME_STEM_AGRO: "parent",
                                 BusinessField.NAME_SINGLE: "parent",
                                 BusinessField.NAME_XTRA_Q: "parent",
                                 BusinessField.BN_Q: "parent",
                                 BusinessField.IDENTIFIER_Q: "parent"},
                             query_boost_fields={
                                 BusinessField.NAME_Q: 2,
                                 BusinessField.NAME_STEM_AGRO: 2,
                                 BusinessField.NAME_SINGLE: 2},
                             query_fuzzy_fields={
                                 BusinessField.NAME_Q: {"short": 1, "long": 2},
                                 BusinessField.NAME_STEM_AGRO: {"short": 1, "long": 2},
                                 BusinessField.NAME_SINGLE: {"short": 1, "long": 2}},
                             child_query=child_query,
                             child_categories={},
                             child_date_ranges={})
        # execute search
        results = business_search(params, business_solr)
        response = {
            "facets": parse_facets(results),
            "searchResults": {
                "queryInfo": {
                    "query": {
                        "value": query["value"],
                        BusinessField.NAME.value: query[BusinessField.NAME_SINGLE.value] or "",
                        BusinessField.IDENTIFIER.value: query[BusinessField.IDENTIFIER_Q.value] or "",
                        BusinessField.BN.value: query[BusinessField.BN_Q.value] or ""
                    },
                    "categories": {
                        BusinessField.TYPE.value: categories.get(BusinessField.TYPE, ""),
                        BusinessField.STATE.value: categories.get(BusinessField.STATE, "")},
                    "rows": params.rows,
                    "start": params.start
                },
                "totalResults": results.get("response", {}).get("numFound"),
                "results": results.get("response", {}).get("docs")},
            }

        return jsonify(response), HTTPStatus.OK

    except SolrException as solr_exception:
        return resource_utils.exception_response(solr_exception)
    except Exception as default_exception:
        return resource_utils.default_exception_response(default_exception)
