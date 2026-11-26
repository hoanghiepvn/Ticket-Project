param([switch]$Deploy)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$version='0.30.4'
$folder=Join-Path $root "Airbyte/tools/abctl-$version"
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$archiveName="abctl-v$version-windows-amd64.zip"
$archive=Join-Path $folder $archiveName
$base="https://github.com/airbytehq/abctl/releases/download/v$version"
Invoke-WebRequest "$base/$archiveName" -OutFile $archive
$checks=(Invoke-WebRequest "$base/abctl_${version}_checksums.txt").Content
if ($checks -is [byte[]]) { $checks=[Text.Encoding]::UTF8.GetString($checks) }
$line=($checks -split "`n" | Where-Object { $_ -match [regex]::Escape($archiveName) } | Select-Object -First 1)
if (-not $line) { throw 'Checksum entry missing' }
$expected=($line.Trim() -split '\s+')[0]
if ((Get-FileHash $archive -Algorithm SHA256).Hash.ToLower() -ne $expected.ToLower()) { throw 'Checksum mismatch' }
Expand-Archive -LiteralPath $archive -DestinationPath $folder -Force
$binary=(Get-ChildItem $folder -Filter abctl.exe -Recurse | Select-Object -First 1).FullName
if (-not $binary) { throw 'abctl.exe missing' }
& $binary version
if ($LASTEXITCODE -ne 0) { throw 'abctl failed' }
if ($Deploy) {
    & $binary local install --port 8000
    if ($LASTEXITCODE -ne 0) { throw 'Airbyte deployment failed; inspect abctl local status' }
} else {
    Write-Host "Prepared abctl at $binary"
    Write-Host 'Run this script with -Deploy to deploy Airbyte. Then run abctl local credentials locally.'
}
