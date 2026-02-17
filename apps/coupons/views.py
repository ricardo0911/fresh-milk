"""
优惠券模块 - 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q, F
from django.db import transaction
from .models import Coupon, UserCoupon, CouponActivity
from .serializers import (
    CouponSerializer, CouponListSerializer,
    UserCouponSerializer, CouponActivitySerializer
)


class CouponViewSet(viewsets.ModelViewSet):
    """优惠券视图集"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        """管理操作需要管理员权限，查看允许所有人"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    def get_serializer_class(self):
        if self.action == 'list':
            return CouponListSerializer
        return CouponSerializer
    
    def get_queryset(self):
        queryset = Coupon.objects.all()
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 类型筛选
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可领取的优惠券"""
        now = timezone.now()
        coupons = Coupon.objects.filter(
            status='active',
            start_time__lte=now,
            end_time__gte=now
        ).filter(
            Q(total_count=0) | Q(total_count__gt=F('used_count'))
        )
        serializer = CouponListSerializer(coupons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def exchangeable(self, request):
        """获取可积分兑换的优惠券"""
        now = timezone.now()
        coupons = Coupon.objects.filter(
            status='active',
            is_exchangeable=True,
            start_time__lte=now,
            end_time__gte=now
        ).filter(
            Q(exchange_limit=0) | Q(exchange_limit__gt=F('exchanged_count'))
        )
        serializer = CouponListSerializer(coupons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def grant(self, request, pk=None):
        """管理员发放优惠券给用户"""
        from apps.users.models import User

        coupon = self.get_object()
        user_ids = request.data.get('user_ids', [])

        if not user_ids:
            return Response({'error': '请选择用户'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证优惠券状态
        if coupon.status != 'active':
            return Response({'error': '优惠券已停用'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取用户
        users = User.objects.filter(id__in=user_ids)
        if not users.exists():
            return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        granted_count = 0
        skipped_users = []

        for user in users:
            # 检查用户已领取数量
            user_count = UserCoupon.objects.filter(user=user, coupon=coupon).count()
            if user_count >= coupon.per_user_limit:
                skipped_users.append(user.username or user.phone)
                continue

            # 创建用户优惠券
            UserCoupon.objects.create(user=user, coupon=coupon)
            granted_count += 1

        message = f'成功发放给 {granted_count} 位用户'
        if skipped_users:
            message += f'，{len(skipped_users)} 位用户已达领取上限'

        return Response({
            'message': message,
            'granted_count': granted_count,
            'skipped_users': skipped_users
        })


class UserCouponViewSet(viewsets.ModelViewSet):
    """用户优惠券视图集"""
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UserCoupon.objects.filter(user=self.request.user).select_related('coupon')
        # 支持按状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @action(detail=False, methods=['post'])
    def receive(self, request):
        """领取优惠券"""
        coupon_id = request.data.get('coupon_id')
        
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({'error': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 验证优惠券状态
        now = timezone.now()
        if coupon.status != 'active':
            return Response({'error': '优惠券已停用'}, status=status.HTTP_400_BAD_REQUEST)
        if now < coupon.start_time or now > coupon.end_time:
            return Response({'error': '优惠券不在有效期内'}, status=status.HTTP_400_BAD_REQUEST)
        if coupon.total_count > 0 and coupon.used_count >= coupon.total_count:
            return Response({'error': '优惠券已领完'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户领取数量
        user_count = UserCoupon.objects.filter(user=request.user, coupon=coupon).count()
        if user_count >= coupon.per_user_limit:
            return Response({'error': f'每人限领{coupon.per_user_limit}张'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户优惠券
        user_coupon = UserCoupon.objects.create(
            user=request.user,
            coupon=coupon
        )
        
        return Response({
            'message': '领取成功',
            'user_coupon': UserCouponSerializer(user_coupon).data
        })
    
    @action(detail=False, methods=['get'])
    def usable(self, request):
        """获取可用的优惠券(用于下单)"""
        amount = request.query_params.get('amount', 0)
        try:
            amount = float(amount)
        except:
            amount = 0
        
        now = timezone.now()
        user_coupons = UserCoupon.objects.filter(
            user=request.user,
            status='unused',
            coupon__status='active',
            coupon__end_time__gte=now,
            coupon__min_amount__lte=amount
        ).select_related('coupon')
        
        serializer = UserCouponSerializer(user_coupons, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """使用优惠券"""
        user_coupon = self.get_object()
        order_id = request.data.get('order_id')
        
        if user_coupon.status != 'unused':
            return Response({'error': '优惠券已使用或已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_coupon.status = 'used'
        user_coupon.used_at = timezone.now()
        if order_id:
            user_coupon.order_id = order_id
        user_coupon.save()
        
        # 更新优惠券使用数
        user_coupon.coupon.used_count += 1
        user_coupon.coupon.save()
        
        return Response({'message': '使用成功'})

    @action(detail=False, methods=['post'])
    def exchange(self, request):
        """积分兑换优惠券"""
        coupon_id = request.data.get('coupon_id')
        user = request.user

        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({'error': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 验证优惠券状态
        now = timezone.now()
        if coupon.status != 'active':
            return Response({'error': '优惠券已停用'}, status=status.HTTP_400_BAD_REQUEST)
        if not coupon.is_exchangeable:
            return Response({'error': '该优惠券不支持积分兑换'}, status=status.HTTP_400_BAD_REQUEST)
        if now < coupon.start_time or now > coupon.end_time:
            return Response({'error': '优惠券不在有效期内'}, status=status.HTTP_400_BAD_REQUEST)
        if coupon.exchange_limit > 0 and coupon.exchanged_count >= coupon.exchange_limit:
            return Response({'error': '优惠券已兑完'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户积分
        if user.points < coupon.points_required:
            return Response({'error': f'积分不足，需要{coupon.points_required}积分'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户领取数量
        user_count = UserCoupon.objects.filter(user=user, coupon=coupon).count()
        if user_count >= coupon.per_user_limit:
            return Response({'error': f'每人限兑{coupon.per_user_limit}张'}, status=status.HTTP_400_BAD_REQUEST)

        # 执行兑换
        from apps.users.models import PointsRecord
        with transaction.atomic():
            # 扣除积分
            user.points -= coupon.points_required
            user.save()

            # 记录积分变动
            PointsRecord.objects.create(
                user=user,
                type='spend',
                source='exchange',
                points=-coupon.points_required,
                balance=user.points,
                remark=f'兑换优惠券: {coupon.name}'
            )

            # 创建用户优惠券
            user_coupon = UserCoupon.objects.create(
                user=user,
                coupon=coupon
            )

            # 更新兑换数量
            coupon.exchanged_count += 1
            coupon.save()

        return Response({
            'message': '兑换成功',
            'user_coupon': UserCouponSerializer(user_coupon).data,
            'remaining_points': user.points
        })


class CouponActivityViewSet(viewsets.ModelViewSet):
    """优惠券活动视图集"""
    queryset = CouponActivity.objects.filter(is_active=True)
    serializer_class = CouponActivitySerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前进行中的活动"""
        now = timezone.now()
        activities = CouponActivity.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).prefetch_related('coupons')
        serializer = CouponActivitySerializer(activities, many=True)
        return Response(serializer.data)
