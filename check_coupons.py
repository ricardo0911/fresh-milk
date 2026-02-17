"""检查并创建可兑换优惠券"""
import os
import sys
import django

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.coupons.models import Coupon
from django.utils import timezone
from datetime import timedelta

# 输出到文件
with open('coupon_result.txt', 'w', encoding='utf-8') as f:
    # 检查现有优惠券
    coupons = Coupon.objects.all()
    f.write(f'现有优惠券数量: {coupons.count()}\n')

    for c in coupons:
        f.write(f'  - {c.name}: is_exchangeable={c.is_exchangeable}, points={c.points_required}, status={c.status}\n')

    # 检查可兑换的优惠券
    exchangeable = Coupon.objects.filter(
        status='active',
        is_exchangeable=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )
    f.write(f'\n可兑换优惠券数量: {exchangeable.count()}\n')

    # 如果没有可兑换优惠券，创建测试数据
    if exchangeable.count() == 0:
        f.write('\n创建测试优惠券...\n')
        now = timezone.now()
        end_time = now + timedelta(days=30)

        test_coupons = [
            {
                'name': '5元优惠券',
                'type': 'amount',
                'discount_amount': 5,
                'min_amount': 30,
                'points_required': 50,
                'is_exchangeable': True,
                'description': '满30元可用',
            },
            {
                'name': '10元优惠券',
                'type': 'amount',
                'discount_amount': 10,
                'min_amount': 50,
                'points_required': 100,
                'is_exchangeable': True,
                'description': '满50元可用',
            },
            {
                'name': '20元优惠券',
                'type': 'amount',
                'discount_amount': 20,
                'min_amount': 100,
                'points_required': 200,
                'is_exchangeable': True,
                'description': '满100元可用',
            },
        ]

        for data in test_coupons:
            coupon = Coupon.objects.create(
                name=data['name'],
                type=data['type'],
                discount_amount=data['discount_amount'],
                min_amount=data['min_amount'],
                points_required=data['points_required'],
                is_exchangeable=data['is_exchangeable'],
                description=data['description'],
                status='active',
                start_time=now,
                end_time=end_time,
            )
            f.write(f'  创建: {coupon.name} (需要{coupon.points_required}积分)\n')

        f.write('\n优惠券创建完成!\n')
    else:
        f.write('\n已有可兑换优惠券，无需创建\n')

print('Done - check coupon_result.txt')
