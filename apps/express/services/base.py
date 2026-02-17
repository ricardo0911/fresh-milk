"""
快递服务基类
"""
import hashlib
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ExpressResult:
    """快递操作结果"""
    success: bool
    express_no: str = ''
    message: str = ''
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class TraceInfo:
    """物流轨迹信息"""
    time: str
    status: str
    description: str
    location: str = ''


@dataclass
class TraceResult:
    """物流查询结果"""
    success: bool
    status: str = ''  # 当前状态
    traces: List[TraceInfo] = None
    message: str = ''

    def __post_init__(self):
        if self.traces is None:
            self.traces = []


class ExpressService(ABC):
    """快递服务基类"""

    def __init__(self, config: dict):
        """
        初始化快递服务

        Args:
            config: 配置信息，包含 app_id, app_key, app_secret, customer_code 等
        """
        self.config = config
        self.app_id = config.get('app_id', '')
        self.app_key = config.get('app_key', '')
        self.app_secret = config.get('app_secret', '')
        self.customer_code = config.get('customer_code', '')
        self.api_url = config.get('api_url', '')

    @abstractmethod
    def create_order(
        self,
        order_no: str,
        sender: dict,
        receiver: dict,
        goods: List[dict],
        remark: str = ''
    ) -> ExpressResult:
        """
        创建快递订单

        Args:
            order_no: 商户订单号
            sender: 发件人信息 {name, phone, province, city, district, address}
            receiver: 收件人信息 {name, phone, province, city, district, address}
            goods: 商品信息列表 [{name, quantity}]
            remark: 备注

        Returns:
            ExpressResult: 包含快递单号等信息
        """
        pass

    @abstractmethod
    def query_trace(self, express_no: str) -> TraceResult:
        """
        查询物流轨迹

        Args:
            express_no: 快递单号

        Returns:
            TraceResult: 物流轨迹信息
        """
        pass

    @abstractmethod
    def cancel_order(self, express_no: str) -> ExpressResult:
        """
        取消快递订单

        Args:
            express_no: 快递单号

        Returns:
            ExpressResult: 操作结果
        """
        pass

    def generate_order_id(self) -> str:
        """生成唯一订单ID"""
        return f"{int(time.time() * 1000)}{uuid.uuid4().hex[:8]}"

    def md5(self, text: str) -> str:
        """MD5加密"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_timestamp(self) -> str:
        """获取时间戳"""
        return str(int(time.time()))
