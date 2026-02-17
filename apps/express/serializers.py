from rest_framework import serializers
from .models import ExpressCompany, ExpressOrder, ExpressTrace


class ExpressCompanySerializer(serializers.ModelSerializer):
    """快递公司序列化器"""

    class Meta:
        model = ExpressCompany
        fields = ['id', 'code', 'name', 'is_active', 'is_default']


class ExpressCompanyDetailSerializer(serializers.ModelSerializer):
    """快递公司详情序列化器（管理员用）"""

    class Meta:
        model = ExpressCompany
        fields = '__all__'


class ExpressTraceSerializer(serializers.ModelSerializer):
    """物流轨迹序列化器"""

    class Meta:
        model = ExpressTrace
        fields = ['time', 'status', 'description', 'location']


class ExpressOrderSerializer(serializers.ModelSerializer):
    """快递订单序列化器"""
    express_company_name = serializers.CharField(source='express_company.name', read_only=True)
    traces = ExpressTraceSerializer(many=True, read_only=True)

    class Meta:
        model = ExpressOrder
        fields = [
            'id', 'order', 'express_company', 'express_company_name',
            'express_no', 'status', 'receiver_name', 'receiver_phone',
            'receiver_address', 'freight', 'created_at', 'collected_at',
            'signed_at', 'traces'
        ]


class ExpressShipSerializer(serializers.Serializer):
    """快递发货序列化器"""
    express_company_code = serializers.CharField(help_text='快递公司代码: SF/YTO')
    remark = serializers.CharField(required=False, allow_blank=True, help_text='备注')
