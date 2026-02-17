"""
模拟快递服务 - 用于演示/测试
根据快递单号生成固定的随机数据，保证同一单号每次查询结果一致
"""
import time
import random
import base64
import hashlib
from datetime import datetime, timedelta
from .base import ExpressService, ExpressResult, TraceResult, TraceInfo


# 模拟数据池
COURIER_NAMES = [
    '王建国', '李明', '张伟', '刘洋', '陈强', '杨帆', '赵磊', '周杰',
    '吴斌', '郑浩', '孙鹏', '马超', '朱军', '胡涛', '林峰', '何勇'
]

CITIES = [
    {'province': '北京市', 'city': '北京市', 'districts': ['朝阳区', '海淀区', '东城区', '西城区', '丰台区']},
    {'province': '上海市', 'city': '上海市', 'districts': ['浦东新区', '徐汇区', '静安区', '黄浦区', '长宁区']},
    {'province': '广东省', 'city': '广州市', 'districts': ['天河区', '越秀区', '海珠区', '白云区', '番禺区']},
    {'province': '广东省', 'city': '深圳市', 'districts': ['南山区', '福田区', '罗湖区', '宝安区', '龙岗区']},
    {'province': '浙江省', 'city': '杭州市', 'districts': ['西湖区', '上城区', '拱墅区', '滨江区', '余杭区']},
    {'province': '江苏省', 'city': '南京市', 'districts': ['玄武区', '秦淮区', '鼓楼区', '建邺区', '江宁区']},
]

BRANCH_TYPES = ['营业点', '集散中心', '转运中心', '快递站', '服务点']


def get_seed_from_express_no(express_no: str) -> int:
    """根据快递单号生成固定的随机种子"""
    return int(hashlib.md5(express_no.encode()).hexdigest()[:8], 16)


class MockExpressService(ExpressService):
    """模拟快递服务，用于毕设演示"""

    def __init__(self, config: dict = None):
        super().__init__(config or {})

    def _get_random_phone(self, rng: random.Random) -> str:
        """生成随机手机号"""
        prefixes = ['138', '139', '150', '151', '152', '158', '159', '186', '187', '188']
        return f"{rng.choice(prefixes)}{rng.randint(10000000, 99999999)}"

    def _get_random_courier(self, rng: random.Random) -> dict:
        """生成随机快递员信息"""
        return {
            'name': rng.choice(COURIER_NAMES),
            'phone': self._get_random_phone(rng)
        }

    def _get_random_route(self, rng: random.Random) -> list:
        """生成随机物流路线（2-4个城市）"""
        num_cities = rng.randint(2, 4)
        selected_cities = rng.sample(CITIES, num_cities)
        route = []
        for city_info in selected_cities:
            district = rng.choice(city_info['districts'])
            branch_type = rng.choice(BRANCH_TYPES)
            route.append({
                'province': city_info['province'],
                'city': city_info['city'],
                'district': district,
                'location': f"{city_info['city']}{district}{branch_type}"
            })
        return route

    def create_order(self, order_no: str, sender: dict, receiver: dict,
                     goods: list, remark: str = '') -> ExpressResult:
        """创建快递订单 - 返回模拟单号"""
        express_no = f"SF{int(time.time())}{random.randint(1000, 9999)}"
        return ExpressResult(
            success=True,
            express_no=express_no,
            message='下单成功'
        )

    def query_trace(self, express_no: str) -> TraceResult:
        """查询物流轨迹 - 根据单号生成固定的随机轨迹"""
        # 使用快递单号作为随机种子，保证同一单号每次查询结果一致
        seed = get_seed_from_express_no(express_no)
        rng = random.Random(seed)

        now = datetime.now()

        # 随机生成快递员
        pickup_courier = self._get_random_courier(rng)
        delivery_courier = self._get_random_courier(rng)

        # 随机生成路线
        route = self._get_random_route(rng)

        # 生成轨迹
        traces = []
        hour_offset = 1

        # 派送中
        traces.append(TraceInfo(
            time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
            status='delivering',
            description=f'【派送中】快递员 {delivery_courier["name"]} ({delivery_courier["phone"]}) 正在为您派送，请保持电话畅通',
            location=route[-1]['location']
        ))
        hour_offset += rng.randint(1, 3)

        # 到达派送点
        traces.append(TraceInfo(
            time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
            status='delivering',
            description=f'快件已到达【{route[-1]["location"]}】，快递员 {delivery_courier["name"]} 正在安排派送',
            location=route[-1]['location']
        ))
        hour_offset += rng.randint(2, 5)

        # 中转站点（倒序遍历路线）
        for i in range(len(route) - 2, 0, -1):
            traces.append(TraceInfo(
                time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
                status='in_transit',
                description=f'快件已到达【{route[i]["location"]}】',
                location=route[i]['location']
            ))
            hour_offset += rng.randint(3, 8)

            traces.append(TraceInfo(
                time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
                status='in_transit',
                description=f'快件已从【{route[i-1]["location"] if i > 0 else route[0]["location"]}】发出，正发往【{route[i]["location"]}】',
                location=route[i-1]['location'] if i > 0 else route[0]['location']
            ))
            hour_offset += rng.randint(2, 4)

        # 已揽收
        traces.append(TraceInfo(
            time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
            status='collected',
            description=f'【已揽收】快递员 {pickup_courier["name"]} ({pickup_courier["phone"]}) 已揽件',
            location=route[0]['location']
        ))
        hour_offset += rng.randint(1, 3)

        # 已下单
        traces.append(TraceInfo(
            time=(now - timedelta(hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S'),
            status='created',
            description='顺丰速运 已收到订单信息，等待揽收',
            location=route[0]['location']
        ))

        return TraceResult(
            success=True,
            status='delivering',
            traces=traces,
            message='查询成功'
        )

    def cancel_order(self, express_no: str) -> ExpressResult:
        """取消快递订单"""
        return ExpressResult(
            success=True,
            message='取消成功'
        )

    def get_waybill_image(self, express_no: str, order_no: str = '') -> dict:
        """获取电子面单图片 - 返回模拟面单"""
        # 根据单号生成固定随机数据
        seed = get_seed_from_express_no(express_no)
        rng = random.Random(seed)

        route = self._get_random_route(rng)
        sender_location = route[0]
        receiver_location = route[-1]

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320">
            <rect width="400" height="320" fill="white" stroke="black" stroke-width="2"/>
            <text x="200" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#E60012">顺丰速运</text>
            <line x1="10" y1="45" x2="390" y2="45" stroke="black" stroke-width="1"/>
            <text x="20" y="70" font-size="14" font-weight="bold">快递单号: {express_no}</text>
            <text x="20" y="92" font-size="12" fill="#666">订单编号: {order_no}</text>
            <line x1="10" y1="105" x2="390" y2="105" stroke="black" stroke-width="1"/>
            <text x="20" y="128" font-size="12" font-weight="bold">寄件人:</text>
            <text x="80" y="128" font-size="12">鲜奶配送中心 13800138000</text>
            <text x="20" y="148" font-size="11" fill="#666">{sender_location['province']}{sender_location['city']}{sender_location['district']}张江高科技园区</text>
            <line x1="10" y1="160" x2="390" y2="160" stroke="black" stroke-width="1"/>
            <text x="20" y="183" font-size="12" font-weight="bold">收件人:</text>
            <text x="80" y="183" font-size="12">客户 138****8888</text>
            <text x="20" y="203" font-size="11" fill="#666">{receiver_location['province']}{receiver_location['city']}{receiver_location['district']}</text>
            <line x1="10" y1="220" x2="390" y2="220" stroke="black" stroke-width="1"/>
            <rect x="20" y="235" width="70" height="70" fill="white" stroke="#333"/>
            <text x="55" y="275" text-anchor="middle" font-size="9" fill="#666">二维码</text>
            <rect x="110" y="235" width="160" height="30" fill="#E60012"/>
            <text x="190" y="256" text-anchor="middle" font-size="14" fill="white" font-weight="bold">标准快递</text>
            <text x="110" y="285" font-size="10" fill="#666">打印时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</text>
        </svg>'''

        image_data = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

        return {
            'success': True,
            'image_data': image_data,
            'image_type': 'svg+xml'
        }

    def book_pickup(self, express_no: str, pickup_time: str,
                    contact_name: str, contact_phone: str,
                    address: str, remark: str = '') -> dict:
        """预约上门取件"""
        pickup_code = f"PK{random.randint(100000, 999999)}"
        return {
            'success': True,
            'message': f'预约成功，快递员将于预约时间上门取件，取件码: {pickup_code}',
            'pickup_code': pickup_code
        }

    def cancel_pickup(self, express_no: str) -> dict:
        """取消预约取件"""
        return {
            'success': True,
            'message': '取消预约成功'
        }

    def get_pickup_time(self, address: str) -> dict:
        """获取可预约时间段"""
        now = datetime.now()
        time_slots = []
        for i in range(3):
            date = now + timedelta(days=i)
            time_slots.append({
                'date': date.strftime('%Y-%m-%d'),
                'slots': ['09:00-12:00', '14:00-18:00', '18:00-21:00']
            })
        return {
            'success': True,
            'time_slots': time_slots
        }
