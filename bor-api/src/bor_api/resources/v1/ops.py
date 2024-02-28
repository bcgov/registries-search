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
"""Endpoints to check and manage the health of the service."""
from flask import current_app, Blueprint
from sqlalchemy import text, exc

from bor_api.exceptions import SolrException, exception_response
from bor_api.models import db
from bor_api.services import solr


bp = Blueprint('OPS', __name__, url_prefix='/ops')  # pylint: disable=invalid-name

SQL = text('select 1')


@bp.get('/healthz')
def healthy():
    """Return a JSON object stating the health of the Service and dependencies."""
    try:
        db.session.execute(SQL)
        solr.call_solr('GET', solr.search_url)
    except exc.SQLAlchemyError as db_exception:
        current_app.logger.error('DB connection pool unhealthy:' + repr(db_exception))
        return {'message': 'api is down'}, 500
    except SolrException as solr_exception:
        return exception_response(solr_exception)
    except Exception as default_exception:   # noqa: B902; log error
        current_app.logger.error('DB connection pool or SOLR connection query failed:' + repr(default_exception))
        return {'message': 'api is down'}, 500

    # made it here, so all checks passed
    return {'message': 'api is healthy'}, 200


@bp.get('/readyz')
def ready():
    """Return a JSON object that identifies if the service is setupAnd ready to work."""
    return {'message': 'api is ready'}, 200
