"""
配送模块 - URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryPersonViewSet, DeliveryRecordViewSet, DeliveryRouteViewSet

router = DefaultRouter()
router.register('delivery-persons', DeliveryPersonViewSet, basename='delivery-person')
router.register('delivery-records', DeliveryRecordViewSet, basename='delivery-record')
router.register('delivery-routes', DeliveryRouteViewSet, basename='delivery-route')

urlpatterns = [
    path('', include(router.urls)),
]
