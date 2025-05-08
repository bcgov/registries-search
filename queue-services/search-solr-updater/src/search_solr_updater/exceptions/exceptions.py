# Copyright © 2025 Province of British Columbia
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
"""Application Specific Exceptions"""
from dataclasses import dataclass
from http import HTTPStatus


@dataclass
class BaseException(Exception):  # noqa: N818
    """Base exception class for custom exceptions."""

    error: str
    message: str = None
    status_code: HTTPStatus = None


@dataclass
class AuthorizationException(BaseException):
    """Authorization exception."""

    def __post_init__(self):
        """Return a valid AuthorizationException."""
        self.error = f"{self.error}, {self.status_code}"
        self.message = "Unauthorized access."
        self.status_code = HTTPStatus.UNAUTHORIZED


@dataclass
class BusinessException(BaseException):
    """Business rules exception."""

    def __post_init__(self):
        """Return a valid BusinessException."""
        if not self.message:
            self.message = "Business exception."


@dataclass
class ExternalServiceException(BaseException):
    """3rd party service exception."""

    def __post_init__(self):
        """Return a valid ExternalServiceException."""
        self.message = "3rd party service error while processing request."
        self.error = f"{self.error}, {self.status_code}"
        self.status_code = HTTPStatus.SERVICE_UNAVAILABLE
