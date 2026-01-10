"""
产品模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, FavoriteViewSet, AdminProductViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('favorites', FavoriteViewSet, basename='favorite')

admin_router = DefaultRouter()
admin_router.register('products', AdminProductViewSet, basename='admin-product')
admin_router.register('categories', CategoryViewSet, basename='admin-category')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
