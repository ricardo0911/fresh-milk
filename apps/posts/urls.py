"""
社区帖子模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, PostViewSet, AdminTopicViewSet, AdminPostViewSet

router = DefaultRouter()
router.register('topics', TopicViewSet, basename='topic')
router.register('posts', PostViewSet, basename='post')

admin_router = DefaultRouter()
admin_router.register('topics', AdminTopicViewSet, basename='admin-topic')
admin_router.register('posts', AdminPostViewSet, basename='admin-post')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]
