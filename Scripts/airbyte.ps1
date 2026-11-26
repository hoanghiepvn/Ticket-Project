param([ValidateSet('start','status','credentials')][string]$Action='status')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$binary=Join-Path $root 'Airbyte/tools/abctl-0.30.4/abctl-v0.30.4-windows-amd64/abctl.exe'
if (-not (Test-Path -LiteralPath $binary)) { throw 'abctl missing. See scripts/install-airbyte.ps1.' }
docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Open Docker Desktop and wait for the engine.' }
if ($Action -eq 'start') {
    $state=docker inspect --format '{{.State.Running}}' airbyte-abctl-control-plane 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'Airbyte cluster missing. Read the setup guide; do not delete volumes.' }
    if ($state -ne 'true') {
        docker start airbyte-abctl-control-plane
        if ($LASTEXITCODE -ne 0) { throw 'Cannot start Airbyte cluster' }
    }
    Write-Host 'Airbyte http://localhost:8000 -- allow services time to become ready.'
    & $binary local status
} elseif ($Action -eq 'credentials') {
    & $binary local credentials
} else {
    & $binary local status
}
if ($LASTEXITCODE -ne 0) { throw 'abctl command failed; inspect the output above.' }
