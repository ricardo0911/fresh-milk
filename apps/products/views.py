"""
产品模块 - 视图
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F
from .models import Category, Product, ProductImage, Favorite
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer, FavoriteSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = Category.objects.all()
        if self.action == 'list' and not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """产品视图集"""
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subtitle', 'description']
    ordering_fields = ['price', 'sales_count', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # 普通用户只能看到上架商品
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # 分类筛选
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 热门/新品筛选
        is_hot = self.request.query_params.get('is_hot')
        is_new = self.request.query_params.get('is_new')
        is_subscription = self.request.query_params.get('is_subscription')
        
        if is_hot == 'true':
            queryset = queryset.filter(is_hot=True)
        if is_new == 'true':
            queryset = queryset.filter(is_new=True)
        if is_subscription == 'true':
            queryset = queryset.filter(is_subscription=True)
        
        # 价格筛选
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加浏览量
        Product.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """热门产品"""
        queryset = self.get_queryset().filter(is_hot=True)[:10]
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """新品上市"""
        queryset = self.get_queryset().filter(is_new=True)[:10]
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def subscription(self, request):
        """周期购产品"""
        queryset = self.get_queryset().filter(is_subscription=True)
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        """推荐产品 - 基于协同过滤"""
        # 简单推荐：基于销量和浏览量
        queryset = self.get_queryset().order_by('-sales_count', '-view_count')[:10]
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """收藏视图集"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': '请指定产品ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': '产品不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, product=product
        )
        
        if created:
            return Response({'message': '收藏成功'}, status=status.HTTP_201_CREATED)
        return Response({'message': '已收藏'})

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """切换收藏状态"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': '请指定产品ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = Favorite.objects.get(user=request.user, product_id=product_id)
            favorite.delete()
            return Response({'message': '取消收藏', 'is_favorited': False})
        except Favorite.DoesNotExist:
            try:
                product = Product.objects.get(pk=product_id, is_active=True)
                Favorite.objects.create(user=request.user, product=product)
                return Response({'message': '收藏成功', 'is_favorited': True})
            except Product.DoesNotExist:
                return Response({'error': '产品不存在'}, status=status.HTTP_404_NOT_FOUND)


class AdminProductViewSet(viewsets.ModelViewSet):
    """管理员产品视图集"""
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """上架/下架产品"""
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        return Response({
            'message': '操作成功', 
            'is_active': product.is_active
        })

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """更新库存"""
        product = self.get_object()
        stock = request.data.get('stock')
        if stock is None:
            return Response({'error': '请指定库存数量'}, status=status.HTTP_400_BAD_REQUEST)
        product.stock = int(stock)
        product.save()
        return Response({'message': '库存更新成功', 'stock': product.stock})
