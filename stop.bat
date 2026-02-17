@echo off
cd /d "%~dp0"

echo.
echo [*] Stopping all services...
echo.

echo [*] Stopping port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [*] Stopping port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [*] Stopping node processes...
taskkill /IM node.exe /F >nul 2>&1

echo.
echo [+] All services stopped
echo.
pause
