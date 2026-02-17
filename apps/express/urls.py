from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('companies', views.ExpressCompanyViewSet, basename='express-company')
router.register('orders', views.ExpressOrderViewSet, basename='express-order')
router.register('admin', views.AdminExpressViewSet, basename='admin-express')

urlpatterns = [
    path('', include(router.urls)),
]
