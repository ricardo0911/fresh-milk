"""
优惠券模块 - 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q
from .models import Coupon, UserCoupon, CouponActivity
from .serializers import (
    CouponSerializer, CouponListSerializer,
    UserCouponSerializer, CouponActivitySerializer
)


class CouponViewSet(viewsets.ModelViewSet):
    """优惠券视图集"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    
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
            Q(total_count=0) | Q(total_count__gt=models.F('used_count'))
        )
        serializer = CouponListSerializer(coupons, many=True)
        return Response(serializer.data)


class UserCouponViewSet(viewsets.ModelViewSet):
    """用户优惠券视图集"""
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user).select_related('coupon')
    
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
