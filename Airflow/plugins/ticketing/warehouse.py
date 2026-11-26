"""Confirm Bronze input and record completion; dbt writes directly to Gold."""
import os
import uuid
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
from ticketing.schema import FIELDS, KEYS, GOLD, require

LOCK = 19280928

def connect():
    return psycopg2.connect(connect_timeout=10, application_name='ticketing_airflow')

def columns(names):
    return sql.SQL(',').join(sql.Identifier(n) for n in names)

def preflight(full_refresh=False):
    uuid.UUID(os.environ.get('AIRBYTE_CONNECTION_ID',''))
    require(bool(os.environ.get('AIRBYTE_CLIENT_ID') and os.environ.get('AIRBYTE_CLIENT_SECRET')),
            'Configure Airbyte credentials in .env')
    with connect() as conn, conn.cursor() as cur:
        cur.execute('SHOW server_version_num')
        require(int(cur.fetchone()[0]) >= 150000, 'MERGE requires PostgreSQL 15+')
        for name in FIELDS:
            cur.execute("SELECT to_regclass(%s)", ('silver.'+name,))
            if cur.fetchone()[0] and not full_refresh:
                cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='silver' AND table_name=%s AND column_name IN ('_record_hash','_is_deleted','_loaded_at')",(name,))
                require(cur.fetchone()[0] == 3, 'First upgraded run requires full_refresh=true')
        if not full_refresh:
            cur.execute("SELECT to_regclass('gold.fact_ticket_sales')")
            if cur.fetchone()[0]:
                cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='gold' AND table_name='fact_ticket_sales' AND column_name IN ('_record_hash','_is_deleted','_loaded_at')")
                require(cur.fetchone()[0] == 3, 'First direct-Gold run requires full_refresh=true')
    return True

def assert_working(cur, run_id):
    cur.execute('SELECT run_id FROM audit.working_run WHERE singleton')
    row = cur.fetchone()
    require(row and row[0] == run_id, 'Working tables belong to another run; do not retry old tasks')

def confirm_bronze(run_id, job_id, allow_empty=False):
    with connect() as conn:
        conn.set_session(isolation_level='REPEATABLE READ')
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_xact_lock(%s)',(LOCK,))
            cur.execute('SELECT run_id FROM audit.runs WHERE run_id=%s',(run_id,))
            if cur.fetchone():
                assert_working(cur,run_id)
                return
            for name, fields in FIELDS.items():
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='bronze' AND table_name=%s",(name,))
                available = {r[0] for r in cur.fetchall()}
                require(set(fields) <= available, f'Missing Bronze business columns: {name}')
                require({'_airbyte_extracted_at','_airbyte_raw_id'} <= available, f'Missing Airbyte metadata: {name}')
                cur.execute(sql.SQL('SELECT count(*),count({}) FROM {}').format(sql.Identifier(KEYS[name]),sql.Identifier('bronze',name)))
                count, nonnull = cur.fetchone()
                require(allow_empty or count > 0, f'Empty snapshot blocked: {name}')
                require(count == nonnull, f'Null business key: {name}')
            cur.execute('INSERT INTO audit.runs(run_id,airbyte_job_id,mode) VALUES (%s,%s,%s)',(run_id,job_id,'airbyte'))
            cur.execute('CREATE TABLE IF NOT EXISTS audit.working_run (singleton boolean PRIMARY KEY CHECK(singleton),run_id text NOT NULL)')
            cur.execute('INSERT INTO audit.working_run VALUES(true,%s) ON CONFLICT(singleton) DO UPDATE SET run_id=excluded.run_id',(run_id,))

def complete(run_id):
    """Record completion only; this is not an atomic multi-model publication."""
    metrics = {}
    with connect() as conn, conn.cursor() as cur:
        cur.execute('SELECT pg_advisory_xact_lock(%s)',(LOCK,))
        assert_working(cur,run_id)
        for name in GOLD:
            cur.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier('gold',name)))
            metrics[name] = cur.fetchone()[0]
        cur.execute('GRANT USAGE ON SCHEMA gold TO powerbi_reader')
        cur.execute('GRANT SELECT ON ALL TABLES IN SCHEMA gold TO powerbi_reader')
        cur.execute('UPDATE audit.runs SET published_at=now(),metrics=%s WHERE run_id=%s',(Json(metrics),run_id))
        cur.execute('INSERT INTO audit.current_publication VALUES(true,%s) ON CONFLICT(singleton) DO UPDATE SET run_id=excluded.run_id',(run_id,))
    return metrics
