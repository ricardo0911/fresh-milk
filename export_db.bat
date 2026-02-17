@echo off
chcp 65001 >nul

set DB_NAME=fresh_milk_db
set DB_USER=root
set DB_PASS=root
set OUTPUT_FILE=fresh_milk_db_backup.sql

echo Exporting database %DB_NAME% ...
mysqldump -u%DB_USER% -p%DB_PASS% %DB_NAME% > %OUTPUT_FILE%

if %errorlevel% equ 0 (
    echo Export success! File: %OUTPUT_FILE%
) else (
    echo Export failed. Please check MySQL.
)

pause
