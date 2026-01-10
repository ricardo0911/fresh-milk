"""
配送模块 - 序列化器
"""
from rest_framework import serializers
from .models import DeliveryPerson, DeliveryRecord, DeliveryRoute


class DeliveryPersonSerializer(serializers.ModelSerializer):
    """配送员序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DeliveryPerson
        fields = [
            'id', 'employee_no', 'name', 'phone', 'avatar', 
            'vehicle_type', 'status', 'status_display', 'delivery_area',
            'total_deliveries', 'rating', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'total_deliveries', 'rating', 'created_at']


class DeliveryPersonListSerializer(serializers.ModelSerializer):
    """配送员列表简化序列化器"""
    class Meta:
        model = DeliveryPerson
        fields = ['id', 'employee_no', 'name', 'phone', 'status', 'rating']


class DeliveryRecordSerializer(serializers.ModelSerializer):
    """配送记录序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.name', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    
    class Meta:
        model = DeliveryRecord
        fields = [
            'id', 'order', 'order_no', 'delivery_person', 'delivery_person_name',
            'status', 'status_display', 'receiver_name', 'receiver_phone',
            'receiver_address', 'assigned_at', 'picked_at', 'delivered_at',
            'remark', 'customer_remark'
        ]
        read_only_fields = ['id', 'assigned_at']


class DeliveryRouteSerializer(serializers.ModelSerializer):
    """配送路线序列化器"""
    delivery_person_name = serializers.CharField(source='delivery_person.name', read_only=True)
    records_detail = DeliveryRecordSerializer(source='records', many=True, read_only=True)
    
    class Meta:
        model = DeliveryRoute
        fields = [
            'id', 'delivery_person', 'delivery_person_name', 'date',
            'records', 'records_detail', 'total_orders', 'completed_orders', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
