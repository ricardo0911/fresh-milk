#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成商品占位图片并更新数据库
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from PIL import Image, ImageDraw, ImageFont
from apps.products.models import Product

# 牛奶产品的颜色方案
COLORS = [
    ('#E8F5E9', '#2E7D32'),  # 浅绿/深绿
    ('#E3F2FD', '#1565C0'),  # 浅蓝/深蓝
    ('#FFF3E0', '#E65100'),  # 浅橙/深橙
    ('#F3E5F5', '#7B1FA2'),  # 浅紫/深紫
    ('#FFEBEE', '#C62828'),  # 浅红/深红
    ('#E0F7FA', '#00838F'),  # 浅青/深青
    ('#FFF8E1', '#FF8F00'),  # 浅黄/深黄
    ('#E8EAF6', '#283593'),  # 浅靛/深靛
    ('#FCE4EC', '#AD1457'),  # 浅粉/深粉
    ('#F1F8E9', '#558B2F'),  # 浅草绿/深草绿
]

def create_placeholder_image(product_id, product_name, width=400, height=400):
    """创建占位图片"""
    bg_color, text_color = COLORS[(product_id - 1) % len(COLORS)]

    # 创建图片
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # 绘制牛奶瓶图标（简单的形状）
    center_x, center_y = width // 2, height // 2 - 30

    # 瓶身
    bottle_width = 80
    bottle_height = 120
    draw.rounded_rectangle(
        [center_x - bottle_width//2, center_y - bottle_height//2,
         center_x + bottle_width//2, center_y + bottle_height//2],
        radius=15,
        fill='white',
        outline=text_color,
        width=3
    )

    # 瓶盖
    cap_width = 40
    cap_height = 25
    draw.rectangle(
        [center_x - cap_width//2, center_y - bottle_height//2 - cap_height,
         center_x + cap_width//2, center_y - bottle_height//2],
        fill=text_color
    )

    # 添加产品名称
    try:
        font = ImageFont.truetype("msyh.ttc", 24)
    except:
        try:
            font = ImageFont.truetype("simhei.ttf", 24)
        except:
            font = ImageFont.load_default()

    # 截取产品名称前几个字
    short_name = product_name[:6] if len(product_name) > 6 else product_name

    # 计算文字位置
    bbox = draw.textbbox((0, 0), short_name, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = center_y + bottle_height//2 + 20

    draw.text((text_x, text_y), short_name, fill=text_color, font=font)

    return img

def main():
    media_dir = os.path.join(BASE_DIR, 'media')
    covers_dir = os.path.join(media_dir, 'products', 'covers')

    os.makedirs(covers_dir, exist_ok=True)

    products = Product.objects.all()
    print(f"Found {products.count()} products")

    for product in products:
        # 创建封面图
        img = create_placeholder_image(product.id, product.name)

        # 保存图片
        filename = f'product_{product.id}.jpg'
        filepath = os.path.join(covers_dir, filename)
        img.save(filepath, 'JPEG', quality=90)

        # 更新数据库
        product.cover_image = f'products/covers/{filename}'
        product.save(update_fields=['cover_image'])

        print(f"Created image for: {product.id} - {product.name}")

    print("\nDone! All product images created.")

if __name__ == '__main__':
    main()
