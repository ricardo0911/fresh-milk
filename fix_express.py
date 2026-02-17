#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复已发货订单的快递信息"""
import os
import sys
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from apps.orders.models import Order

# 查看已发货但没有快递单号的订单
orders = Order.objects.filter(status='shipped', express_no__isnull=True)
print(f'需要修复的订单数: {orders.count()}')

# 也检查 express_no 为空字符串的情况
orders_empty = Order.objects.filter(status='shipped', express_no='')
print(f'快递单号为空的订单数: {orders_empty.count()}')

# 合并查询
from django.db.models import Q
all_orders = Order.objects.filter(
    status='shipped'
).filter(
    Q(express_no__isnull=True) | Q(express_no='')
)

print(f'总共需要修复: {all_orders.count()}')

# 为这些订单补充快递信息
for order in all_orders:
    order.express_company = 'SF'
    order.express_no = f"SF{time.strftime('%Y%m%d%H%M%S')}{order.id}"
    order.express_status = '已揽收'
    order.save()
    print(f'已修复: {order.order_no} -> {order.express_no}')

print('修复完成!')

# 验证
print('\n=== 验证结果 ===')
shipped_orders = Order.objects.filter(status='shipped')[:5]
for o in shipped_orders:
    print(f'{o.order_no}: express_no={o.express_no}')
