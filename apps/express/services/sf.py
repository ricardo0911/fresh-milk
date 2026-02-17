"""
顺丰速运API对接

顺丰开放平台文档: https://open.sf-express.com/

需要申请:
1. 顺丰开放平台账号
2. 月结账号（用于运费结算）
3. 获取 partner_id 和 checkword
"""
import json
import time
import uuid
import hashlib
import base64
import requests
from typing import List
from .base import ExpressService, ExpressResult, TraceResult, TraceInfo


class SFExpressService(ExpressService):
    """顺丰速运服务"""

    # 顺丰API地址
    PROD_URL = 'https://bspgw.sf-express.com/std/service'
    TEST_URL = 'https://sfapi-sbox.sf-express.com/std/service'

    def __init__(self, config: dict):
        super().__init__(config)
        self.partner_id = config.get('app_id', '')  # 顾客编码
        self.checkword = config.get('app_secret', '')  # 校验码
        self.monthly_card = config.get('customer_code', '')  # 月结卡号
        self.api_url = config.get('api_url', '') or self.PROD_URL

    def _sign(self, msg_data: str, timestamp: str) -> str:
        """生成签名"""
        text = f"{msg_data}{timestamp}{self.checkword}"
        md5_hash = hashlib.md5(text.encode('utf-8')).digest()
        return base64.b64encode(md5_hash).decode('utf-8')

    def _request(self, service_code: str, msg_data: dict) -> dict:
        """发送请求到顺丰API"""
        timestamp = str(int(time.time()))
        msg_data_str = json.dumps(msg_data, ensure_ascii=False)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        data = {
            'partnerID': self.partner_id,
            'requestID': uuid.uuid4().hex,
            'serviceCode': service_code,
            'timestamp': timestamp,
            'msgDigest': self._sign(msg_data_str, timestamp),
            'msgData': msg_data_str
        }

        try:
            response = requests.post(self.api_url, data=data, headers=headers, timeout=30)
            result = response.json()
            return result
        except Exception as e:
            return {'apiResultCode': 'ERROR', 'apiErrorMsg': str(e)}

    def create_order(
        self,
        order_no: str,
        sender: dict,
        receiver: dict,
        goods: List[dict],
        remark: str = ''
    ) -> ExpressResult:
        """
        创建顺丰快递订单

        顺丰下单接口: EXP_RECE_CREATE_ORDER
        """
        # 构建商品信息
        cargo_details = []
        for item in goods:
            cargo_details.append({
                'name': item.get('name', '鲜奶'),
                'count': item.get('quantity', 1)
            })

        msg_data = {
            'language': 'zh-CN',
            'orderId': order_no,
            'cargoDetails': cargo_details,
            'monthlyCard': self.monthly_card,
            'payMethod': 1,  # 1-寄方付 2-收方付 3-第三方付
            'expressTypeId': 2,  # 2-顺丰标快
            'isReturnRoutelabel': 1,  # 返回路由标签
            'contactInfoList': [
                {
                    'contactType': 1,  # 寄件方
                    'contact': sender.get('name', ''),
                    'tel': sender.get('phone', ''),
                    'province': sender.get('province', ''),
                    'city': sender.get('city', ''),
                    'county': sender.get('district', ''),
                    'address': sender.get('address', '')
                },
                {
                    'contactType': 2,  # 收件方
                    'contact': receiver.get('name', ''),
                    'tel': receiver.get('phone', ''),
                    'province': receiver.get('province', ''),
                    'city': receiver.get('city', ''),
                    'county': receiver.get('district', ''),
                    'address': receiver.get('address', '')
                }
            ],
            'remark': remark
        }

        result = self._request('EXP_RECE_CREATE_ORDER', msg_data)

        if result.get('apiResultCode') == 'A1000':
            # 成功
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)

            return ExpressResult(
                success=True,
                express_no=api_result.get('waybillNoInfoList', [{}])[0].get('waybillNo', ''),
                message='下单成功',
                data=api_result
            )
        else:
            return ExpressResult(
                success=False,
                message=result.get('apiErrorMsg', '下单失败'),
                data=result
            )

    def query_trace(self, express_no: str) -> TraceResult:
        """
        查询顺丰物流轨迹

        顺丰路由查询接口: EXP_RECE_SEARCH_ROUTES
        """
        msg_data = {
            'language': 'zh-CN',
            'trackingType': 1,  # 1-根据顺丰运单号查询
            'trackingNumber': [express_no],
            'methodType': 1  # 1-标准路由查询
        }

        result = self._request('EXP_RECE_SEARCH_ROUTES', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)

            route_resps = api_result.get('routeResps', [])
            if not route_resps:
                return TraceResult(success=True, status='created', traces=[], message='暂无物流信息')

            routes = route_resps[0].get('routes', [])
            traces = []
            current_status = 'created'

            for route in routes:
                op_code = route.get('opCode', '')
                # 根据操作码判断状态
                if op_code in ['50', '51']:  # 揽收
                    current_status = 'collected'
                elif op_code in ['30', '31', '36']:  # 运输
                    current_status = 'in_transit'
                elif op_code in ['44', '45']:  # 派送
                    current_status = 'delivering'
                elif op_code == '80':  # 签收
                    current_status = 'signed'

                traces.append(TraceInfo(
                    time=route.get('acceptTime', ''),
                    status=op_code,
                    description=route.get('remark', ''),
                    location=route.get('acceptAddress', '')
                ))

            return TraceResult(
                success=True,
                status=current_status,
                traces=traces,
                message='查询成功'
            )
        else:
            return TraceResult(
                success=False,
                message=result.get('apiErrorMsg', '查询失败')
            )

    def cancel_order(self, express_no: str) -> ExpressResult:
        """
        取消顺丰订单

        顺丰取消订单接口: EXP_RECE_UPDATE_ORDER
        """
        msg_data = {
            'language': 'zh-CN',
            'orderId': express_no,
            'dealType': 2  # 2-取消订单
        }

        result = self._request('EXP_RECE_UPDATE_ORDER', msg_data)

        if result.get('apiResultCode') == 'A1000':
            return ExpressResult(
                success=True,
                express_no=express_no,
                message='取消成功'
            )
        else:
            return ExpressResult(
                success=False,
                express_no=express_no,
                message=result.get('apiErrorMsg', '取消失败')
            )

    def get_price(self, sender: dict, receiver: dict, weight: float = 1.0) -> dict:
        """
        查询运费

        顺丰运费查询接口: EXP_RECE_SEARCH_PRICE
        """
        msg_data = {
            'searchPrice': {
                'srcProvinceName': sender.get('province', ''),
                'srcCityName': sender.get('city', ''),
                'srcCountyName': sender.get('district', ''),
                'destProvinceName': receiver.get('province', ''),
                'destCityName': receiver.get('city', ''),
                'destCountyName': receiver.get('district', ''),
                'weight': weight,
                'expressTypeId': 2  # 顺丰标快
            }
        }

        result = self._request('EXP_RECE_SEARCH_PRICE', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)
            return {
                'success': True,
                'price': api_result.get('priceTax', 0),
                'data': api_result
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '查询失败')
            }

    def get_waybill_image(self, express_no: str, order_no: str = '') -> dict:
        """
        获取电子面单图片

        顺丰面单打印接口: EXP_RECE_SEARCH_WAYBILL_IMAGE
        返回面单的base64图片数据
        """
        msg_data = {
            'language': 'zh-CN',
            'waybillNo': express_no,
            'orderId': order_no,
            'imageType': 1,  # 1-PNG 2-PDF
            'imageSize': '180x180'  # 面单尺寸
        }

        result = self._request('EXP_RECE_SEARCH_WAYBILL_IMAGE', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)

            images = api_result.get('images', [])
            if images:
                return {
                    'success': True,
                    'image_data': images[0].get('image', ''),
                    'image_type': 'png',
                    'data': api_result
                }
            return {
                'success': False,
                'message': '未获取到面单图片'
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '获取面单失败')
            }

    def print_waybill(self, express_no: str, order_no: str = '') -> dict:
        """
        获取面单打印数据（云打印）

        顺丰云打印接口: COM_RECE_CLOUD_PRINT_WAYBILLS
        返回可直接打印的面单数据
        """
        msg_data = {
            'templateCode': 'fm_150_standard_HNQYJHYXGS',  # 标准模板
            'version': '2.0',
            'fileType': 'pdf',
            'sync': True,
            'documents': [{
                'masterWaybillNo': express_no,
                'orderId': order_no
            }]
        }

        result = self._request('COM_RECE_CLOUD_PRINT_WAYBILLS', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)

            files = api_result.get('obj', {}).get('files', [])
            if files:
                return {
                    'success': True,
                    'pdf_url': files[0].get('url', ''),
                    'pdf_token': files[0].get('token', ''),
                    'data': api_result
                }
            return {
                'success': False,
                'message': '未获取到打印数据'
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '获取打印数据失败')
            }

    def book_pickup(
        self,
        express_no: str,
        pickup_time: str = '',
        contact_name: str = '',
        contact_phone: str = '',
        address: str = '',
        remark: str = ''
    ) -> dict:
        """
        预约上门取件

        顺丰预约取件接口: EXP_RECE_CREATE_PICKUP

        Args:
            express_no: 快递单号
            pickup_time: 预约取件时间，格式 "2026-01-29 14:00:00"
            contact_name: 联系人姓名
            contact_phone: 联系人电话
            address: 取件地址
            remark: 备注
        """
        msg_data = {
            'language': 'zh-CN',
            'orderId': express_no,
            'expectPickupTime': pickup_time,
            'contactName': contact_name,
            'contactPhone': contact_phone,
            'pickupAddress': address,
            'remark': remark or '请准时上门取件'
        }

        result = self._request('EXP_RECE_CREATE_PICKUP', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)
            return {
                'success': True,
                'pickup_code': api_result.get('pickupCode', ''),
                'message': '预约成功，快递员将在预约时间上门取件',
                'data': api_result
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '预约取件失败')
            }

    def cancel_pickup(self, express_no: str) -> dict:
        """
        取消预约取件

        顺丰取消预约接口: EXP_RECE_CANCEL_PICKUP
        """
        msg_data = {
            'language': 'zh-CN',
            'orderId': express_no
        }

        result = self._request('EXP_RECE_CANCEL_PICKUP', msg_data)

        if result.get('apiResultCode') == 'A1000':
            return {
                'success': True,
                'message': '取消预约成功'
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '取消预约失败')
            }

    def get_pickup_time(self, address: str) -> dict:
        """
        查询可预约取件时间段

        顺丰查询可预约时间接口: EXP_RECE_SEARCH_PICKUP_TIME
        """
        msg_data = {
            'language': 'zh-CN',
            'address': address
        }

        result = self._request('EXP_RECE_SEARCH_PICKUP_TIME', msg_data)

        if result.get('apiResultCode') == 'A1000':
            api_result = result.get('apiResultData', {})
            if isinstance(api_result, str):
                api_result = json.loads(api_result)
            return {
                'success': True,
                'time_slots': api_result.get('pickupTimeList', []),
                'data': api_result
            }
        else:
            return {
                'success': False,
                'message': result.get('apiErrorMsg', '查询失败')
            }
