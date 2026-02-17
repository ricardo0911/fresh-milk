@echo off
cd /d c:\Users\root\Desktop\fresh-milk
python manage.py migrate coupons > migrate_output.txt 2>&1
echo Done >> migrate_output.txt
