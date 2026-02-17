import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
django.setup()

from apps.feedback.models import Feedback

print("=== 反馈数据检查 ===")
print(f"反馈总数: {Feedback.objects.count()}")

feedbacks = Feedback.objects.all()[:5]
for f in feedbacks:
    print(f"\n反馈ID: {f.id}")
    print(f"  用户: {f.user.username if f.user else '匿名'}")
    print(f"  类型: {f.get_feedback_type_display()}")
    print(f"  标题: {f.title}")
    print(f"  内容: {f.content[:50]}...")
    print(f"  状态: {f.get_status_display()}")
    print(f"  回复: {f.reply or '无'}")
    print(f"  创建时间: {f.created_at}")
