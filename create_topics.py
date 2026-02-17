"""创建话题数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.posts.models import Topic

topics = [
    {'name': '日常', 'description': '日常分享', 'sort_order': 1},
    {'name': '新品', 'description': '新品体验', 'sort_order': 2},
    {'name': '活动', 'description': '活动分享', 'sort_order': 3},
    {'name': '建议', 'description': '意见建议', 'sort_order': 4},
]

for t in topics:
    obj, created = Topic.objects.get_or_create(name=t['name'], defaults=t)
    status = '创建' if created else '已存在'
    print(f'{status}: {obj.name}')

print('\n话题创建完成!')
