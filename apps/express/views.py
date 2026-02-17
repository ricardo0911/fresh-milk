from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone

from .models import ExpressCompany, ExpressOrder, ExpressTrace
from .serializers import (
    ExpressCompanySerializer,
    ExpressCompanyDetailSerializer,
    ExpressOrderSerializer,
    ExpressShipSerializer
)
from .utils import get_express_service, get_sender_info
from apps.orders.models import Order


class ExpressCompanyViewSet(viewsets.ModelViewSet):
    """快递公司管理"""
    queryset = ExpressCompany.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExpressCompanySerializer
        return ExpressCompanyDetailSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsAdminUser()]


class ExpressOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """快递订单查询"""
    serializer_class = ExpressOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ExpressOrder.objects.all()
        return ExpressOrder.objects.filter(order__user=user)

    @action(detail=True, methods=['get'])
    def trace(self, request, pk=None):
        """查询物流轨迹"""
        express_order = self.get_object()

        # 从数据库获取已保存的轨迹
        traces = express_order.traces.all()
        if traces.exists():
            serializer = ExpressOrderSerializer(express_order)
            return Response(serializer.data)

        # 调用快递API查询最新轨迹
        service = get_express_service(express_order.express_company.code)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        result = service.query_trace(express_order.express_no)
        if result.success:
            # 保存轨迹到数据库
            for trace in result.traces:
                ExpressTrace.objects.get_or_create(
                    express_order=express_order,
                    time=trace.time,
                    defaults={
                        'status': trace.status,
                        'description': trace.description,
                        'location': trace.location
                    }
                )
            # 更新快递状态
            express_order.status = result.status
            express_order.save()

            serializer = ExpressOrderSerializer(express_order)
            return Response(serializer.data)
        else:
            return Response({'error': result.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """
        根据订单ID或订单号查询物流轨迹（用户端使用）
        GET /express/orders/by-order/{order_id_or_order_no}/
        """
        # 尝试通过订单ID或订单号查找订单
        try:
            # 先尝试作为ID查询
            order = Order.objects.get(id=order_id)
        except (Order.DoesNotExist, ValueError):
            # 再尝试作为订单号查询
            try:
                order = Order.objects.get(order_no=order_id)
            except Order.DoesNotExist:
                return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 验证用户权限（只能查看自己的订单）
        if not request.user.is_staff and order.user != request.user:
            return Response({'error': '无权查看此订单'}, status=status.HTTP_403_FORBIDDEN)

        # 检查是否有物流信息
        if not order.express_no:
            return Response({'error': '订单暂无物流信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            # 没有快递服务时，返回基本信息
            return Response({
                'express_company': order.express_company,
                'express_no': order.express_no,
                'status': order.express_status or 'unknown',
                'traces': []
            })

        result = service.query_trace(order.express_no)
        if result.success:
            # 更新订单物流状态
            order.express_status = result.status
            order.save()

            return Response({
                'express_company': order.express_company,
                'express_no': order.express_no,
                'status': result.status,
                'traces': [
                    {
                        'time': t.time,
                        'description': t.description,
                        'location': t.location
                    }
                    for t in result.traces
                ]
            })
        else:
            # 即使查询失败，也返回基本信息
            return Response({
                'express_company': order.express_company,
                'express_no': order.express_no,
                'status': order.express_status or 'unknown',
                'traces': [],
                'message': result.message
            })


class AdminExpressViewSet(viewsets.ViewSet):
    """管理员快递操作"""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], url_path='ship/(?P<order_id>[^/.]+)')
    def ship(self, request, order_id=None):
        """
        快递发货

        POST /admin/express/ship/{order_id}/
        {
            "express_company_code": "SF",  // SF-顺丰, YTO-圆通
            "remark": "备注"
        }
        """
        serializer = ExpressShipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_code = serializer.validated_data['express_company_code']
        remark = serializer.validated_data.get('remark', '')

        # 获取订单
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'paid':
            return Response({'error': '订单状态不正确，只有已支付订单可以发货'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递公司配置
        try:
            express_company = ExpressCompany.objects.get(code=company_code, is_active=True)
        except ExpressCompany.DoesNotExist:
            return Response({'error': '快递公司不存在或未启用'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(company_code)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取发件人信息
        sender = get_sender_info(company_code)
        if not sender.get('name'):
            return Response({'error': '请先配置发件人信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 解析收件人地址
        receiver = {
            'name': order.receiver_name,
            'phone': order.receiver_phone,
            'province': '',
            'city': '',
            'district': '',
            'address': order.receiver_address
        }

        # 获取商品信息
        goods = []
        for item in order.items.all():
            goods.append({
                'name': item.product_name,
                'quantity': item.quantity
            })

        # 调用快递API下单
        result = service.create_order(
            order_no=order.order_no,
            sender=sender,
            receiver=receiver,
            goods=goods,
            remark=remark
        )

        if result.success:
            # 创建快递订单记录
            express_order = ExpressOrder.objects.create(
                order=order,
                express_company=express_company,
                express_no=result.express_no,
                status='created',
                receiver_name=order.receiver_name,
                receiver_phone=order.receiver_phone,
                receiver_address=order.receiver_address
            )

            # 更新订单状态
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.express_company = company_code
            order.express_no = result.express_no
            order.express_status = 'created'
            order.save()

            return Response({
                'message': '发货成功',
                'express_no': result.express_no,
                'express_company': express_company.name
            })
        else:
            return Response({'error': result.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def companies(self, request):
        """获取可用的快递公司列表"""
        companies = ExpressCompany.objects.filter(is_active=True)
        serializer = ExpressCompanySerializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='trace/(?P<order_id>[^/.]+)')
    def trace(self, request, order_id=None):
        """查询订单物流轨迹"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not order.express_no:
            return Response({'error': '订单暂无物流信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        result = service.query_trace(order.express_no)
        if result.success:
            # 更新订单物流状态
            order.express_status = result.status
            order.save()

            return Response({
                'express_company': order.express_company,
                'express_no': order.express_no,
                'status': result.status,
                'traces': [
                    {
                        'time': t.time,
                        'description': t.description,
                        'location': t.location
                    }
                    for t in result.traces
                ]
            })
        else:
            return Response({'error': result.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='waybill/(?P<order_id>[^/.]+)')
    def waybill(self, request, order_id=None):
        """
        获取电子面单图片

        GET /express/admin/waybill/{order_id}/
        返回面单的base64图片数据，前端可直接显示或打印
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not order.express_no:
            return Response({'error': '订单暂无快递单号'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        # 调用获取面单接口
        result = service.get_waybill_image(order.express_no, order.order_no)
        if result.get('success'):
            return Response({
                'express_no': order.express_no,
                'image_data': result.get('image_data', ''),
                'image_type': result.get('image_type', 'png')
            })
        else:
            return Response({'error': result.get('message', '获取面单失败')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='pickup/(?P<order_id>[^/.]+)')
    def pickup(self, request, order_id=None):
        """
        预约上门取件

        POST /express/admin/pickup/{order_id}/
        {
            "pickup_time": "2026-01-29 14:00:00",  // 预约取件时间
            "remark": "备注"
        }
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not order.express_no:
            return Response({'error': '请先发货获取快递单号'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取发件人信息
        sender = get_sender_info(order.express_company)

        pickup_time = request.data.get('pickup_time', '')
        remark = request.data.get('remark', '')

        # 调用预约取件接口
        result = service.book_pickup(
            express_no=order.express_no,
            pickup_time=pickup_time,
            contact_name=sender.get('name', ''),
            contact_phone=sender.get('phone', ''),
            address=f"{sender.get('province', '')}{sender.get('city', '')}{sender.get('district', '')}{sender.get('address', '')}",
            remark=remark
        )

        if result.get('success'):
            # 更新快递订单状态
            try:
                express_order = ExpressOrder.objects.get(order=order)
                express_order.pickup_time = pickup_time
                express_order.pickup_code = result.get('pickup_code', '')
                express_order.save()
            except ExpressOrder.DoesNotExist:
                pass

            return Response({
                'message': result.get('message', '预约成功'),
                'pickup_code': result.get('pickup_code', ''),
                'pickup_time': pickup_time
            })
        else:
            return Response({'error': result.get('message', '预约失败')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='cancel-pickup/(?P<order_id>[^/.]+)')
    def cancel_pickup(self, request, order_id=None):
        """
        取消预约取件

        POST /express/admin/cancel-pickup/{order_id}/
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not order.express_no:
            return Response({'error': '订单暂无快递单号'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        result = service.cancel_pickup(order.express_no)
        if result.get('success'):
            # 清除预约信息
            try:
                express_order = ExpressOrder.objects.get(order=order)
                express_order.pickup_time = None
                express_order.pickup_code = ''
                express_order.save()
            except ExpressOrder.DoesNotExist:
                pass

            return Response({'message': '取消预约成功'})
        else:
            return Response({'error': result.get('message', '取消失败')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='pickup-times')
    def pickup_times(self, request):
        """
        查询可预约取件时间段

        GET /express/admin/pickup-times/?company=SF
        """
        company_code = request.query_params.get('company', 'SF')

        # 获取快递服务
        service = get_express_service(company_code)
        if not service:
            return Response({'error': '快递服务不可用'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取发件人地址
        sender = get_sender_info(company_code)
        address = f"{sender.get('province', '')}{sender.get('city', '')}{sender.get('district', '')}{sender.get('address', '')}"

        result = service.get_pickup_time(address)
        if result.get('success'):
            return Response({
                'time_slots': result.get('time_slots', [])
            })
        else:
            return Response({'error': result.get('message', '查询失败')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='cancel/(?P<order_id>[^/.]+)')
    def cancel(self, request, order_id=None):
        """
        取消快递订单

        POST /express/admin/cancel/{order_id}/
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not order.express_no:
            return Response({'error': '订单暂无快递单号'}, status=status.HTTP_400_BAD_REQUEST)

        # 演示模式：允许取消任何状态的快递（实际生产环境应该限制）
        # 不可取消的状态：已签收、已完成
        non_cancelable_statuses = ['signed', '已签收', 'completed', '已完成']
        if order.express_status in non_cancelable_statuses:
            return Response({'error': f'快递已签收，无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取快递服务
        service = get_express_service(order.express_company)
        if not service:
            # 没有快递服务时，直接清除快递信息
            order.express_company = ''
            order.express_no = ''
            order.express_status = ''
            if order.status == 'shipped':
                order.status = 'paid'
                order.shipped_at = None
            order.save()
            return Response({'message': '取消成功，订单已恢复为待发货状态'})

        result = service.cancel_order(order.express_no)
        if result.success:
            # 清除快递信息
            order.express_company = ''
            order.express_no = ''
            order.express_status = ''
            # 如果订单是已发货状态，恢复为待发货
            if order.status == 'shipped':
                order.status = 'paid'
                order.shipped_at = None
            order.save()

            # 更新快递订单状态
            try:
                express_order = ExpressOrder.objects.get(order=order)
                express_order.status = 'cancelled'
                express_order.save()
            except ExpressOrder.DoesNotExist:
                pass

            return Response({'message': '取消成功，订单已恢复为待发货状态'})
        else:
            return Response({'error': result.message}, status=status.HTTP_400_BAD_REQUEST)
