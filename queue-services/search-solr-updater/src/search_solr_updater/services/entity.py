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
"""Manages entity service interactions."""
from http import HTTPStatus

import requests
from flask import current_app
from flask_caching import Cache
from requests import exceptions

from search_solr_updater.exceptions import ExternalServiceException
from search_solr_updater.services.auth import get_bearer_token

entity_cache = Cache()

def get_cache_key(*args, **kwargs):
    """Return the cache key for the given args."""
    path = kwargs["path"] if kwargs else args[0]
    return "entity" + path


@entity_cache.cached(timeout=30, make_cache_key=get_cache_key)
def get_entity_info(path: str):
    """Get business data from the legal-api."""
    try:
        headers = {
          "Authorization": "Bearer " + get_bearer_token(),
          "Content-Type": "application/json"
        }
        url = current_app.config["LEAR_SVC_URL"] + path
        resp = requests.get(url=url,
                            headers=headers,
                            params={"slim": True},
                            timeout=current_app.config["LEAR_SVC_TIMEOUT"])
        if resp.status_code != HTTPStatus.OK:
            raise ExternalServiceException(error="Unable to get business data from legal-api.",
                                           status_code=resp.status_code)
        return resp
    except (exceptions.ConnectionError, exceptions.Timeout) as err:
        current_app.logger.debug("LEGAL API connection failure: %s", err)
        raise ExternalServiceException(error="Unable to get business data from legal-api.",
                                       status_code=resp.status_code) from err
    except ExternalServiceException as err:
        # pass along
        raise err
    except Exception as err:
        current_app.logger.debug("LEGAL API connection failure: %s", err.with_traceback(None))
        raise ExternalServiceException(error="Unable to get business data from legal-api.",
                                       status_code=HTTPStatus.INTERNAL_SERVER_ERROR) from err
