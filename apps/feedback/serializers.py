"""
反馈模块 - 序列化器
"""
from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    """反馈序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    type_display = serializers.CharField(source='get_feedback_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'username', 'feedback_type', 'type_display',
                  'title', 'content', 'images', 'contact', 'status', 
                  'status_display', 'reply', 'replied_by', 'replied_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'reply', 'replied_by', 
                            'replied_at', 'created_at', 'updated_at']


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """反馈创建序列化器"""
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'title', 'content', 'images', 'contact']
