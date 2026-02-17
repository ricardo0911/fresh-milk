@echo off
cd /d c:\Users\root\Desktop\fresh-milk
C:\Param\MySQL\bin\mysql.exe -uroot -proot fresh_milk_db < insert_coupons.sql > sql_result.txt 2>&1
echo Done
type sql_result.txt
pause
