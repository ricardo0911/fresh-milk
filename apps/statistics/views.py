"""
统计模块 - 视图
"""
from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, UserLog
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from apps.comments.models import Comment
from apps.feedback.models import Feedback


class DashboardView(views.APIView):
    """仪表盘统计"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        
        # 基本统计
        total_users = User.objects.filter(is_admin=False).count()
        total_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).aggregate(total=Sum('pay_amount'))['total'] or 0
        
        # 今日统计
        today_orders = Order.objects.filter(created_at__date=today).count()
        today_revenue = Order.objects.filter(
            created_at__date=today,
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).aggregate(total=Sum('pay_amount'))['total'] or 0
        today_users = User.objects.filter(date_joined__date=today).count()
        
        # 待处理事项
        pending_orders = Order.objects.filter(status='paid').count()
        pending_feedbacks = Feedback.objects.filter(status='pending').count()
        low_stock_products = Product.objects.filter(stock__lt=10, is_active=True).count()
        
        return Response({
            'overview': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
            },
            'today': {
                'orders': today_orders,
                'revenue': float(today_revenue),
                'new_users': today_users,
            },
            'pending': {
                'orders': pending_orders,
                'feedbacks': pending_feedbacks,
                'low_stock': low_stock_products,
            }
        })


class SalesStatisticsView(views.APIView):
    """销售统计"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days-1)
        
        # 每日销售额
        daily_sales = Order.objects.filter(
            created_at__date__gte=start_date,
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('pay_amount'),
            count=Count('id')
        ).order_by('date')
        
        # 分类销售占比
        category_sales = OrderItem.objects.filter(
            order__status__in=['paid', 'shipped', 'delivered', 'completed'],
            product__isnull=False
        ).values(
            'product__category__name'
        ).annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('-total')[:10]
        
        return Response({
            'daily_sales': list(daily_sales),
            'category_sales': list(category_sales),
        })


class ProductStatisticsView(views.APIView):
    """产品统计"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # 热门产品(按销量)
        hot_products = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count')[:10].values(
            'id', 'name', 'sales_count', 'view_count', 'stock'
        )
        
        # 高浏览产品
        popular_products = Product.objects.filter(
            is_active=True
        ).order_by('-view_count')[:10].values(
            'id', 'name', 'sales_count', 'view_count', 'stock'
        )
        
        # 低库存预警
        low_stock = Product.objects.filter(
            is_active=True, stock__lt=10
        ).values('id', 'name', 'stock')
        
        # 分类产品数量
        category_count = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).values('name', 'product_count')
        
        return Response({
            'hot_products': list(hot_products),
            'popular_products': list(popular_products),
            'low_stock': list(low_stock),
            'category_count': list(category_count),
        })


class UserStatisticsView(views.APIView):
    """用户统计"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days-1)
        
        # 每日新增用户
        daily_users = User.objects.filter(
            date_joined__date__gte=start_date,
            is_admin=False
        ).annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 每日登录用户(UV)
        daily_logins = UserLog.objects.filter(
            created_at__date__gte=start_date,
            action='login'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('user', distinct=True)
        ).order_by('date')
        
        # 用户订购行为
        user_orders = Order.objects.filter(
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).values('user').annotate(
            order_count=Count('id'),
            total_spent=Sum('pay_amount')
        ).order_by('-total_spent')[:10]
        
        return Response({
            'daily_users': list(daily_users),
            'daily_logins': list(daily_logins),
            'top_buyers': list(user_orders),
        })
