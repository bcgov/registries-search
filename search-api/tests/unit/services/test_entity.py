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
"""Tests for LEAR entity-service interactions."""

from search_api.services.entity import get_business_filing_document


def test_get_business_filing_document_forwards_document_class_and_drs_id(app, mocker):
    """Required DRS query parameters are forwarded to the LEAR document endpoint."""
    app.config["LEAR_SVC_URL"] = "https://legal-api.example/api/v2"
    app.config["BUSINESS_API_TIMEOUT"] = 30
    mocker.patch("search_api.services.entity.get_bearer_token", return_value="token")
    request_get = mocker.patch("search_api.services.entity.requests.get")

    with app.test_request_context("/?documentClass=COOP&drsId=DS0000657762"):
        get_business_filing_document("CP1234567", 1618118, "certifiedMemorandum")

    request_get.assert_called_once_with(
        url=(
            "https://legal-api.example/api/v2/businesses/CP1234567/filings/1618118/"
            "documents/certifiedMemorandum?documentClass=COOP&drsId=DS0000657762"
        ),
        headers={"Authorization": "Bearer token", "Content-Type": "application/pdf"},
        timeout=30,
    )


def test_get_business_filing_document_preserves_legacy_report_type_request(app, mocker):
    """Existing reportType and drsId requests remain unchanged."""
    app.config["LEAR_SVC_URL"] = "https://legal-api.example/api/v2"
    app.config["BUSINESS_API_TIMEOUT"] = 30
    mocker.patch("search_api.services.entity.get_bearer_token", return_value="token")
    request_get = mocker.patch("search_api.services.entity.requests.get")

    with app.test_request_context("/?reportType=certificate&drsId=DS0000657762"):
        get_business_filing_document("CP1234567", 1618118, "certifiedMemorandum")

    request_get.assert_called_once_with(
        url=(
            "https://legal-api.example/api/v2/businesses/CP1234567/filings/1618118/"
            "documents/certifiedMemorandum?reportType=certificate&drsId=DS0000657762"
        ),
        headers={"Authorization": "Bearer token", "Content-Type": "application/pdf"},
        timeout=30,
    )
