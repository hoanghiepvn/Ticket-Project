param([switch]$Build)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Open Docker Desktop first.' }
docker image inspect ticketing-elt:4.0-postgres --format '{{.Id}}' 2>$null | Out-Null
if ($Build -or $LASTEXITCODE -ne 0) {
    docker compose build airflow-init
    if ($LASTEXITCODE -ne 0) { throw 'Image build failed' }
}
docker compose up -d --no-build
if ($LASTEXITCODE -ne 0) { throw 'Startup failed; inspect docker compose logs' }
Write-Host 'Airflow http://localhost:8080 | PostgreSQL localhost:5433'
Write-Host 'Bronze runs Airbyte only. IDs: dags/bronze/config.py. Edit schedule inside each DAG file before unpausing.'
