"""
鲜牛奶订购管理系统 - 主URL配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('', include('apps.users.urls')),
        path('', include('apps.products.urls')),
        path('', include('apps.orders.urls')),
        path('', include('apps.comments.urls')),
        path('', include('apps.notifications.urls')),
        path('', include('apps.feedback.urls')),
        path('', include('apps.statistics.urls')),
        path('', include('apps.delivery.urls')),
        path('', include('apps.coupons.urls')),
        path('', include('apps.subscriptions.urls')),
        path('', include('apps.posts.urls')),
        path('express/', include('apps.express.urls')),
    ])),
]

# 开发环境静态文件和媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
