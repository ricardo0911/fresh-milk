"""
反馈模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, AdminFeedbackViewSet

router = DefaultRouter()
router.register('feedbacks', FeedbackViewSet, basename='feedback')

admin_router = DefaultRouter()
admin_router.register('feedbacks', AdminFeedbackViewSet, basename='admin-feedback')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
