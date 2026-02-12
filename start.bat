@echo off
title HealthATM - Launcher
echo.
echo  ========================================
echo   HealthATM - Starting All Services
echo  ========================================
echo.

:: --- Backend 1 (Main - AI Pipeline) ---
echo  [1/3] Starting Backend (port 8000)...
start "HealthATM Backend" cmd /k "cd /d %~dp0backend && %~dp0fypenv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak > nul

:: --- Backend 2 (Dinesh - Chat/Auth) ---
echo  [2/3] Starting Backend-Dinesh (port 8001)...
start "HealthATM Backend-Dinesh" cmd /k "cd /d %~dp0backend-dinesh && %~dp0fypenv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 2 /nobreak > nul

:: --- Frontend ---
echo  [3/3] Starting Frontend (port 3000)...
start "HealthATM Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo  ========================================
echo   All 3 services are starting!
echo.
echo   Backend (Main):    http://localhost:8000
echo   Backend (Dinesh):  http://localhost:8001
echo   Frontend:          http://localhost:3000
echo.
echo   Test scans: test_scans\
echo  ========================================
echo.
echo  You can close this window. The servers
echo  run in their own terminal windows.
echo.
pause
