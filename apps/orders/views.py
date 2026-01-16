"""
订单模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Order, OrderItem, Cart, Payment
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    CartSerializer, CartUpdateSerializer, PaymentSerializer
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
    def cancel(self, request, pk=None):
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
    def confirm_receive(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        if order.status != 'delivered':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        
        return Response({'message': '确认收货成功'})

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
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
        queryset = Order.objects.all()
        status_param = self.request.query_params.get('status')
        order_no = self.request.query_params.get('order_no')
        user_id = self.request.query_params.get('user_id')
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if order_no:
            queryset = queryset.filter(order_no__icontains=order_no)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货"""
        order = self.get_object()
        if order.status != 'paid':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.save()
        
        return Response({'message': '发货成功'})

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """确认送达"""
        order = self.get_object()
        if order.status != 'shipped':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        return Response({'message': '已确认送达'})


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """支付记录视图集"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]
