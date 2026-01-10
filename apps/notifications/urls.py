"""
消息模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdvertisementViewSet, MessageListViewSet, UserMessageViewSet,
    AdminAdvertisementViewSet, AdminMessageViewSet
)

router = DefaultRouter()
router.register('ads', AdvertisementViewSet, basename='ad')
router.register('announcements', MessageListViewSet, basename='announcement')
router.register('notifications', UserMessageViewSet, basename='notification')

admin_router = DefaultRouter()
admin_router.register('ads', AdminAdvertisementViewSet, basename='admin-ad')
admin_router.register('messages', AdminMessageViewSet, basename='admin-message')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
