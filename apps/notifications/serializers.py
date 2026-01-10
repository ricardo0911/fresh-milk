"""
消息模块 - 序列化器
"""
from rest_framework import serializers
from .models import Advertisement, Message, UserMessage


class AdvertisementSerializer(serializers.ModelSerializer):
    """广告序列化器"""
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'image', 'link', 'link_type', 'link_id',
                  'position', 'sort_order', 'start_time', 'end_time',
                  'is_active', 'click_count', 'created_at']
        read_only_fields = ['id', 'click_count', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """系统消息序列化器"""
    type_display = serializers.CharField(source='get_message_type_display', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'title', 'content', 'message_type', 'type_display',
                  'image', 'link', 'is_global', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserMessageSerializer(serializers.ModelSerializer):
    """用户消息序列化器"""
    message = MessageSerializer(read_only=True)

    class Meta:
        model = UserMessage
        fields = ['id', 'message', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at']
