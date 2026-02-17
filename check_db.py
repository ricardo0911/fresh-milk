#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

django.setup()

from django.db import connection

cursor = connection.cursor()

try:
    cursor.execute("SELECT 1 FROM comments LIMIT 1")
    print("OK: comments table exists")
except Exception as e:
    print(f"ERROR: comments table not found: {e}")

try:
    cursor.execute("SELECT 1 FROM comment_likes LIMIT 1")
    print("OK: comment_likes table exists")
except Exception as e:
    print(f"ERROR: comment_likes table not found: {e}")

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\nTotal tables: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")
