"""
评论模块 - 序列化器
"""
from rest_framework import serializers
from .models import Comment, CommentLike


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'avatar', 'product', 'product_name',
                  'product_image', 'order', 'rating', 'content', 'images', 'likes', 
                  'is_anonymous', 'is_approved', 'reply', 'replied_at', 'is_liked', 'created_at']
        read_only_fields = ['id', 'user', 'likes', 'is_approved', 'reply', 
                            'replied_at', 'created_at']

    def get_username(self, obj):
        if obj.user:
            return obj.user.nickname or obj.user.username
        return '匿名用户'
    
    def get_avatar(self, obj):
        if obj.user and obj.user.avatar:
            return obj.user.avatar.url
        return None

    def get_product_image(self, obj):
        if obj.product and obj.product.cover_image:
            return obj.product.cover_image.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(user=request.user, comment=obj).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    class Meta:
        model = Comment
        fields = ['product', 'order', 'rating', 'content', 'images', 'is_anonymous', 'user']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('评分必须在1-5之间')
        return value

    def create(self, validated_data):
        # 如果没有提供 user，设置为 None（用于匿名评论）
        if 'user' not in validated_data or validated_data['user'] is None:
            validated_data.pop('user', None)
        return super().create(validated_data)
