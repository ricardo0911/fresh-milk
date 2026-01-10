"""
评论模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, AdminCommentViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')

admin_router = DefaultRouter()
admin_router.register('comments', AdminCommentViewSet, basename='admin-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
