"""
订单模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, AdminOrderViewSet, PaymentViewSet

router = DefaultRouter()
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')

admin_router = DefaultRouter()
admin_router.register('orders', AdminOrderViewSet, basename='admin-order')
admin_router.register('payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
