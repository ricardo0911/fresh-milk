"""
圆通速递API对接

圆通开放平台文档: https://open.yto.net.cn/

需要申请:
1. 圆通开放平台账号
2. 获取 app_key 和 app_secret
3. 获取客户编码 customer_code
"""
import json
import time
import hashlib
import requests
from typing import List
from .base import ExpressService, ExpressResult, TraceResult, TraceInfo


class YTOExpressService(ExpressService):
    """圆通速递服务"""

    # 圆通API地址
    PROD_URL = 'https://openapi.yto.net.cn/open/api'
    TEST_URL = 'https://openapi-test.yto.net.cn/open/api'

    def __init__(self, config: dict):
        super().__init__(config)
        self.app_key = config.get('app_key', '')
        self.app_secret = config.get('app_secret', '')
        self.customer_code = config.get('customer_code', '')  # 客户编码
        self.api_url = config.get('api_url', '') or self.PROD_URL

    def _sign(self, params: dict) -> str:
        """生成签名"""
        # 按key排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 拼接字符串
        sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])
        sign_str = self.app_secret + sign_str + self.app_secret
        # MD5加密
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _request(self, method: str, params: dict) -> dict:
        """发送请求到圆通API"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        common_params = {
            'app_key': self.app_key,
            'method': method,
            'timestamp': timestamp,
            'format': 'JSON',
            'v': '1.0'
        }

        # 合并参数
        all_params = {**common_params, **params}
        all_params['sign'] = self._sign(all_params)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(self.api_url, data=all_params, headers=headers, timeout=30)
            result = response.json()
            return result
        except Exception as e:
            return {'success': False, 'errorMsg': str(e)}

    def create_order(
        self,
        order_no: str,
        sender: dict,
        receiver: dict,
        goods: List[dict],
        remark: str = ''
    ) -> ExpressResult:
        """
        创建圆通快递订单

        圆通下单接口: yto.open.order.create
        """
        # 构建商品名称
        goods_name = '、'.join([item.get('name', '鲜奶') for item in goods])

        order_data = {
            'clientID': self.customer_code,
            'logisticProviderID': 'YTO',
            'txLogisticID': order_no,  # 商户订单号
            'tradeNo': order_no,
            'totalServiceFee': 0,
            'codSplitFee': 0,
            'sender': {
                'name': sender.get('name', ''),
                'phone': sender.get('phone', ''),
                'mobile': sender.get('phone', ''),
                'prov': sender.get('province', ''),
                'city': sender.get('city', ''),
                'county': sender.get('district', ''),
                'address': sender.get('address', '')
            },
            'receiver': {
                'name': receiver.get('name', ''),
                'phone': receiver.get('phone', ''),
                'mobile': receiver.get('phone', ''),
                'prov': receiver.get('province', ''),
                'city': receiver.get('city', ''),
                'county': receiver.get('district', ''),
                'address': receiver.get('address', '')
            },
            'itemsValue': 0,
            'items': [{
                'itemName': goods_name,
                'number': sum([item.get('quantity', 1) for item in goods]),
                'itemValue': 0
            }],
            'special': 0,
            'remark': remark
        }

        params = {
            'param': json.dumps(order_data, ensure_ascii=False)
        }

        result = self._request('yto.open.order.create', params)

        if result.get('success'):
            data = result.get('data', {})
            return ExpressResult(
                success=True,
                express_no=data.get('waybillNo', ''),
                message='下单成功',
                data=data
            )
        else:
            return ExpressResult(
                success=False,
                message=result.get('errorMsg', '下单失败'),
                data=result
            )

    def query_trace(self, express_no: str) -> TraceResult:
        """
        查询圆通物流轨迹

        圆通轨迹查询接口: yto.open.waybill.trace.query
        """
        params = {
            'param': json.dumps({
                'waybillNo': express_no
            })
        }

        result = self._request('yto.open.waybill.trace.query', params)

        if result.get('success'):
            data = result.get('data', {})
            trace_list = data.get('traces', [])

            traces = []
            current_status = 'created'

            for trace in trace_list:
                scan_type = trace.get('scanType', '')
                # 根据扫描类型判断状态
                if scan_type == 'GOT':  # 揽收
                    current_status = 'collected'
                elif scan_type in ['ARRIVAL', 'DEPARTURE']:  # 到达/发出
                    current_status = 'in_transit'
                elif scan_type == 'SENT_SCAN':  # 派送
                    current_status = 'delivering'
                elif scan_type == 'SIGNED':  # 签收
                    current_status = 'signed'

                traces.append(TraceInfo(
                    time=trace.get('scanTime', ''),
                    status=scan_type,
                    description=trace.get('desc', ''),
                    location=trace.get('scanStation', '')
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
                message=result.get('errorMsg', '查询失败')
            )

    def cancel_order(self, express_no: str) -> ExpressResult:
        """
        取消圆通订单

        圆通取消订单接口: yto.open.order.cancel
        """
        params = {
            'param': json.dumps({
                'waybillNo': express_no,
                'reason': '商户取消'
            })
        }

        result = self._request('yto.open.order.cancel', params)

        if result.get('success'):
            return ExpressResult(
                success=True,
                express_no=express_no,
                message='取消成功'
            )
        else:
            return ExpressResult(
                success=False,
                express_no=express_no,
                message=result.get('errorMsg', '取消失败')
            )

    def get_waybill_no(self, count: int = 1) -> dict:
        """
        获取电子面单号

        圆通获取面单号接口: yto.open.waybill.get
        """
        params = {
            'param': json.dumps({
                'clientID': self.customer_code,
                'count': count
            })
        }

        result = self._request('yto.open.waybill.get', params)

        if result.get('success'):
            return {
                'success': True,
                'waybill_nos': result.get('data', {}).get('waybillNos', [])
            }
        else:
            return {
                'success': False,
                'message': result.get('errorMsg', '获取失败')
            }
