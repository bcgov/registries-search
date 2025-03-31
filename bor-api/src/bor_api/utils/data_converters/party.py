# Copyright © 2024 Province of British Columbia
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
"""Data conversion methods for party."""
from flask import current_app
from phonenumbers import PhoneNumberFormat, format_number, parse

from bor_api.enums import InterestDetails
from bor_api.services.bor_solr.doc_models import DateRange, Entity, EntityRole, Interest, InterestParty

from .address import get_btr_address, get_lear_addresses


def _add_btr_interests(owner_info: dict, interests: list[Interest], date_ranges: list[DateRange]):
    """Populate interests from the owner_info"""
    for interest_info in owner_info.get("interests", []):
        interest_parties = [
            InterestParty(interestPartyID=x["uuid"], interestPartyName=x.get("legalName") or None)
            for x in interest_info.get("connectedIndividuals", [])
        ]

        # NOTE: BTR saves a new interest for each interest/details for each effective date range
        start_date = interest_info.get("startDate")
        end_date = interest_info.get("endDate")
        # Only add 1 date range per unique interest effective start date
        if not any(date for date in date_ranges if date.start == start_date):
            date_ranges.append(DateRange(start=start_date or None, end=end_date or None, active=not end_date))

        interest_details = interest_info.get("details") or None
        # Only add 1 interest per unique interest details
        interest_already_added = any(
            interest
            for interest in interests
            if (interest.details == interest_details)
            # 'other' interest details are transformed to the other reason on init
            or (interest_details not in InterestDetails and interest.interestType == "otherInfluenceOrControl")
        )
        if not interest_already_added:
            interests.append(
                Interest(
                    details=interest_details,
                    directOrIndirect=interest_info.get("directOrIndirect") or None,
                    interestType=interest_info.get("type") or None,
                    relatedParties=interest_parties or None,
                    sharesExact=interest_info.get("share", {}).get("exact") or None,
                    sharesMax=interest_info.get("share", {}).get("maximum") or None,
                    sharesMin=interest_info.get("share", {}).get("minimum") or None,
                )
            )


def _get_btr_phone_number(party: dict[str, dict | str]) -> str:
    """Return the stringified formatted phone number from the BTR phone dict."""
    if (phone_info := party.get("phoneNumber")) and (number := phone_info.get("number")):
        if country_number := phone_info.get("countryCallingCode", ""):
            country_number = f"+{country_number}".replace("++", "+")
        if extension := phone_info.get("extension", ""):
            extension = f"#{extension}".replace("##", "#")

        if (country_iso := phone_info.get("countryCode2letterIso") or None) or country_number:
            try:
                phone_number_obj = parse(country_number + number, country_iso)
                # NOTE: this will return an unformatted string if the area code is invalid for the country
                number = format_number(phone_number_obj, PhoneNumberFormat.NATIONAL)

            except Exception as err:
                current_app.logger.debug("phone_info: %s", phone_info)
                current_app.logger.warning("Failed to parse phone number: %s", err)

        return f"{country_number} {number} {extension}".strip()

    return None


def _get_lear_party_name(officer: dict[str, str]) -> str:
    """Return the parsed name of the party from LEAR party officer format."""
    if officer.get("organizationName"):
        return officer["organizationName"].strip()
    person_name = ""
    if officer.get("firstName"):
        person_name += officer["firstName"].strip()
    if officer.get("middleInitial"):
        person_name += " " + officer["middleInitial"].strip()
    if officer.get("lastName"):
        person_name += " " + officer["lastName"].strip()
    return person_name.strip()


def get_lear_party(party_info: dict, business: Entity) -> list[Entity]:
    """Return the party from LEAR format as a list of Entity docs (1 per role)."""
    addresses = None
    if delivery_address_info := party_info.get("deliveryAddress"):
        addresses = get_lear_addresses([delivery_address_info], "DELIVERY")

    name = _get_lear_party_name(party_info["officer"])
    # NOTE: business parties are being ignored for now
    entity_type = "PERSON" if party_info["officer"]["partyType"] == "person" else "BUSINESS"

    base_party_id = f"{party_info['source']}{party_info['officer']['id']}"
    # NOTE: if the id is not unique then multiple roles will be added under the same entity
    # TODO: combine roles across role types under the same entity (UI for director search needs update first)
    # combine roles of the same role type, split roles of different types into their own entity
    roles_to_split: dict[str, str | dict[str, list[DateRange]]] = {}
    for role in party_info.get("roles", []):
        entity_id = f"{base_party_id}{business.identifier}{role['roleType'].replace(' ', '_')}".upper()
        roles_to_split.setdefault(entity_id, {"dates": [], "roleType": role["roleType"]})["dates"].append(
            DateRange(start=role["appointmentDate"], end=role.get("cessationDate", None))
        )
    # add a doc for each role
    entities = []
    for entity_id, role_data in roles_to_split.items():
        entities.append(
            Entity(
                entityAddresses=addresses,
                entityType=entity_type,
                id=entity_id,
                legalName=name,
                roles=[
                    EntityRole(
                        id=entity_id + "/roles0",
                        relatedAddresses=business.entityAddresses,
                        relatedEntityType="BUSINESS",
                        relatedIdentifier=business.identifier,
                        relatedLegalType=business.legalType,
                        relatedName=business.legalName,
                        relatedState=business.state,
                        roleDates=role_data["dates"],
                        roleType=role_data["roleType"],
                        relatedBN=business.bn,
                        relatedEmail=business.email,
                    )
                ],
            )
        )

    return entities


def get_btr_owner(owner_info: dict[str, str | dict], business: Entity):
    """Return the owner info as an Entity."""
    date_ranges: list[DateRange] = []
    interests: list[Interest] = []
    _add_btr_interests(owner_info, interests, date_ranges)

    party: dict = owner_info["interestedParty"]
    names_dict = {}
    for name in party.get("names"):
        if name_type := name.get("type"):  # expecting this to be 'individual' or 'alternative'
            names_dict[name_type] = name.get("fullName")

    tax_number = None
    for identifier in party.get("identifiers", []):
        # TODO: support other tax numbers?
        if identifier["scheme"] == "CAN-TAXID":
            tax_number = identifier["id"]

    address = None
    if (addresses := party.get("addresses")) and len(addresses) > 0:
        address = get_btr_address(addresses[0], "RESIDENCE")

    entity_id = party["statementID"]
    role_id = entity_id + business.identifier + "SIGNIFICANT_INDIVIDUAL"
    return Entity(
        id=entity_id,
        entityAddresses=[address] if address else None,
        entityType="PERSON",
        externalInfluence=party.get("externalInfluence"),
        legalName=names_dict.get("individual"),
        alternateName=names_dict.get("alternative"),
        birthDate=party.get("birthDate"),
        isPermanentResident=party.get("isPermanentResidentCa"),
        nationalities=[country.get("code") for country in party.get("nationalities", [])],
        phoneNumber=_get_btr_phone_number(party),
        taxNumber=tax_number,
        taxResidencies=[country.get("code") for country in party.get("taxResidencies", [])],
        email=party.get("email"),
        roles=[
            EntityRole(
                id=role_id,
                relatedAddresses=business.entityAddresses,
                relatedEntityType="BUSINESS",
                relatedIdentifier=business.identifier,
                relatedLegalType=business.legalType or "N/A",
                relatedName=business.legalName,
                relatedState=business.state or "N/A",
                roleDates=date_ranges,
                roleType="SIGNIFICANT INDIVIDUAL",
                relatedBN=business.bn,
                relatedEmail=business.email,
                relatedInterests=interests,
            )
        ],
    )
