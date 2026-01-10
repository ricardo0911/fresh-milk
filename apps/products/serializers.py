"""
产品模块 - 序列化器
"""
from rest_framework import serializers
from .models import Category, Product, ProductImage, Favorite


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description', 'sort_order', 'is_active', 
                  'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    """产品图片序列化器"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'sort_order']


class ProductListSerializer(serializers.ModelSerializer):
    """产品列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'subtitle', 'price', 'original_price', 
                  'cover_image', 'specification', 'sales_count', 'is_hot', 
                  'is_new', 'is_subscription', 'category_name', 'is_favorited']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, product=obj).exists()
        return False


class ProductDetailSerializer(serializers.ModelSerializer):
    """产品详情序列化器"""
    category = CategorySerializer(read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'subtitle', 'price', 'original_price', 
                  'specification', 'origin', 'shelf_life', 'description', 
                  'detail', 'cover_image', 'images', 'stock', 'sales_count', 
                  'view_count', 'is_hot', 'is_new', 'is_subscription', 
                  'is_active', 'category', 'product_images', 'is_favorited',
                  'comment_count', 'avg_rating', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, product=obj).exists()
        return False

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_avg_rating(self, obj):
        comments = obj.comments.filter(is_approved=True)
        if comments.exists():
            return round(sum(c.rating for c in comments) / comments.count(), 1)
        return 5.0


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """产品创建/更新序列化器"""
    class Meta:
        model = Product
        fields = ['name', 'subtitle', 'category', 'price', 'original_price',
                  'specification', 'origin', 'shelf_life', 'description',
                  'detail', 'cover_image', 'images', 'stock', 'is_hot',
                  'is_new', 'is_subscription', 'is_active']


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']
