"""
初始化示例数据脚本
运行: python init_data.py
"""
import os
import sys

# 添加项目目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.notifications.models import Advertisement, Message

User = get_user_model()

def create_users():
    """创建用户"""
    # 创建管理员
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@freshmilk.com',
            password='admin123',
            is_admin=True
        )
        print(f'创建管理员: {admin.username}')
    
    # 创建测试用户
    test_users = [
        {'username': 'user1', 'email': 'user1@test.com', 'phone': '13800138001'},
        {'username': 'user2', 'email': 'user2@test.com', 'phone': '13800138002'},
        {'username': 'user3', 'email': 'user3@test.com', 'phone': '13800138003'},
    ]
    
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                password='test123',
                **user_data
            )
            print(f'创建用户: {user.username}')


def create_categories():
    """创建产品分类"""
    categories = [
        {'name': '纯牛奶', 'icon': '🥛', 'description': '新鲜纯牛奶', 'sort_order': 1},
        {'name': '酸奶', 'icon': '🥄', 'description': '浓郁酸奶', 'sort_order': 2},
        {'name': '低脂奶', 'icon': '💧', 'description': '低脂健康牛奶', 'sort_order': 3},
        {'name': 'A2牛奶', 'icon': '🅰️', 'description': 'A2型蛋白牛奶', 'sort_order': 4},
        {'name': '有机奶', 'icon': '🌿', 'description': '有机牧场牛奶', 'sort_order': 5},
        {'name': '儿童奶', 'icon': '👶', 'description': '儿童专属配方', 'sort_order': 6},
    ]
    
    for cat_data in categories:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f'创建分类: {cat.name}')
    
    return Category.objects.all()


def create_products(categories):
    """创建产品"""
    products_data = [
        # 纯牛奶
        {
            'category': '纯牛奶',
            'name': '悦鲜活鲜牛奶',
            'subtitle': '0.09秒杀菌科技 锁住牛奶原生鲜醇',
            'price': 280.00,
            'original_price': 516.00,
            'specification': '260ml*10瓶 共12期',
            'origin': '山东优质牧场',
            'shelf_life': 7,
            'stock': 100,
            'is_hot': True,
            'is_subscription': True,
        },
        {
            'category': '纯牛奶',
            'name': '悦鲜活畅饮450',
            'subtitle': '0.09秒科学鲜醇 锁住牛奶原生正醇香',
            'price': 304.00,
            'original_price': 412.80,
            'specification': '450ml*8瓶 共4期',
            'origin': '山东优质牧场',
            'shelf_life': 7,
            'stock': 80,
            'is_hot': True,
            'is_subscription': True,
        },
        {
            'category': '纯牛奶',
            'name': '悦鲜活鲜活260',
            'subtitle': '每日鲜送 新鲜直达',
            'price': 720.00,
            'original_price': 1068.00,
            'specification': '260ml*10瓶',
            'origin': '山东优质牧场',
            'shelf_life': 7,
            'stock': 50,
            'is_new': True,
            'is_subscription': True,
        },
        # A2牛奶
        {
            'category': 'A2牛奶',
            'name': '亲和易吸收 认准A2型奶',
            'subtitle': '周期购专享 自选发货时间 效期新鲜 自由退改',
            'price': 280.00,
            'original_price': 360.00,
            'specification': '260ml*10瓶',
            'origin': '澳洲优质牧场',
            'shelf_life': 15,
            'stock': 60,
            'is_hot': True,
            'is_subscription': True,
        },
        {
            'category': 'A2牛奶',
            'name': '亲和易吸收A2型奶畅饮装',
            'subtitle': '大瓶更尽兴',
            'price': 352.00,
            'original_price': 604.80,
            'specification': '450ml*8瓶',
            'origin': '澳洲优质牧场',
            'shelf_life': 15,
            'stock': 40,
            'is_subscription': True,
        },
        # 酸奶
        {
            'category': '酸奶',
            'name': '原味浓醇酸奶',
            'subtitle': '传统工艺发酵 口感浓郁',
            'price': 88.00,
            'original_price': 120.00,
            'specification': '200g*6杯',
            'origin': '内蒙古牧场',
            'shelf_life': 21,
            'stock': 120,
            'is_new': True,
        },
        {
            'category': '酸奶',
            'name': '草莓果粒酸奶',
            'subtitle': '真实草莓果粒 酸甜可口',
            'price': 98.00,
            'original_price': 138.00,
            'specification': '200g*6杯',
            'origin': '内蒙古牧场',
            'shelf_life': 21,
            'stock': 80,
        },
        # 低脂奶
        {
            'category': '低脂奶',
            'name': '低脂高钙牛奶',
            'subtitle': '减脂不减营养 健康之选',
            'price': 158.00,
            'original_price': 220.00,
            'specification': '250ml*12盒',
            'origin': '新疆天山牧场',
            'shelf_life': 180,
            'stock': 200,
        },
        # 有机奶
        {
            'category': '有机奶',
            'name': '有机纯牛奶',
            'subtitle': '有机牧场认证 纯净奶源',
            'price': 268.00,
            'original_price': 380.00,
            'specification': '250ml*12盒',
            'origin': '呼伦贝尔有机牧场',
            'shelf_life': 180,
            'stock': 60,
            'is_hot': True,
        },
        # 儿童奶
        {
            'category': '儿童奶',
            'name': '儿童成长牛奶',
            'subtitle': '添加DHA和钙 助力成长',
            'price': 128.00,
            'original_price': 168.00,
            'specification': '200ml*12盒',
            'origin': '黑龙江牧场',
            'shelf_life': 180,
            'stock': 150,
            'is_new': True,
        },
    ]
    
    category_map = {cat.name: cat for cat in categories}
    
    for prod_data in products_data:
        cat_name = prod_data.pop('category')
        category = category_map.get(cat_name)
        
        if category and not Product.objects.filter(name=prod_data['name']).exists():
            product = Product.objects.create(category=category, **prod_data)
            print(f'创建产品: {product.name}')


def create_advertisements():
    """创建广告"""
    ads = [
        {
            'title': '周期购专享优惠',
            'position': 'home_banner',
            'link_type': 'none',
            'sort_order': 1,
        },
        {
            'title': '新品上市 鲜活260',
            'position': 'home_banner',
            'link_type': 'none',
            'sort_order': 2,
        },
        {
            'title': '会员专属福利',
            'position': 'home_banner',
            'link_type': 'none',
            'sort_order': 3,
        },
    ]
    
    for ad_data in ads:
        ad, created = Advertisement.objects.get_or_create(
            title=ad_data['title'],
            defaults=ad_data
        )
        if created:
            print(f'创建广告: {ad.title}')


def create_messages():
    """创建系统消息"""
    messages = [
        {
            'title': '欢迎使用鲜牛奶订购系统',
            'content': '感谢您选择我们的鲜牛奶订购服务！我们提供新鲜、健康的牛奶产品，每日配送到您家门口。',
            'message_type': 'system',
        },
        {
            'title': '周期购优惠活动',
            'content': '现在订购周期购产品，享受更多优惠！12期起订，每周配送，新鲜直达。',
            'message_type': 'promotion',
        },
        {
            'title': '新品上市：悦鲜活鲜活260',
            'content': '全新悦鲜活鲜活260震撼上市，0.09秒杀菌科技，锁住牛奶原生鲜醇。',
            'message_type': 'new_product',
        },
    ]
    
    for msg_data in messages:
        msg, created = Message.objects.get_or_create(
            title=msg_data['title'],
            defaults=msg_data
        )
        if created:
            print(f'创建消息: {msg.title}')


if __name__ == '__main__':
    print('开始初始化数据...')
    print('=' * 50)
    
    create_users()
    print('-' * 50)
    
    categories = create_categories()
    print('-' * 50)
    
    create_products(categories)
    print('-' * 50)
    
    create_advertisements()
    print('-' * 50)
    
    create_messages()
    print('-' * 50)
    
    print('=' * 50)
    print('数据初始化完成!')
    print(f'管理员账号: admin / admin123')
    print(f'测试用户: user1, user2, user3 / test123')
