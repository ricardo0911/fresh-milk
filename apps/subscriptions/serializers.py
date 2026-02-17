"""
订阅模块 - 序列化器
"""
from rest_framework import serializers
from .models import Subscription


class SubscriptionUserSerializer(serializers.Serializer):
    """订阅用户简要信息"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    nickname = serializers.CharField()
    phone = serializers.CharField()


class SubscriptionSerializer(serializers.ModelSerializer):
    """订阅序列化器"""
    status_display = serializers.ReadOnlyField()
    frequency_display = serializers.ReadOnlyField()
    product = serializers.SerializerMethodField()
    user = SubscriptionUserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'subscription_no', 'user', 'product', 'product_name', 'product_image',
            'frequency', 'frequency_display', 'quantity', 'total_periods',
            'delivered_count', 'period_price', 'total_price',
            'receiver_name', 'receiver_phone', 'receiver_address',
            'start_date', 'next_delivery_date', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subscription_no', 'delivered_count', 'created_at', 'updated_at']

    def get_product(self, obj):
        if obj.product:
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'cover_image': obj.product.cover_image.url if obj.product.cover_image else None
            }
        return {
            'name': obj.product_name,
            'cover_image': obj.product_image
        }


class SubscriptionCreateSerializer(serializers.Serializer):
    """创建订阅序列化器"""
    product_id = serializers.IntegerField()
    frequency = serializers.ChoiceField(choices=Subscription.FREQUENCY_CHOICES)
    total_periods = serializers.IntegerField(min_value=1, max_value=52)
    quantity = serializers.IntegerField(min_value=1, default=1)
    start_date = serializers.DateField()
    receiver_name = serializers.CharField(max_length=50, required=False)
    receiver_phone = serializers.CharField(max_length=11, required=False)
    receiver_address = serializers.CharField(required=False)
