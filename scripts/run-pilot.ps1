param([string]$Output = 'data/derived/replay')
$ErrorActionPreference = 'Stop'
$pilotPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $pilotPython)) { $pilotPython = 'python' }
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $pilotPython -B -m bank_quality replay --collection data/pilot-20261001.collection.json --output $Output
    if ($LASTEXITCODE -ne 0) { throw 'Hash-verified pilot replay failed' }
} finally { Pop-Location }
