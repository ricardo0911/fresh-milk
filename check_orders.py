#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from apps.orders.models import Order

print(f'订单总数: {Order.objects.count()}')
orders = Order.objects.all()[:10]
if orders:
    for o in orders:
        print(f'  - {o.order_no} | 状态: {o.status} | 金额: {o.pay_amount} | 创建时间: {o.created_at}')

from django.utils import timezone
from datetime import timedelta
start = timezone.now().date() - timedelta(days=7)

print(f"Checking orders since {start}")
# Test 1: Date lookup (needs TZ tables)
cnt_date = Order.objects.filter(created_at__date__gte=start).count()
print(f"Filter by DATE count: {cnt_date}")

# Test 2: Datetime lookup (pure comparison)
from datetime import datetime, time
start_dt = timezone.make_aware(datetime.combine(start, time.min))
cnt_dt = Order.objects.filter(created_at__gte=start_dt).count()
print(f"Filter by DATETIME count: {cnt_dt}")
