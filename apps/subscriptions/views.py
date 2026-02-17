"""
订阅模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionCreateSerializer
from apps.products.models import Product


class SubscriptionViewSet(viewsets.ModelViewSet):
    """订阅视图集"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """创建订阅"""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 获取产品
        try:
            product = Product.objects.get(pk=data['product_id'], is_active=True, is_subscription=True)
        except Product.DoesNotExist:
            return Response({'error': '产品不存在或不支持周期购'}, status=status.HTTP_404_NOT_FOUND)

        # 计算价格（周期购享9折）
        unit_price = product.price * Decimal('0.9')
        period_price = unit_price * data['quantity']
        total_price = period_price * data['total_periods']

        # 计算下次配送日期
        next_delivery_date = data['start_date']

        # 创建订阅
        subscription = Subscription.objects.create(
            user=request.user,
            product=product,
            product_name=product.name,
            product_image=product.cover_image.url if product.cover_image else None,
            frequency=data['frequency'],
            quantity=data['quantity'],
            total_periods=data['total_periods'],
            period_price=period_price,
            total_price=total_price,
            start_date=data['start_date'],
            next_delivery_date=next_delivery_date,
            receiver_name=data.get('receiver_name', ''),
            receiver_phone=data.get('receiver_phone', ''),
            receiver_address=data.get('receiver_address', ''),
            status='active'
        )

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """暂停订阅"""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response({'error': '只能暂停配送中的订阅'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'paused'
        subscription.save()
        return Response({'message': '订阅已暂停', 'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """恢复订阅"""
        subscription = self.get_object()
        if subscription.status != 'paused':
            return Response({'error': '只能恢复已暂停的订阅'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'active'
        subscription.save()
        return Response({'message': '订阅已恢复', 'status': 'active'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订阅"""
        subscription = self.get_object()
        if subscription.status in ['completed', 'cancelled']:
            return Response({'error': '订阅已结束，无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'cancelled'
        subscription.save()
        return Response({'message': '订阅已取消', 'status': 'cancelled'})

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        """确认配送完成（每期配送完成时调用，增加积分）"""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response({'error': '订阅状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        if subscription.delivered_count >= subscription.total_periods:
            return Response({'error': '所有期数已配送完成'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 更新配送次数
            subscription.delivered_count += 1

            # 计算下次配送日期
            if subscription.delivered_count < subscription.total_periods:
                frequency_days = {
                    'daily': 1,
                    'weekly': 7,
                    'biweekly': 14,
                    'monthly': 30,
                }
                days = frequency_days.get(subscription.frequency, 7)
                subscription.next_delivery_date = subscription.next_delivery_date + timedelta(days=days)
            else:
                # 所有期数配送完成
                subscription.status = 'completed'
                subscription.next_delivery_date = None

            subscription.save()

            # 增加积分 (1元=1积分，按每期价格计算，最低1积分)
            points_earned = max(1, round(float(subscription.period_price)))
            user = subscription.user
            user.points += points_earned
            user.save()

            # 记录积分变动
            from apps.users.models import PointsRecord
            PointsRecord.objects.create(
                user=user,
                type='earn',
                source='subscription',
                points=points_earned,
                balance=user.points,
                subscription=subscription,
                remark=f'周期购配送奖励: {subscription.subscription_no} 第{subscription.delivered_count}期'
            )

        return Response({
            'message': '配送确认成功',
            'delivered_count': subscription.delivered_count,
            'total_periods': subscription.total_periods,
            'points_earned': points_earned,
            'status': subscription.status
        })


class AdminSubscriptionViewSet(viewsets.ModelViewSet):
    """管理员订阅视图集"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Subscription.objects.all().select_related('user', 'product')

    def get_queryset(self):
        queryset = super().get_queryset()
        # 支持筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        subscription_no = self.request.query_params.get('subscription_no')
        if subscription_no:
            queryset = queryset.filter(subscription_no__icontains=subscription_no)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        """管理员确认配送完成（增加积分）"""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response({'error': '订阅状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        if subscription.delivered_count >= subscription.total_periods:
            return Response({'error': '所有期数已配送完成'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 更新配送次数
            subscription.delivered_count += 1

            # 计算下次配送日期
            if subscription.delivered_count < subscription.total_periods:
                frequency_days = {
                    'daily': 1,
                    'weekly': 7,
                    'biweekly': 14,
                    'monthly': 30,
                }
                days = frequency_days.get(subscription.frequency, 7)
                subscription.next_delivery_date = subscription.next_delivery_date + timedelta(days=days)
            else:
                # 所有期数配送完成
                subscription.status = 'completed'
                subscription.next_delivery_date = None

            subscription.save()

            # 增加积分 (1元=1积分，按每期价格计算，最低1积分)
            points_earned = max(1, round(float(subscription.period_price)))
            user = subscription.user
            user.points += points_earned
            user.save()

            # 记录积分变动
            from apps.users.models import PointsRecord
            PointsRecord.objects.create(
                user=user,
                type='earn',
                source='subscription',
                points=points_earned,
                balance=user.points,
                subscription=subscription,
                remark=f'周期购配送奖励: {subscription.subscription_no} 第{subscription.delivered_count}期'
            )

        return Response({
            'message': '配送确认成功',
            'delivered_count': subscription.delivered_count,
            'total_periods': subscription.total_periods,
            'points_earned': points_earned,
            'status': subscription.status
        })

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """管理员暂停订阅"""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response({'error': '只能暂停配送中的订阅'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'paused'
        subscription.save()
        return Response({'message': '订阅已暂停', 'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """管理员恢复订阅"""
        subscription = self.get_object()
        if subscription.status != 'paused':
            return Response({'error': '只能恢复已暂停的订阅'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'active'
        subscription.save()
        return Response({'message': '订阅已恢复', 'status': 'active'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """管理员取消订阅"""
        subscription = self.get_object()
        if subscription.status in ['completed', 'cancelled']:
            return Response({'error': '订阅已结束，无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'cancelled'
        subscription.save()
        return Response({'message': '订阅已取消', 'status': 'cancelled'})
