"""
优惠券模块 - 序列化器
"""
from rest_framework import serializers
from .models import Coupon, UserCoupon, CouponActivity


class CouponSerializer(serializers.ModelSerializer):
    """优惠券序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'type', 'type_display',
            'discount_percent', 'discount_amount', 'min_amount', 'max_discount',
            'total_count', 'used_count', 'remaining', 'per_user_limit',
            'start_time', 'end_time', 'is_all_products',
            'status', 'status_display', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'used_count', 'created_at']
    
    def get_remaining(self, obj):
        if obj.total_count == 0:
            return -1  # 无限
        return obj.total_count - obj.used_count


class CouponListSerializer(serializers.ModelSerializer):
    """优惠券列表简化序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'type', 'type_display',
            'discount_percent', 'discount_amount', 'min_amount',
            'start_time', 'end_time', 'status'
        ]


class UserCouponSerializer(serializers.ModelSerializer):
    """用户优惠券序列化器"""
    coupon_detail = CouponListSerializer(source='coupon', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserCoupon
        fields = [
            'id', 'user', 'coupon', 'coupon_detail',
            'status', 'status_display', 'received_at', 'used_at', 'order'
        ]
        read_only_fields = ['id', 'received_at', 'used_at']


class CouponActivitySerializer(serializers.ModelSerializer):
    """优惠券活动序列化器"""
    coupons_detail = CouponListSerializer(source='coupons', many=True, read_only=True)
    
    class Meta:
        model = CouponActivity
        fields = [
            'id', 'name', 'description', 'coupons', 'coupons_detail',
            'banner_image', 'start_time', 'end_time', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
