#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

django.setup()

from apps.products.models import Product
from django.db import connection

print("=== Product Data Check ===")
print(f"Total products: {Product.objects.count()}")
print(f"Active (is_active=True): {Product.objects.filter(is_active=True).count()}")
print(f"Inactive (is_active=False): {Product.objects.filter(is_active=False).count()}")
print(f"Hot (is_hot=True): {Product.objects.filter(is_hot=True).count()}")
print(f"Not Hot (is_hot=False): {Product.objects.filter(is_hot=False).count()}")

print("\n=== Raw DB Values ===")
with connection.cursor() as cursor:
    cursor.execute("SELECT id, name, is_hot, is_active FROM products LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID={row[0]}, name={row[1]}, is_hot={row[2]} (type={type(row[2]).__name__}), is_active={row[3]} (type={type(row[3]).__name__})")
