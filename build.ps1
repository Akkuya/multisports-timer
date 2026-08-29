$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Building multisports-timer..."
uv run pyinstaller --noconfirm multisports-timer.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

$DistDir = Join-Path $PSScriptRoot "dist"

# Copy the loose assets (audio is loaded from next to the exe, NOT bundled) so
# the dist/ folder is a complete, self-contained deploy bundle. Replacement
# happens with no rebuild.
$assetsSrc = Join-Path $PSScriptRoot "assets"
$assetsDst = Join-Path $DistDir "assets"
if (Test-Path -LiteralPath $assetsSrc) {
    New-Item -ItemType Directory -Force -Path $assetsDst | Out-Null
    Copy-Item -Path (Join-Path $assetsSrc "*") -Destination $assetsDst -Recurse -Force
    Write-Host "Copied assets -> $assetsDst" -ForegroundColor Cyan
} else {
    Write-Host "No assets folder found at $assetsSrc; skipping." -ForegroundColor Yellow
}

# Also ship a starter config.yaml next to the exe (the app creates proper logs/).
$configSrc = Join-Path $PSScriptRoot "config.yaml"
if (Test-Path -LiteralPath $configSrc) {
    Copy-Item -Path $configSrc -Destination (Join-Path $DistDir "config.yaml") -Force
    Write-Host "Copied config.yaml -> $DistDir" -ForegroundColor Cyan
}

Write-Host "`nBuild complete: $DistDir\multisports-timer.exe" -ForegroundColor Green
Write-Host "Deploy the whole dist\ folder (exe + assets\ + config.yaml)." -ForegroundColor Green
