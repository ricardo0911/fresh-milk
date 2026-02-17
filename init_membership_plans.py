"""
初始化会员套餐数据
运行方式: python manage.py shell < init_membership_plans.py
或者: python init_membership_plans.py
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import MembershipPlan

# 会员套餐数据
plans_data = [
    {
        'name': '银卡月卡',
        'level': 'silver',
        'duration_days': 30,
        'original_price': 29.00,
        'price': 19.00,
        'description': '银卡会员月度套餐，享受95折优惠',
        'benefits': ['全场商品95折', '专属客服', '生日礼券'],
        'is_active': True,
        'sort_order': 1,
    },
    {
        'name': '金卡季卡',
        'level': 'gold',
        'duration_days': 90,
        'original_price': 99.00,
        'price': 69.00,
        'description': '金卡会员季度套餐，享受9折优惠',
        'benefits': ['全场商品9折', '专属客服', '生日礼券', '积分1.5倍'],
        'is_active': True,
        'sort_order': 2,
    },
    {
        'name': '铂金年卡',
        'level': 'platinum',
        'duration_days': 365,
        'original_price': 299.00,
        'price': 199.00,
        'description': '铂金会员年度套餐，享受85折优惠',
        'benefits': ['全场商品85折', '专属客服', '生日礼券', '积分2倍', '优先配送', '专属活动'],
        'is_active': True,
        'sort_order': 3,
    },
]

def init_plans():
    """初始化会员套餐"""
    created_count = 0
    updated_count = 0

    for plan_data in plans_data:
        plan, created = MembershipPlan.objects.update_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            created_count += 1
            print(f'创建套餐: {plan.name}')
        else:
            updated_count += 1
            print(f'更新套餐: {plan.name}')

    print(f'\n完成! 创建 {created_count} 个, 更新 {updated_count} 个')

if __name__ == '__main__':
    init_plans()
