"""
订单模块 - 序列化器
"""
from rest_framework import serializers
from .models import Order, OrderItem, Cart, Payment
from apps.products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 
                  'price', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    items_count = serializers.SerializerMethodField()
    first_item = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'total_amount', 'pay_amount', 'status',
                  'is_subscription', 'items_count', 'first_item', 'created_at']

    def get_items_count(self, obj):
        return obj.items.count()

    def get_first_item(self, obj):
        item = obj.items.first()
        if item:
            return {
                'name': item.product_name,
                'image': item.product_image,
                'quantity': item.quantity
            }
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'total_amount', 'pay_amount', 'status',
                  'status_display', 'receiver_name', 'receiver_phone', 
                  'receiver_address', 'delivery_type', 'delivery_fee',
                  'is_subscription', 'subscription_frequency', 'subscription_periods',
                  'current_period', 'remark', 'items', 'paid_at', 'shipped_at',
                  'delivered_at', 'completed_at', 'created_at']


class OrderCreateSerializer(serializers.Serializer):
    """订单创建序列化器"""
    address_id = serializers.IntegerField(required=False)
    receiver_name = serializers.CharField(max_length=50)
    receiver_phone = serializers.CharField(max_length=11)
    receiver_address = serializers.CharField()
    remark = serializers.CharField(required=False, allow_blank=True)
    is_subscription = serializers.BooleanField(default=False)
    subscription_frequency = serializers.CharField(required=False, allow_blank=True)
    subscription_periods = serializers.IntegerField(default=1)
    items = serializers.ListField(child=serializers.DictField())

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('请选择商品')
        return value


class CartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_id', 'quantity', 'selected', 
                  'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_total_price(self, obj):
        return float(obj.product.price * obj.quantity)


class CartUpdateSerializer(serializers.Serializer):
    """购物车更新序列化器"""
    quantity = serializers.IntegerField(min_value=1, required=False)
    selected = serializers.BooleanField(required=False)


class PaymentSerializer(serializers.ModelSerializer):
    """支付记录序列化器"""
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_no', 'trade_no', 'amount', 
                  'method', 'status', 'paid_at', 'created_at']
