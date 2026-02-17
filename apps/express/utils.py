"""
快递服务工厂
"""
from typing import Optional
from .services import ExpressService, SFExpressService, YTOExpressService, MockExpressService
from .models import ExpressCompany

# 演示模式开关 - 设为 True 使用模拟数据，适合毕设演示
DEMO_MODE = True


def get_express_service(company_code: str) -> Optional[ExpressService]:
    """
    获取快递服务实例

    Args:
        company_code: 快递公司代码 (SF/YTO)

    Returns:
        ExpressService: 快递服务实例
    """
    # 演示模式：返回模拟服务
    if DEMO_MODE:
        return MockExpressService()

    try:
        company = ExpressCompany.objects.get(code=company_code, is_active=True)
    except ExpressCompany.DoesNotExist:
        return None

    config = {
        'app_id': company.app_id,
        'app_key': company.app_key,
        'app_secret': company.app_secret,
        'customer_code': company.customer_code,
        'api_url': company.api_url,
    }

    if company_code == 'SF':
        return SFExpressService(config)
    elif company_code == 'YTO':
        return YTOExpressService(config)
    else:
        return None


def get_sender_info(company_code: str) -> dict:
    """
    获取发件人信息

    Args:
        company_code: 快递公司代码

    Returns:
        dict: 发件人信息
    """
    # 演示模式：返回模拟发件人信息
    if DEMO_MODE:
        return {
            'name': '鲜奶配送中心',
            'phone': '13800138000',
            'province': '上海市',
            'city': '上海市',
            'district': '浦东新区',
            'address': '张江高科技园区博云路2号',
        }

    try:
        company = ExpressCompany.objects.get(code=company_code, is_active=True)
        return {
            'name': company.sender_name,
            'phone': company.sender_phone,
            'province': company.sender_province,
            'city': company.sender_city,
            'district': company.sender_district,
            'address': company.sender_address,
        }
    except ExpressCompany.DoesNotExist:
        return {}
