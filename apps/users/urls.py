"""
用户模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserLoginView, UserViewSet, UserAddressViewSet,
    AdminUserViewSet, UserLogViewSet, wx_login,
    send_reset_code, verify_reset_code, reset_password,
    MembershipPlanViewSet, MembershipOrderViewSet, upload_image
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', UserAddressViewSet, basename='address')
router.register('membership/plans', MembershipPlanViewSet, basename='membership-plan')
router.register('membership/orders', MembershipOrderViewSet, basename='membership-order')

admin_router = DefaultRouter()
admin_router.register('users', AdminUserViewSet, basename='admin-user')
admin_router.register('logs', UserLogViewSet, basename='user-log')

urlpatterns = [
    # 认证
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/wx-login/', wx_login, name='wx-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('auth/send-reset-code/', send_reset_code, name='send-reset-code'),
    path('auth/verify-reset-code/', verify_reset_code, name='verify-reset-code'),
    path('auth/reset-password/', reset_password, name='reset-password'),

    # 图片上传
    path('upload/image/', upload_image, name='upload-image'),

    # 用户API
    path('', include(router.urls)),

    # 管理员API
    path('admin/', include(admin_router.urls)),
]

