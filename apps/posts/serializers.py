"""
社区帖子模块 - 序列化器
"""
from rest_framework import serializers
from .models import Topic, Post, PostLike


class TopicSerializer(serializers.ModelSerializer):
    """话题序列化器"""
    class Meta:
        model = Topic
        fields = ['id', 'name', 'image', 'description', 'is_active', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostUserSerializer(serializers.Serializer):
    """帖子用户信息序列化器"""
    id = serializers.IntegerField()
    nickname = serializers.CharField(default='')
    avatar = serializers.CharField(default='')


class PostSerializer(serializers.ModelSerializer):
    """帖子序列化器"""
    user = PostUserSerializer(read_only=True)
    username = serializers.CharField(source='user.nickname', read_only=True, default='')
    topic_name = serializers.CharField(source='topic.name', read_only=True, default='')

    class Meta:
        model = Post
        fields = ['id', 'user', 'username', 'topic', 'topic_name', 'tab', 'content',
                  'image', 'images', 'likes', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'likes', 'created_at', 'updated_at']


class PostCreateSerializer(serializers.ModelSerializer):
    """帖子创建序列化器"""
    class Meta:
        model = Post
        fields = ['topic', 'tab', 'content', 'image', 'images']
