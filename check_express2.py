#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    import django
    django.setup()

    from apps.orders.models import Order

    print("=== Check Orders ===")
    shipped_orders = Order.objects.filter(status='shipped')
    print("Shipped count:", shipped_orders.count())

    for o in shipped_orders:
        print("Order:", o.order_no)
        print("  express_company:", o.express_company)
        print("  express_no:", o.express_no)
        print("---")

except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()
