@echo off
cd /d "%~dp0"

:menu
cls
echo.
echo ========================================
echo   Fresh Milk - Project Manager
echo ========================================
echo.
echo   [1] Start all services
echo   [2] Stop all services
echo   [3] Clean cache
echo   [4] Build project
echo   [5] Clean + Build + Start
echo.
echo   [6] Start backend only
echo   [7] Start frontend only
echo.
echo   [0] Exit
echo.
echo ========================================

set /p choice=Select (0-7):

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto clean
if "%choice%"=="4" goto build
if "%choice%"=="5" goto full
if "%choice%"=="6" goto backend
if "%choice%"=="7" goto frontend
if "%choice%"=="0" goto end
goto menu

:start_all
call start.bat
goto menu

:stop
call stop.bat
goto menu

:clean
call clean.bat
goto menu

:build
call build.bat
goto menu

:full
call stop.bat
call clean.bat
call build.bat
call start.bat
goto menu

:backend
set PYTHON=C:\Param\Python\python-3.12.1\python.exe
echo [*] Starting Django backend...
start "Django" /min cmd /c "%PYTHON% manage.py runserver 0.0.0.0:8000"
echo [+] Backend: http://127.0.0.1:8000
pause
goto menu

:frontend
echo [*] Starting admin frontend...
cd admin-web
start "Frontend" /min cmd /c "npm run dev"
cd ..
echo [+] Frontend: http://127.0.0.1:5173
pause
goto menu

:end
exit
