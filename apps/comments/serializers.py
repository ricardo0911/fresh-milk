"""
评论模块 - 序列化器
"""
from rest_framework import serializers
from .models import Comment, CommentLike


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'avatar', 'product', 'product_name',
                  'order', 'rating', 'content', 'images', 'likes', 'is_anonymous',
                  'is_approved', 'reply', 'replied_at', 'is_liked', 'created_at']
        read_only_fields = ['id', 'user', 'likes', 'is_approved', 'reply', 
                            'replied_at', 'created_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(user=request.user, comment=obj).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    class Meta:
        model = Comment
        fields = ['product', 'order', 'rating', 'content', 'images', 'is_anonymous']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('评分必须在1-5之间')
        return value
