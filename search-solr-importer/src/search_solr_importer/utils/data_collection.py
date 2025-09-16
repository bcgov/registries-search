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
"""Data collection functions."""
from typing import Final

from flask import current_app
from sqlalchemy import CursorResult, text

from search_solr_importer import btr_db, lear_db, oracle_db


def _get_stringified_list_for_sql(config_value: str) -> str:
    """Return the values from the config in a format usable for the execute statement."""
    if items := current_app.config.get(config_value, []):
        return ",".join([f"'{x}'" for x in items]).replace(")", "")

    return ""


def collect_colin_data():
    """Collect data from COLIN."""
    current_app.logger.debug("Connecting to Oracle instance...")
    cursor = oracle_db.connection.cursor()
    current_app.logger.debug("Collecting COLIN data...")
    cursor.execute(f"""
        SELECT c.corp_num as identifier, c.corp_typ_cd as legal_type, c.bn_15 as tax_id,
            c.last_ar_filed_dt as last_ar_date, c.recognition_dts as founding_date, c.transition_dt,
            cn.corp_nme as legal_name, cp.business_nme as organization_name, cp.first_nme as first_name,
            cp.last_nme as last_name, cp.middle_nme as middle_initial, cp.party_typ_cd, cp.corp_party_id as party_id,
            cs.state_typ_cd as state_type, ct.corp_class, f.effective_dt as restoration_date,
            j.can_jur_typ_cd as xpro_jurisdiction,
            CASE cos.op_state_typ_cd
                when 'ACT' then 'ACTIVE' when 'HIS' then 'HISTORICAL'
                else 'ACTIVE' END as state
        FROM corporation c
        join corp_state cs on cs.corp_num = c.corp_num
        join corp_op_state cos on cos.state_typ_cd = cs.state_typ_cd
        join corp_type ct on ct.corp_typ_cd = c.corp_typ_cd
        join corp_name cn on cn.corp_num = c.corp_num
        left join (select * from event e join filing f on f.event_id = e.event_id
                   where filing_typ_cd in ('RESTF','RESXF')
                   order by f.effective_dt desc) f on f.corp_num = c.corp_num
        left join (select * from jurisdiction where end_event_id is null) j on j.corp_num = c.corp_num
        left join (select business_nme, first_nme, last_nme, middle_nme, corp_num, party_typ_cd, corp_party_id
                from corp_party
                where end_event_id is null and party_typ_cd in ('FIO','FBO')
            ) cp on cp.corp_num = c.corp_num
        WHERE c.corp_typ_cd not in ({_get_stringified_list_for_sql('MODERNIZED_LEGAL_TYPES')})
            and cs.end_event_id is null
            and cn.end_event_id is null
            and cn.corp_name_typ_cd in ('CO', 'NB')
        """)
    return cursor


def collect_lear_data() -> CursorResult:
    """Collect data from LEAR."""
    current_app.logger.debug("Connecting to LEAR Postgres instance...")
    conn = lear_db.db.engine.connect()
    current_app.logger.debug("Collecting LEAR data...")
    return conn.execute(text(f"""
        SELECT b.identifier,b.legal_name,b.legal_type,b.tax_id,b.last_ar_date,
            b.founding_date,b.restoration_expiry_date,b.state,pr.role,
            p.first_name,p.middle_initial,p.last_name,p.organization_name,p.party_type,p.id as party_id
        FROM businesses b
            LEFT JOIN (SELECT * FROM party_roles WHERE cessation_date is null
                       AND role in ('partner', 'proprietor')) as pr on pr.business_id = b.id
            LEFT JOIN parties p on p.id = pr.party_id
        WHERE b.identifier not in ({_get_stringified_list_for_sql('BUSINESSES_MANAGED_BY_COLIN')})
        """
    ))


def collect_lear_businesses_requiring_transition() -> CursorResult:
    current_app.logger.debug("Connecting to LEAR Postgres instance...")
    conn = lear_db.db.engine.connect()
    current_app.logger.debug("Collecting LEAR businesses that require a transition application...")
    return conn.execute(text(f"""
        SELECT b.identifier
        FROM businesses b
        JOIN (
            SELECT * FROM filings
            WHERE filing_type in ('restoration','resotrationApplication') AND status = 'COMPLETED'
        ) as rf on rf.business_id = b.id
        WHERE b.legal_type in ({_get_stringified_list_for_sql('TRANSITION_APPLICATION_LEGAL_TYPES')})
            AND b.founding_date < '2004-03-29 00:00:00+00:00'
            AND b.state = 'ACTIVE'
            AND NOT EXISTS (
                SELECT * FROM filings
                WHERE business_id = b.id
                    AND filing_type = 'transition'
                    AND status = 'COMPLETED'
                    AND effective_date > rf.effective_date
            )
        GROUP BY b.identifier
        """
    ))


def collect_btr_data(limit: int | None = None, offset: int | None = None) -> CursorResult:
    """Collect data from BTR."""
    limit_clause = ""
    if limit:
        limit_clause = f"LIMIT {limit}"
    if offset:
        limit_clause += f" OFFSET {offset}"
    if limit_clause:
        # NOTE: needed in order to make sure we get every record when doing batch loads
        limit_clause = f"ORDER BY p.id {limit_clause}"

    current_app.logger.debug("Connecting to BTR Postgres instance...")
    conn = btr_db.db.engine.connect()
    current_app.logger.debug("Collecting BTR data...")
    return conn.execute(text(
        f"""
        SELECT s.business_identifier, p.person_json
        FROM submission s
        JOIN ownership o on s.id = o.submission_id
        JOIN person p on p.id = o.person_id
        {limit_clause}
        """
    ))
