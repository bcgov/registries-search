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
import psycopg2
from flask import current_app

from search_solr_importer import oracle_db


def _get_stringified_list_for_sql(config_value: str) -> str:
    """Return the values from the config in a format usable for the execute statement."""
    if items := current_app.config.get(config_value, []):
        return ','.join([f"'{x}'" for x in items]).replace(')', '')

    return ''


def collect_colin_data():
    """Collect data from COLIN."""
    current_app.logger.debug('Connecting to Oracle instance...')
    cursor = oracle_db.connection.cursor()
    current_app.logger.debug('Collecting COLIN data...')
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


def collect_lear_data():
    """Collect data from LEAR."""
    if current_app.config.get('DB_LOCATION') == 'GCP':
        return _collect_lear_data_gcp()

    current_app.logger.debug('Connecting to OCP Postgres instance...')
    conn = psycopg2.connect(host=current_app.config.get('DB_HOST'),
                            port=current_app.config.get('DB_PORT'),
                            database=current_app.config.get('DB_NAME'),
                            user=current_app.config.get('DB_USER'),
                            password=current_app.config.get('DB_PASSWORD'))
    cur = conn.cursor()
    current_app.logger.debug('Collecting LEAR data...')
    cur.execute(f"""
        SELECT b.identifier,b.legal_name,b.legal_type,b.tax_id,b.last_ar_date,
            b.founding_date,b.restoration_expiry_date,pr.role,
            p.first_name,p.middle_initial,p.last_name,p.organization_name,p.party_type,p.id as party_id,
            CASE when b.state = 'LIQUIDATION' then 'ACTIVE' else b.state END state
        FROM businesses b
            LEFT JOIN (SELECT * FROM party_roles WHERE cessation_date is null
                       AND role in ('partner', 'proprietor')) as pr on pr.business_id = b.id
            LEFT JOIN parties p on p.id = pr.party_id
        WHERE b.legal_type in ({_get_stringified_list_for_sql('MODERNIZED_LEGAL_TYPES')})
        """)
    return cur


def _collect_lear_data_gcp():
    """Collect data from LEAR."""
    current_app.logger.debug('Connecting to GCP Postgres instance...')
    conn = psycopg2.connect(host=current_app.config.get('DB_HOST'),
                            port=current_app.config.get('DB_PORT'),
                            database=current_app.config.get('DB_NAME'),
                            user=current_app.config.get('DB_USER'),
                            password=current_app.config.get('DB_PASSWORD'))
    cur = conn.cursor()
    current_app.logger.debug('Collecting LEAR data...')
    cur.execute(f"""
        SELECT le.identifier,le.legal_name,le.entity_type as legal_type,le.founding_date,
            le.restoration_expiry_date,le.last_ar_date,alt.name as legal_name_alt,
            er.role_type as role,er.appointment_date,
            rle.first_name,rle.middle_initial,rle.last_name,rle.id as party_id,rle.legal_name as organization_name,
            rle_alt.name as organization_name_alt,
            rle_colin.organization_name as organization_name_colin,rle_colin.id as party_id_colin,
            CASE WHEN rle.entity_type != 'person'
                 THEN 'organization'
                 ELSE 'person'
                 END party_type,
            CASE WHEN le.state = 'LIQUIDATION'
                 THEN 'ACTIVE'
                 ELSE le.state
                 END state,
            CASE WHEN alt.bn15 IS NOT NULL
                 THEN alt.bn15
                 ELSE le.tax_id
                 END tax_id
        FROM legal_entities le
            LEFT JOIN alternate_names alt
                ON alt.legal_entity_id = le.id
                    AND alt.name_type = 'OPERATING'
                    AND alt.end_date IS NULL
            LEFT JOIN entity_roles er ON er.legal_entity_id = le.id
            LEFT JOIN legal_entities rle ON rle.id = er.related_entity_id
            LEFT JOIN alternate_names rle_alt
                ON rle_alt.legal_entity_id = rle.id
                    AND rle_alt.name_type = 'OPERATING'
                    AND rle_alt.end_date IS NULL
            LEFT JOIN colin_entities rle_colin ON rle_colin.id = er.related_colin_entity_id
        WHERE le.entity_type in ({_get_stringified_list_for_sql('MODERNIZED_LEGAL_TYPES')})
            AND er.cessation_date IS NULL
        """)
    return cur
