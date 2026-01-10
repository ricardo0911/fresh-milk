"""
优惠券模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, UserCouponViewSet, CouponActivityViewSet

router = DefaultRouter()
router.register('coupons', CouponViewSet, basename='coupon')
router.register('user-coupons', UserCouponViewSet, basename='user-coupon')
router.register('coupon-activities', CouponActivityViewSet, basename='coupon-activity')

urlpatterns = [
    path('', include(router.urls)),
]
