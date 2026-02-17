import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
django.setup()

from apps.comments.models import Comment
from apps.users.models import User

print("=== 评论数据检查 ===")
print(f"评论总数: {Comment.objects.count()}")

comments = Comment.objects.all()[:5]
for c in comments:
    print(f"\n评论ID: {c.id}")
    print(f"  用户: {c.user.username if c.user else '匿名'}")
    print(f"  产品: {c.product.name if c.product else '无'}")
    print(f"  评分: {c.rating}")
    print(f"  内容: {c.content[:50]}...")
    print(f"  商家回复: {c.reply or '无'}")
    print(f"  创建时间: {c.created_at}")

print("\n=== 用户数据检查 ===")
print(f"用户总数: {User.objects.count()}")

# 检查有评论的用户
users_with_comments = User.objects.filter(comments__isnull=False).distinct()
print(f"有评论的用户数: {users_with_comments.count()}")

for u in users_with_comments[:3]:
    comment_count = Comment.objects.filter(user=u).count()
    print(f"  用户 {u.username}: {comment_count} 条评论")
