"""
订单模块 - 视图
"""
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Order, OrderItem, Cart, Payment, RefundRequest
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    CartSerializer, CartUpdateSerializer, PaymentSerializer,
    RefundRequestSerializer, RefundRequestCreateSerializer
)
from apps.products.models import Product


class CartViewSet(viewsets.ModelViewSet):
    """购物车视图集"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('product')

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': '产品不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.stock < quantity:
            return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CartUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if 'quantity' in serializer.validated_data:
            quantity = serializer.validated_data['quantity']
            if instance.product.stock < quantity:
                return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)
            instance.quantity = quantity
        
        if 'selected' in serializer.validated_data:
            instance.selected = serializer.validated_data['selected']
        
        instance.save()
        return Response(CartSerializer(instance).data)

    @action(detail=False, methods=['post'])
    def select_all(self, request):
        """全选/取消全选"""
        selected = request.data.get('selected', True)
        Cart.objects.filter(user=request.user).update(selected=selected)
        return Response({'message': '操作成功'})

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """清空购物车"""
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': '购物车已清空'})

    @action(detail=False, methods=['delete'])
    def clear_selected(self, request):
        """清空已选商品"""
        Cart.objects.filter(user=request.user, selected=True).delete()
        return Response({'message': '已清空选中商品'})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """购物车汇总"""
        cart_items = Cart.objects.filter(user=request.user, selected=True)
        total_count = sum(item.quantity for item in cart_items)
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        return Response({
            'total_count': total_count,
            'total_amount': float(total_amount)
        })


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_no'  # 使用订单号作为查询字段

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            receiver_name=data['receiver_name'],
            receiver_phone=data['receiver_phone'],
            receiver_address=data['receiver_address'],
            remark=data.get('remark', ''),
            is_subscription=data.get('is_subscription', False),
            subscription_frequency=data.get('subscription_frequency', ''),
            subscription_periods=data.get('subscription_periods', 1),
            total_amount=0,
            pay_amount=0
        )
        
        total_amount = Decimal('0')
        
        # 创建订单商品
        for item_data in data['items']:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            try:
                product = Product.objects.select_for_update().get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f'产品不存在: {product_id}')
            
            if product.stock < quantity:
                raise serializers.ValidationError(f'库存不足: {product.name}')
            
            # 创建订单项
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_image=product.cover_image.url if product.cover_image else '',
                price=product.price,
                quantity=quantity,
                total_price=product.price * quantity
            )
            
            total_amount += product.price * quantity
            
            # 扣减库存
            product.stock -= quantity
            product.sales_count += quantity
            product.save()
        
        # 更新订单金额
        order.total_amount = total_amount
        # 应用会员折扣
        discount_rate = request.user.get_discount_rate()
        order.pay_amount = total_amount * Decimal(str(discount_rate))
        order.save()
        
        # 清空购物车中已下单的商品
        product_ids = [item['product_id'] for item in data['items']]
        Cart.objects.filter(user=request.user, product_id__in=product_ids).delete()
        
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, order_no=None):
        """取消订单"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '只能取消待支付订单'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 恢复库存
        with transaction.atomic():
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.sales_count -= item.quantity
                    item.product.save()
            
            order.status = 'cancelled'
            order.save()
        
        return Response({'message': '订单已取消'})

    @action(detail=True, methods=['post'])
    def confirm_receive(self, request, order_no=None):
        """确认收货"""
        order = self.get_object()
        if order.status not in ['shipped', 'delivered']:
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()

            # 订单完成后增加积分 (1元=1积分)
            points_earned = int(order.pay_amount)
            if points_earned > 0:
                user = order.user
                user.points += points_earned
                user.save()

                # 记录积分变动
                from apps.users.models import PointsRecord
                PointsRecord.objects.create(
                    user=user,
                    type='earn',
                    source='order',
                    points=points_earned,
                    balance=user.points,
                    order=order,
                    remark=f'订单完成奖励: {order.order_no}'
                )

        return Response({
            'message': '确认收货成功',
            'points_earned': points_earned
        })

    @action(detail=True, methods=['post'])
    def pay(self, request, order_no=None):
        """模拟支付"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建支付记录
        payment = Payment.objects.create(
            order=order,
            payment_no=f"PAY{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}",
            amount=order.pay_amount,
            method='sandbox',
            status='success',
            paid_at=timezone.now()
        )
        
        # 更新订单状态
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        return Response({
            'message': '支付成功',
            'payment_no': payment.payment_no
        })


class AdminOrderViewSet(viewsets.ModelViewSet):
    """管理员订单视图集"""
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    def get_queryset(self):
        queryset = Order.objects.select_related('user').all()
        status_param = self.request.query_params.get('status')
        order_no = self.request.query_params.get('order_no')
        user_id = self.request.query_params.get('user_id')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if order_no:
            queryset = queryset.filter(order_no__icontains=order_no)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货 - 调用顺丰API获取快递单号"""
        order = self.get_object()
        if order.status != 'paid':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        # 调用顺丰API创建快递订单
        try:
            from apps.express.services.sf import SFExpressService
            from apps.express.models import ExpressOrder, ExpressConfig

            # 获取顺丰配置
            config = ExpressConfig.objects.filter(company='SF', is_active=True).first()
            if config:
                sf_service = SFExpressService()

                # 获取商品信息
                items = order.items.all()
                cargo_name = ', '.join([item.product_name for item in items[:3]])
                if items.count() > 3:
                    cargo_name += ' 等'

                # 调用顺丰API
                result = sf_service.create_order(
                    order_id=order.order_no,
                    sender_name=config.sender_name or '鲜奶配送中心',
                    sender_phone=config.sender_phone or '13800138000',
                    sender_address=config.sender_address or '上海市浦东新区',
                    receiver_name=order.receiver_name,
                    receiver_phone=order.receiver_phone,
                    receiver_address=order.receiver_address,
                    cargo_name=cargo_name,
                    weight=1.0
                )

                if result.get('success'):
                    waybill_no = result.get('waybill_no')
                    order.express_company = 'SF'
                    order.express_no = waybill_no
                    order.express_status = '已揽收'

                    # 创建快递订单记录
                    ExpressOrder.objects.create(
                        order=order,
                        company='SF',
                        waybill_no=waybill_no,
                        status='created',
                        sender_name=config.sender_name or '鲜奶配送中心',
                        sender_phone=config.sender_phone or '13800138000',
                        sender_address=config.sender_address or '上海市浦东新区',
                        receiver_name=order.receiver_name,
                        receiver_phone=order.receiver_phone,
                        receiver_address=order.receiver_address
                    )
                else:
                    # API调用失败，使用模拟单号
                    import time
                    order.express_company = 'SF'
                    order.express_no = f"SF{time.strftime('%Y%m%d%H%M%S')}"
                    order.express_status = '已揽收'
            else:
                # 没有配置，使用模拟单号
                import time
                order.express_company = 'SF'
                order.express_no = f"SF{time.strftime('%Y%m%d%H%M%S')}"
                order.express_status = '已揽收'
        except Exception as e:
            # 出错时使用模拟单号
            import time
            order.express_company = 'SF'
            order.express_no = f"SF{time.strftime('%Y%m%d%H%M%S')}"
            order.express_status = '已揽收'

        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.save()

        return Response({
            'message': '发货成功',
            'express_company': order.express_company,
            'express_no': order.express_no
        })

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """确认送达 - 直接完成订单并发放积分"""
        order = self.get_object()
        if order.status != 'shipped':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order.status = 'completed'
            order.delivered_at = timezone.now()
            order.completed_at = timezone.now()
            order.save()

            # 订单完成后增加积分 (1元=1积分，最低1积分)
            points_earned = max(1, round(float(order.pay_amount)))
            user = order.user
            user.points += points_earned
            user.save()

            # 记录积分变动
            from apps.users.models import PointsRecord
            PointsRecord.objects.create(
                user=user,
                type='earn',
                source='order',
                points=points_earned,
                balance=user.points,
                order=order,
                remark=f'订单完成奖励: {order.order_no}'
            )

        return Response({
            'message': '已确认送达，订单已完成',
            'points_earned': points_earned
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """支付记录视图集"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]


class RefundRequestViewSet(viewsets.ModelViewSet):
    """退款申请视图集 - 用户端"""
    serializer_class = RefundRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RefundRequest.objects.filter(user=self.request.user).select_related('order', 'user')

    def create(self, request, *args, **kwargs):
        serializer = RefundRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 检查订单
        try:
            order = Order.objects.get(pk=data['order_id'], user=request.user)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 检查订单状态
        if order.status not in ['paid', 'shipped', 'delivered', 'completed']:
            return Response({'error': '该订单状态不支持退款'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已有进行中的退款申请
        existing = RefundRequest.objects.filter(order=order, status__in=['pending', 'approved']).exists()
        if existing:
            return Response({'error': '该订单已有进行中的退款申请'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查退款金额
        if data['amount'] > order.pay_amount:
            return Response({'error': '退款金额不能超过实付金额'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建退款申请
        refund = RefundRequest.objects.create(
            order=order,
            user=request.user,
            type=data['type'],
            reason=data['reason'],
            description=data.get('description', ''),
            amount=data['amount'],
            images=data.get('images', '')
        )

        # 更新订单状态为退款中
        order.status = 'refunding'
        order.save()

        return Response(RefundRequestSerializer(refund).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消退款申请"""
        refund = self.get_object()
        if refund.status != 'pending':
            return Response({'error': '只能取消待处理的退款申请'}, status=status.HTTP_400_BAD_REQUEST)

        refund.status = 'cancelled'
        refund.save()

        # 恢复订单状态
        order = refund.order
        if order.status == 'refunding':
            # 恢复到之前的状态
            if order.completed_at:
                order.status = 'completed'
            elif order.delivered_at:
                order.status = 'delivered'
            elif order.shipped_at:
                order.status = 'shipped'
            elif order.paid_at:
                order.status = 'paid'
            order.save()

        return Response({'message': '退款申请已取消'})

    @action(detail=True, methods=['post'])
    def fill_return_express(self, request, pk=None):
        """填写退货快递信息"""
        refund = self.get_object()
        if refund.status != 'approved' or refund.type != 'return_refund':
            return Response({'error': '当前状态不支持填写退货信息'}, status=status.HTTP_400_BAD_REQUEST)

        express_company = request.data.get('express_company')
        express_no = request.data.get('express_no')

        if not express_company or not express_no:
            return Response({'error': '请填写快递公司和快递单号'}, status=status.HTTP_400_BAD_REQUEST)

        refund.return_express_company = express_company
        refund.return_express_no = express_no
        refund.save()

        return Response({'message': '退货信息已提交'})


class AdminRefundRequestViewSet(viewsets.ModelViewSet):
    """退款申请视图集 - 管理端"""
    queryset = RefundRequest.objects.all()
    serializer_class = RefundRequestSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = RefundRequest.objects.select_related('order', 'user', 'admin').all()
        status_param = self.request.query_params.get('status')
        refund_no = self.request.query_params.get('refund_no')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if refund_no:
            queryset = queryset.filter(refund_no__icontains=refund_no)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """同意退款"""
        refund = self.get_object()
        if refund.status != 'pending':
            return Response({'error': '只能处理待处理的退款申请'}, status=status.HTTP_400_BAD_REQUEST)

        admin_remark = request.data.get('admin_remark', '')
        return_address = request.data.get('return_address', '')

        refund.status = 'approved'
        refund.admin = request.user
        refund.admin_remark = admin_remark
        refund.processed_at = timezone.now()

        # 如果是退货退款，设置退货地址
        if refund.type == 'return_refund' and return_address:
            refund.return_address = return_address

        refund.save()

        # 如果是仅退款，直接完成退款
        if refund.type == 'refund_only':
            return self._complete_refund(refund)

        return Response({'message': '已同意退款申请，等待用户退货'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝退款"""
        refund = self.get_object()
        if refund.status != 'pending':
            return Response({'error': '只能处理待处理的退款申请'}, status=status.HTTP_400_BAD_REQUEST)

        reject_reason = request.data.get('reject_reason', '')
        if not reject_reason:
            return Response({'error': '请填写拒绝原因'}, status=status.HTTP_400_BAD_REQUEST)

        refund.status = 'rejected'
        refund.admin = request.user
        refund.reject_reason = reject_reason
        refund.processed_at = timezone.now()
        refund.save()

        # 恢复订单状态
        order = refund.order
        if order.status == 'refunding':
            if order.completed_at:
                order.status = 'completed'
            elif order.delivered_at:
                order.status = 'delivered'
            elif order.shipped_at:
                order.status = 'shipped'
            elif order.paid_at:
                order.status = 'paid'
            order.save()

        return Response({'message': '已拒绝退款申请'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成退款（确认收到退货后）"""
        refund = self.get_object()
        if refund.status != 'approved':
            return Response({'error': '只能完成已同意的退款申请'}, status=status.HTTP_400_BAD_REQUEST)

        return self._complete_refund(refund)

    def _complete_refund(self, refund):
        """执行退款完成逻辑"""
        with transaction.atomic():
            refund.status = 'completed'
            refund.completed_at = timezone.now()
            refund.save()

            # 更新订单状态
            order = refund.order
            order.status = 'refunded'
            order.save()

            # 恢复库存
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.sales_count -= item.quantity
                    item.product.save()

            # 扣除之前发放的积分（如果订单已完成过）
            if order.completed_at:
                from apps.users.models import PointsRecord
                # 查找该订单发放的积分记录
                points_record = PointsRecord.objects.filter(
                    user=order.user,
                    source='order',
                    order=order,
                    type='earn'
                ).first()

                if points_record:
                    points_to_deduct = points_record.points
                    user = order.user
                    user.points = max(0, user.points - points_to_deduct)
                    user.save()

                    # 记录积分扣除
                    PointsRecord.objects.create(
                        user=user,
                        type='spend',
                        source='refund',
                        points=-points_to_deduct,
                        balance=user.points,
                        order=order,
                        remark=f'订单退款扣除积分: {order.order_no}'
                    )

        return Response({'message': '退款已完成'})

