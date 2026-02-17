#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新商品详情内容
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from apps.products.models import Product

# 商品详情模板
PRODUCT_DETAILS = {
    '悦鲜活': {
        'description': '悦鲜活鲜牛奶，采用优质牧场奶源，72°C巴氏杀菌工艺，保留更多活性营养。每日新鲜配送，从牧场到餐桌不超过24小时。',
        'detail': '''【产品特点】
• 优质奶源：精选山东优质牧场，奶牛自然放牧
• 巴氏杀菌：72°C低温杀菌，保留活性营养
• 新鲜直达：每日凌晨生产，当日配送到家
• 营养丰富：富含优质蛋白质和钙质

【营养成分】(每100ml)
• 能量：272kJ
• 蛋白质：3.2g
• 脂肪：3.6g
• 碳水化合物：4.8g
• 钙：120mg

【储存方式】
2-6°C冷藏保存，开封后请尽快饮用

【温馨提示】
本品为鲜牛奶，请注意保质期，建议冷藏后口感更佳'''
    },
    '白荷': {
        'description': '白荷花牛A2纯牛奶，甄选A2奶牛，只含A2型β-酪蛋白，更亲和人体，易于消化吸收。适合全家人饮用。',
        'detail': '''【产品特点】
• A2奶源：100%A2型β-酪蛋白，亲和人体
• 优质牧场：自有生态牧场，科学养殖
• 纯净配方：无添加，纯天然
• 易于吸收：更适合亚洲人体质

【营养成分】(每100ml)
• 能量：280kJ
• 蛋白质：3.3g
• 脂肪：3.8g
• 碳水化合物：4.9g
• 钙：125mg

【储存方式】
2-6°C冷藏保存

【适宜人群】
全家适用，特别适合肠胃敏感人群'''
    },
    '酸奶': {
        'description': '精选优质生牛乳发酵，添加活性益生菌，口感醇厚细腻，酸甜适中，助力肠道健康。',
        'detail': '''【产品特点】
• 活性益生菌：添加双歧杆菌，呵护肠道
• 优质奶源：100%生牛乳发酵
• 口感醇厚：质地细腻，酸甜可口
• 营养均衡：富含蛋白质和钙

【营养成分】(每100g)
• 能量：350kJ
• 蛋白质：3.0g
• 脂肪：3.2g
• 碳水化合物：12g
• 钙：110mg

【储存方式】
2-6°C冷藏保存，开封后24小时内食用完毕

【食用建议】
早餐搭配或餐后食用，风味更佳'''
    },
    '儿童': {
        'description': '专为3-12岁儿童研发，添加DHA、钙铁锌等成长所需营养素，助力儿童健康成长。',
        'detail': '''【产品特点】
• 专业配方：针对儿童成长需求研发
• 营养强化：添加DHA、钙、铁、锌
• 口感适宜：甜度适中，孩子爱喝
• 安全放心：无防腐剂，无香精

【营养成分】(每100ml)
• 能量：290kJ
• 蛋白质：3.0g
• DHA：15mg
• 钙：130mg
• 铁：1.5mg
• 锌：0.8mg

【储存方式】
常温密封保存，开封后冷藏

【适宜人群】
3-12岁儿童'''
    },
    '有机': {
        'description': '通过有机认证，奶牛食用有机牧草，不使用抗生素和激素，从源头保证纯净品质。',
        'detail': '''【产品特点】
• 有机认证：通过国家有机产品认证
• 生态牧场：奶牛自然放牧，食用有机牧草
• 零添加：不使用抗生素、激素
• 纯净品质：从牧场到餐桌全程可追溯

【营养成分】(每100ml)
• 能量：275kJ
• 蛋白质：3.3g
• 脂肪：3.7g
• 碳水化合物：4.8g
• 钙：122mg

【储存方式】
2-6°C冷藏保存

【品质保证】
每批次产品均可扫码溯源'''
    },
    '脱脂': {
        'description': '脱脂高钙牛奶，脂肪含量≤0.5%，保留丰富钙质和蛋白质，适合控制体重人群。',
        'detail': '''【产品特点】
• 低脂健康：脂肪含量≤0.5%
• 高钙配方：钙含量比普通牛奶高30%
• 优质蛋白：保留完整蛋白质营养
• 清爽口感：口感清淡不腻

【营养成分】(每100ml)
• 能量：150kJ
• 蛋白质：3.4g
• 脂肪：≤0.5g
• 碳水化合物：5.0g
• 钙：150mg

【储存方式】
2-6°C冷藏保存

【适宜人群】
健身人群、控制体重人群、中老年人'''
    }
}

# 默认详情
DEFAULT_DETAIL = {
    'description': '精选优质奶源，采用先进工艺加工，营养丰富，口感醇厚，是您日常补充营养的理想选择。',
    'detail': '''【产品特点】
• 优质奶源：精选优质牧场
• 营养丰富：富含蛋白质和钙
• 口感醇厚：新鲜美味

【营养成分】(每100ml)
• 能量：270kJ
• 蛋白质：3.2g
• 脂肪：3.5g
• 钙：120mg

【储存方式】
请按包装说明储存

【温馨提示】
开封后请尽快饮用'''
}

def main():
    products = Product.objects.all()
    print(f"Updating {products.count()} products...")

    for product in products:
        # 根据产品名称匹配详情模板
        detail_data = DEFAULT_DETAIL
        for keyword, data in PRODUCT_DETAILS.items():
            if keyword in product.name:
                detail_data = data
                break

        product.description = detail_data['description']
        product.detail = detail_data['detail']
        product.save(update_fields=['description', 'detail'])
        print(f"Updated: {product.name}")

    print("\nDone!")

if __name__ == '__main__':
    main()
