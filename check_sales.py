"""检查销售数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order

today = timezone.now().date()
start_date = today - timedelta(days=6)

print(f"检查日期范围: {start_date} ~ {today}")
print("-" * 50)

# 所有订单
all_orders = Order.objects.all()
print(f"订单总数: {all_orders.count()}")

# 按状态统计
print("\n按状态统计:")
for status, label in Order.STATUS_CHOICES:
    count = Order.objects.filter(status=status).count()
    if count > 0:
        print(f"  {label}({status}): {count}")

# 有效订单（用于统计销售额的）
valid_statuses = ['paid', 'shipped', 'delivered', 'completed']
valid_orders = Order.objects.filter(status__in=valid_statuses)
print(f"\n有效订单数（paid/shipped/delivered/completed）: {valid_orders.count()}")

# 最近7天的有效订单
recent_orders = valid_orders.filter(created_at__date__gte=start_date)
print(f"最近7天有效订单数: {recent_orders.count()}")

# 显示最近的订单
print("\n最近10个订单:")
for order in Order.objects.all()[:10]:
    print(f"  {order.order_no} | 状态:{order.status} | 金额:{order.pay_amount} | 创建:{order.created_at.date()}")

# 计算销售额
from django.db.models import Sum
total = valid_orders.aggregate(total=Sum('pay_amount'))['total'] or 0
recent_total = recent_orders.aggregate(total=Sum('pay_amount'))['total'] or 0
print(f"\n总销售额: ¥{total}")
print(f"最近7天销售额: ¥{recent_total}")
