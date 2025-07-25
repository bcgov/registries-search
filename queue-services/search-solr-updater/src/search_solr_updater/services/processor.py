# Copyright © 2024 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the "License");
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    https://opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Manages processor for updating a business in search."""
from contextlib import suppress
from time import sleep

from flask import current_app
from simple_cloudevent import SimpleCloudEvent

from search_solr_updater.exceptions import BusinessException
from search_solr_updater.services.entity import get_entity_info
from search_solr_updater.services.search import update_search


def process_business_event(ce: SimpleCloudEvent):
    """Process business events."""
    if not ce.type or not "bc.registry.business" in ce.type:
        # expecting bc.registry.business.<anything>
        current_app.logger.debug("skipping event based on ce.type")
        return
    current_app.logger.debug(">>>>>>>process_business_event>>>>>")
    # get identifier
    identifier = ce.data.get("identifier")
    if not identifier:
        raise BusinessException("Unable to parse identifier from message payload.")
    if identifier in current_app.config["BUSINESSES_MANAGED_BY_COLIN"]:
        current_app.logger.warning("Business is managed by COLIN. Skipping update for %s", identifier)
        return

    with suppress(Exception):
        if (filings := ce.data.get("filing", {}).get("legalFilings", [])) and "alteration" in filings:
            # if alteration, then give it 5 seconds (lear will still be processing it in some cases)
            sleep(5)
  
    # get extra data from lear
    business_info_path = f"/businesses/{identifier}"
    parties_info_path = f"/businesses/{identifier}/parties"
    business_resp = get_entity_info(business_info_path)
    parties_resp = get_entity_info(parties_info_path)
    # only add parties that are currently stored in solr
    solr_party_roles = ["partner", "proprietor"]  # solr does not store other parties
    parties = []
    for party in parties_resp.json().get("parties"):
        valid_roles = [x for x in party.get("roles") if x["roleType"].lower() in solr_party_roles]
        if valid_roles:
            party["roles"] = valid_roles
            parties.append(party)

    def convert_business(business: dict):
        """Return the business info with the expected legal name."""
        if business["legalType"] in ["SP", "GP"]:
            for name in business.get("alternateNames", []):
                if name["identifier"] == business["identifier"]:
                    business["legalName"] = name["name"]
                    break
        business['modernized'] = True
        return business

    # update solr via search-api
    update_payload = {
      "business": convert_business(business_resp.json()["business"]),
      "parties": parties
    }
    update_search(update_payload)

    current_app.logger.debug("<<<<<<<process_business_event<<<<<<<<<<")
