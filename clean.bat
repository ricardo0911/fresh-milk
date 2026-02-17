@echo off
cd /d "%~dp0"

echo.
echo [*] Cleaning cache...
echo.

echo [*] Cleaning Python cache...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul

echo [*] Cleaning frontend cache...
if exist "admin-web\node_modules\.cache" rd /s /q "admin-web\node_modules\.cache" 2>nul
if exist "admin-web\dist" rd /s /q "admin-web\dist" 2>nul

echo [*] Cleaning miniprogram cache...
if exist "miniprogram\miniprogram_npm" rd /s /q "miniprogram\miniprogram_npm" 2>nul

echo.
echo [+] Cache cleaned
echo.
pause
