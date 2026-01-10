"""
统计模块 - URL配置
"""
from django.urls import path
from .views import DashboardView, SalesStatisticsView, ProductStatisticsView, UserStatisticsView

urlpatterns = [
    path('admin/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/statistics/sales/', SalesStatisticsView.as_view(), name='sales-statistics'),
    path('admin/statistics/products/', ProductStatisticsView.as_view(), name='product-statistics'),
    path('admin/statistics/users/', UserStatisticsView.as_view(), name='user-statistics'),
]
