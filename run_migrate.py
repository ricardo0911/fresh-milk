#!/usr/bin/env python
import os
import sys
import django

# 设置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 设置项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 初始化 Django
django.setup()

# 运行迁移
from django.core.management import call_command
try:
    call_command('migrate', verbosity=2)
    print("\n✓ 迁移成功完成！")
except Exception as e:
    print(f"\n✗ 迁移失败: {e}")
    import traceback
    traceback.print_exc()
