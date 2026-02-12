<#
.SYNOPSIS
    HealthATM - Start All Services (2 Backends + Frontend)

.USAGE
    Right-click > Run with PowerShell
    OR from terminal:  .\start.ps1
#>

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "   HealthATM - Starting All Services" -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

# --- Backend 1 (Main - AI Pipeline) ---
Write-Host "  [1/3] Starting Backend (port 8000)..." -ForegroundColor Yellow
$backend1Cmd = @"
Set-Location '$root\backend'
& '$root\fypenv\Scripts\Activate.ps1'
Write-Host '  Backend (Main) activated - port 8000' -ForegroundColor Green
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backend1Cmd

Start-Sleep -Seconds 2

# --- Backend 2 (Dinesh - Chat/Auth) ---
Write-Host "  [2/3] Starting Backend-Dinesh (port 8001)..." -ForegroundColor Yellow
$backend2Cmd = @"
Set-Location '$root\backend-dinesh'
& '$root\fypenv\Scripts\Activate.ps1'
Write-Host '  Backend (Dinesh) activated - port 8001' -ForegroundColor Green
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backend2Cmd

Start-Sleep -Seconds 2

# --- Frontend ---
Write-Host "  [3/3] Starting Frontend (port 3000)..." -ForegroundColor Yellow
$frontendCmd = @"
Set-Location '$root\frontend'
Write-Host '  Frontend starting...' -ForegroundColor Green
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "   All 3 services are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "   Backend (Main):    http://localhost:8000" -ForegroundColor White
Write-Host "   Backend (Dinesh):  http://localhost:8001" -ForegroundColor White
Write-Host "   Frontend:          http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "   Test scans: $root\test_scans\" -ForegroundColor DarkGray
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Press any key to close this launcher..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
