@echo off
title HealthATM - Stop All
echo.
echo  Stopping all HealthATM services...
echo.

:: Kill processes on ports 8000, 8001, 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

echo.
echo  All services stopped (ports 8000, 8001, 3000).
echo.
pause
