\set ON_ERROR_STOP on
\getenv loader_password AIRBYTE_DB_PASSWORD
\getenv bi_password BI_PASSWORD
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE ROLE airbyte_loader LOGIN PASSWORD :'loader_password';
CREATE ROLE powerbi_reader LOGIN PASSWORD :'bi_password';
CREATE SCHEMA bronze AUTHORIZATION airbyte_loader;
CREATE SCHEMA airbyte_internal AUTHORIZATION airbyte_loader;
CREATE SCHEMA silver;
CREATE SCHEMA gold;
CREATE SCHEMA audit;
GRANT CONNECT ON DATABASE ticketing_analytics TO airbyte_loader, powerbi_reader;
GRANT USAGE ON SCHEMA gold TO powerbi_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE warehouse_admin IN SCHEMA gold GRANT SELECT ON TABLES TO powerbi_reader;
CREATE TABLE audit.runs (
 run_id text PRIMARY KEY, airbyte_job_id text NOT NULL, mode text NOT NULL,
 frozen_at timestamptz NOT NULL DEFAULT now(), published_at timestamptz, metrics jsonb
);
CREATE TABLE audit.current_publication (
 singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
 run_id text NOT NULL REFERENCES audit.runs(run_id)
);
