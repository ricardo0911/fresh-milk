@echo off
chcp 936 >nul
cd /d "%~dp0"

echo.
echo ========================================
echo   Fresh Milk System - Startup
echo ========================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)

echo [1/3] Starting Django backend...
start "Django Backend" /D "%~dp0" cmd /k python manage.py runserver 0.0.0.0:8000
timeout /t 2 /nobreak >nul

echo [2/3] Starting Admin frontend...
if not exist "%~dp0admin-web\node_modules" (
    echo      Installing dependencies...
    cd /d "%~dp0admin-web"
    call npm install
    cd /d "%~dp0"
)
start "Admin Frontend" /D "%~dp0admin-web" cmd /k npm run dev
timeout /t 2 /nobreak >nul

echo [3/3] Opening miniprogram directory...
explorer "%~dp0miniprogram"

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo   Backend API:    http://127.0.0.1:8000
echo   Admin Panel:    http://127.0.0.1:3000
echo   Miniprogram:    Open miniprogram folder in WeChat DevTools
echo.
echo   Press any key to close this window (services will keep running)
echo.
pause
