# Manual events-only run. Schedule is configured in Airflow/dags/bronze/bronze_ticket_events.py.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
docker compose exec -T airflow-scheduler airflow dags unpause bronze_ticket_events
if ($LASTEXITCODE -ne 0) { throw 'Cannot unpause Bronze' }
docker compose exec -T airflow-scheduler airflow dags trigger bronze_ticket_events
if ($LASTEXITCODE -ne 0) { throw 'Cannot trigger Bronze' }
Write-Host 'Bronze only: Airbyte sync jobs. Silver and Gold are not triggered.'
