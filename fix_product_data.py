"""
修复产品数据脚本
1. 修复 is_hot 字段类型不一致问题（字符串 "false" -> 布尔值 False）
2. 批量上架所有商品
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.products.models import Product
from django.db import connection


def check_data():
    """检查当前数据状态"""
    print("=" * 50)
    print("当前数据状态检查")
    print("=" * 50)

    products = Product.objects.all()
    print(f"\n总产品数: {products.count()}")

    # 检查 is_active 状态
    active_count = products.filter(is_active=True).count()
    inactive_count = products.filter(is_active=False).count()
    print(f"上架商品: {active_count}")
    print(f"下架商品: {inactive_count}")

    # 检查 is_hot 状态
    hot_count = products.filter(is_hot=True).count()
    not_hot_count = products.filter(is_hot=False).count()
    print(f"热门商品: {hot_count}")
    print(f"非热门商品: {not_hot_count}")

    # 检查原始数据库值
    print("\n原始数据库值检查:")
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, is_hot, is_active FROM products")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID={row[0]}, name={row[1]}, is_hot={row[2]} (type={type(row[2]).__name__}), is_active={row[3]}")

    return products


def fix_is_hot_field():
    """修复 is_hot 字段类型问题"""
    print("\n" + "=" * 50)
    print("修复 is_hot 字段")
    print("=" * 50)

    # 使用原始 SQL 检查是否有字符串类型的值
    with connection.cursor() as cursor:
        # SQLite 中布尔值存储为 0/1，如果是字符串会不同
        cursor.execute("SELECT id, name, is_hot FROM products WHERE typeof(is_hot) = 'text'")
        text_rows = cursor.fetchall()

        if text_rows:
            print(f"发现 {len(text_rows)} 条 is_hot 为字符串类型的记录:")
            for row in text_rows:
                print(f"  ID={row[0]}, name={row[1]}, is_hot='{row[2]}'")

            # 修复这些记录
            cursor.execute("""
                UPDATE products
                SET is_hot = CASE
                    WHEN is_hot = 'true' OR is_hot = '1' OR is_hot = 'True' THEN 1
                    ELSE 0
                END
                WHERE typeof(is_hot) = 'text'
            """)
            print(f"已修复 {cursor.rowcount} 条记录")
        else:
            print("未发现字符串类型的 is_hot 值")

    # 同样检查 is_active
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, is_active FROM products WHERE typeof(is_active) = 'text'")
        text_rows = cursor.fetchall()

        if text_rows:
            print(f"\n发现 {len(text_rows)} 条 is_active 为字符串类型的记录:")
            for row in text_rows:
                print(f"  ID={row[0]}, name={row[1]}, is_active='{row[2]}'")

            cursor.execute("""
                UPDATE products
                SET is_active = CASE
                    WHEN is_active = 'true' OR is_active = '1' OR is_active = 'True' THEN 1
                    ELSE 0
                END
                WHERE typeof(is_active) = 'text'
            """)
            print(f"已修复 {cursor.rowcount} 条记录")


def batch_activate_products():
    """批量上架所有商品"""
    print("\n" + "=" * 50)
    print("批量上架商品")
    print("=" * 50)

    inactive_products = Product.objects.filter(is_active=False)
    count = inactive_products.count()

    if count > 0:
        print(f"发现 {count} 个下架商品，正在上架...")
        updated = inactive_products.update(is_active=True)
        print(f"已上架 {updated} 个商品")
    else:
        print("没有需要上架的商品")


def main():
    print("\n" + "=" * 50)
    print("产品数据修复脚本")
    print("=" * 50)

    # 1. 检查当前数据状态
    check_data()

    # 2. 修复 is_hot 字段类型
    fix_is_hot_field()

    # 3. 批量上架商品
    batch_activate_products()

    # 4. 再次检查数据状态
    print("\n" + "=" * 50)
    print("修复后数据状态")
    print("=" * 50)
    check_data()

    print("\n修复完成！")


if __name__ == '__main__':
    main()
