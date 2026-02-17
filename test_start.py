print("Script started")

import os
import sys

print("Setting up paths...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

print("Importing Django...")
try:
    import django
    print(f"Django version: {django.VERSION}")
    django.setup()
    print("Django setup OK")
except Exception as e:
    print(f"Django setup error: {e}")
    import traceback
    traceback.print_exc()

print("Testing database connection...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("Database connection OK")
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()

input("Press Enter to exit...")
