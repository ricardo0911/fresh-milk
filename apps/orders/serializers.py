"""
订单模块 - 序列化器
"""
from rest_framework import serializers
from .models import Order, OrderItem, Cart, Payment, RefundRequest
from apps.products.serializers import ProductListSerializer


class OrderUserSerializer(serializers.Serializer):
    """订单用户简要信息"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    nickname = serializers.CharField()
    phone = serializers.CharField()


class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    cover_image = serializers.CharField(source='product_image', read_only=True)
    name = serializers.CharField(source='product_name', read_only=True)
    specification = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'cover_image',
                  'name', 'specification', 'price', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']

    def get_specification(self, obj):
        if obj.product:
            return obj.product.specification
        return ''


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    total_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_reviewed = serializers.SerializerMethodField()
    user = OrderUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'user', 'total_amount', 'pay_amount', 'status',
                  'status_display', 'is_subscription', 'total_count', 'items',
                  'is_reviewed', 'created_at', 'express_company', 'express_no',
                  'express_status', 'receiver_name', 'receiver_phone', 'receiver_address']

    def get_total_count(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_is_reviewed(self, obj):
        return obj.comments.exists()


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = OrderUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'user', 'total_amount', 'pay_amount', 'status',
                  'status_display', 'receiver_name', 'receiver_phone',
                  'receiver_address', 'delivery_type', 'delivery_fee',
                  'is_subscription', 'subscription_frequency', 'subscription_periods',
                  'current_period', 'remark', 'items', 'paid_at', 'shipped_at',
                  'delivered_at', 'completed_at', 'created_at',
                  'express_company', 'express_no', 'express_status']


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


class RefundRequestSerializer(serializers.ModelSerializer):
    """退款申请序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    user_info = serializers.SerializerMethodField()
    order_info = serializers.SerializerMethodField()

    class Meta:
        model = RefundRequest
        fields = ['id', 'refund_no', 'order', 'order_no', 'user', 'user_info',
                  'type', 'type_display', 'reason', 'reason_display', 'description',
                  'amount', 'images', 'status', 'status_display',
                  'admin_remark', 'reject_reason',
                  'return_express_company', 'return_express_no', 'return_address',
                  'processed_at', 'completed_at', 'created_at', 'order_info']
        read_only_fields = ['id', 'refund_no', 'user', 'status', 'processed_at', 'completed_at', 'created_at']

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'nickname': getattr(obj.user, 'nickname', '') or obj.user.username,
            'phone': getattr(obj.user, 'phone', '')
        }

    def get_order_info(self, obj):
        order = obj.order
        items = order.items.all()
        return {
            'order_no': order.order_no,
            'total_amount': str(order.total_amount),
            'pay_amount': str(order.pay_amount),
            'status': order.status,
            'items': [{
                'product_name': item.product_name,
                'product_image': item.product_image,
                'price': str(item.price),
                'quantity': item.quantity
            } for item in items]
        }


class RefundRequestCreateSerializer(serializers.Serializer):
    """退款申请创建序列化器"""
    order_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=['refund_only', 'return_refund'], default='refund_only')
    reason = serializers.ChoiceField(choices=['quality', 'not_on_time', 'not_match', 'no_need', 'other'])
    description = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    images = serializers.CharField(required=False, allow_blank=True)
