#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查订单快递信息"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from apps.orders.models import Order

print('=== 所有已发货订单 ===')
shipped_orders = Order.objects.filter(status='shipped')
print(f'已发货订单数: {shipped_orders.count()}')

for o in shipped_orders:
    print(f'订单: {o.order_no}')
    print(f'  express_company: [{o.express_company}]')
    print(f'  express_no: [{o.express_no}]')
    print(f'  express_status: [{o.express_status}]')
    print('---')
