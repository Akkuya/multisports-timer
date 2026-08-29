$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Building multisports-timer..."
uv run pyinstaller --noconfirm multisports-timer.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nBuild complete: $PSScriptRoot\dist\multisports-timer.exe" -ForegroundColor Green
