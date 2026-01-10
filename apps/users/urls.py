"""
用户模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserLoginView, UserViewSet, UserAddressViewSet, 
    AdminUserViewSet, UserLogViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', UserAddressViewSet, basename='address')

admin_router = DefaultRouter()
admin_router.register('users', AdminUserViewSet, basename='admin-user')
admin_router.register('logs', UserLogViewSet, basename='user-log')

urlpatterns = [
    # 认证
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    
    # 用户API
    path('', include(router.urls)),
    
    # 管理员API
    path('admin/', include(admin_router.urls)),
]
