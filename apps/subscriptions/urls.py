"""
订阅模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, AdminSubscriptionViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionViewSet, basename='subscription')

admin_router = DefaultRouter()
admin_router.register('subscriptions', AdminSubscriptionViewSet, basename='admin-subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
