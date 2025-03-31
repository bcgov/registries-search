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
"""Enum for user roles."""
from .base import BaseEnum


class InterestDetails(BaseEnum):
    """Enum of the interest details of a significant individual."""

    DIR_DIRECT = "controlType.directors.directControl"
    DIR_INCONCERT = "controlType.directors.inConcertControl"
    DIR_INDIRECT = "controlType.directors.indirectControl"
    DIR_JOINTLY = "controlType.directors.actingJointly"
    DIR_SIG_INFL = "controlType.directors.significantInfluence"
    SHARES_BEN_OWNER = "controlType.shares.beneficialOwner"
    SHARES_INCONCERT = "controlType.shares.inConcertControl"
    SHARES_INDIRECT = "controlType.shares.indirectControl"
    SHARES_JOINTLY = "controlType.shares.actingJointly"
    SHARES_REG_OWNER = "controlType.shares.registeredOwner"
    VOTES_BEN_OWNER = "controlType.votes.beneficialOwner"
    VOTES_INCONCERT = "controlType.votes.inConcertControl"
    VOTES_INDIRECT = "controlType.votes.indirectControl"
    VOTES_JOINTLY = "controlType.votes.actingJointly"
    VOTES_REG_OWNER = "controlType.votes.registeredOwner"
