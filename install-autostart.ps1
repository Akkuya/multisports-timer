param(
    [switch]$Uninstall,
    [string]$ExePath = ""
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$TaskName = "Multisports Timer"

if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Autostart task '$TaskName' removed." -ForegroundColor Green
    } else {
        Write-Host "No autostart task '$TaskName' found." -ForegroundColor Yellow
    }
    exit 0
}

if (-not $ExePath) {
    $ExePath = Join-Path $PSScriptRoot "dist\multisports-timer.exe"
}

if (-not (Test-Path -LiteralPath $ExePath)) {
    Write-Host "No built exe found at $ExePath" -ForegroundColor Yellow
    Write-Host "Run .\build.ps1 first, or pass -ExePath pointing at your exe."
    exit 1
}

$ExePath = (Get-Item -LiteralPath $ExePath).FullName
Write-Host "Installing autostart for: $ExePath" -ForegroundColor Cyan

# Register the task. Runs at user logon with highest privileges so the
# 'keyboard' global-hotkey hook works (it needs admin on Windows).
$action = New-ScheduledTaskAction -Execute $ExePath
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

if ($?) {
    Write-Host "Autostart task '$TaskName' registered." -ForegroundColor Green
    Write-Host "It will launch the timer at every logon of $env:USERNAME." -ForegroundColor Green
} else {
    Write-Host "Failed to register the task." -ForegroundColor Red
    exit 1
}

Write-Host "`nTo verify or remove:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  .\install-autostart.ps1 -Uninstall"
