$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

# The exe icon (app_icon.ico) is a derived file (gitignored) regenerated here
# from the source app_icon.png when the .ico is missing — so a fresh clone
# builds cleanly even though only the .png is committed.
$iconPng = Join-Path $PSScriptRoot "app_icon.png"
$iconIco = Join-Path $PSScriptRoot "app_icon.ico"
if ((Test-Path -LiteralPath $iconPng) -and -not (Test-Path -LiteralPath $iconIco)) {
    Write-Host "Generating app_icon.ico from app_icon.png..." -ForegroundColor Cyan
    $env:PYTHONPATH = $PSScriptRoot
    & ".venv\Scripts\python.exe" -c "import sys; from PySide6.QtGui import QImage; from PySide6.QtCore import QSize, Qt; img=QImage(r'$iconPng').scaled(QSize(256,256), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation); sys.exit(0 if img.save(r'$iconIco','ICO') else 1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to generate app_icon.ico." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

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
