@echo off
cd /d "%~dp0"

echo.
echo [*] Building project...
echo.

set PYTHON=C:\Param\Python\python-3.12.1\python.exe

echo [*] Running database migrations...
"%PYTHON%" manage.py makemigrations
"%PYTHON%" manage.py migrate

echo [*] Installing frontend dependencies...
cd admin-web
call npm install

echo [*] Building frontend...
call npm run build
cd ..

echo.
echo [+] Build completed
echo.
pause
