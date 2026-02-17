"""添加可兑换优惠券数据"""
from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def create_exchangeable_coupons(apps, schema_editor):
    Coupon = apps.get_model('coupons', 'Coupon')

    now = timezone.now()
    end_time = now + timedelta(days=365)

    coupons_data = [
        {
            'code': 'EXCHANGE5',
            'name': '5元优惠券',
            'type': 'amount',
            'discount_amount': 5,
            'min_amount': 30,
            'points_required': 50,
            'is_exchangeable': True,
            'description': '满30元可用',
        },
        {
            'code': 'EXCHANGE10',
            'name': '10元优惠券',
            'type': 'amount',
            'discount_amount': 10,
            'min_amount': 50,
            'points_required': 100,
            'is_exchangeable': True,
            'description': '满50元可用',
        },
        {
            'code': 'EXCHANGE20',
            'name': '20元优惠券',
            'type': 'amount',
            'discount_amount': 20,
            'min_amount': 100,
            'points_required': 200,
            'is_exchangeable': True,
            'description': '满100元可用',
        },
    ]

    for data in coupons_data:
        if not Coupon.objects.filter(code=data['code']).exists():
            Coupon.objects.create(
                code=data['code'],
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


def remove_exchangeable_coupons(apps, schema_editor):
    Coupon = apps.get_model('coupons', 'Coupon')
    Coupon.objects.filter(code__in=['EXCHANGE5', 'EXCHANGE10', 'EXCHANGE20']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0002_coupon_exchange_limit_coupon_exchanged_count_and_more'),
    ]

    operations = [
        migrations.RunPython(create_exchangeable_coupons, remove_exchangeable_coupons),
    ]
