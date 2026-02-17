"""
统计模块 - 视图
"""
from rest_framework import views, permissions
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime

from apps.users.models import User, UserLog
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from apps.comments.models import Comment
from apps.feedback.models import Feedback


class DashboardView(views.APIView):
    """仪表盘统计"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        # Ensure we have timezone aware datetimes for the range
        today_start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Convert back to UTC for database query if necessary, or let Django handle aware datetimes
        # Using accurate range query is safer than __date
        
        # 基本统计
        total_users = User.objects.filter(is_admin=False).count()
        total_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).aggregate(total=Sum('pay_amount'))['total'] or 0
        
        # 今日统计
        today_orders = Order.objects.filter(
            created_at__range=(today_start, today_end)
        ).count()
        
        today_revenue = Order.objects.filter(
            created_at__range=(today_start, today_end),
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).aggregate(total=Sum('pay_amount'))['total'] or 0
        
        today_users = User.objects.filter(
            date_joined__range=(today_start, today_end)
        ).count()
        
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

        # 使用本地时间计算日期范围
        now = timezone.localtime(timezone.now())
        today = now.date()
        start_date = today - timedelta(days=days-1)

        # 转换为时间范围
        start_datetime = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time()),
            timezone.get_current_timezone()
        )
        end_datetime = timezone.make_aware(
            datetime.combine(today, datetime.max.time()),
            timezone.get_current_timezone()
        )

        # 每日销售额 - 使用时间范围查询
        valid_orders = Order.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime,
            status__in=['paid', 'shipped', 'delivered', 'completed']
        )

        # 按日期分组统计
        sales_dict = {}
        for order in valid_orders:
            order_date = timezone.localtime(order.created_at).date()
            if order_date not in sales_dict:
                sales_dict[order_date] = {'revenue': 0, 'count': 0}
            sales_dict[order_date]['revenue'] += float(order.pay_amount or 0)
            sales_dict[order_date]['count'] += 1

        # 生成完整的日期范围数据
        daily_sales = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            if date in sales_dict:
                daily_sales.append({
                    'date': date.strftime('%m-%d'),
                    'revenue': sales_dict[date]['revenue'],
                    'count': sales_dict[date]['count']
                })
            else:
                daily_sales.append({
                    'date': date.strftime('%m-%d'),
                    'revenue': 0,
                    'count': 0
                })

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
            'daily_sales': daily_sales,
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
        now = timezone.localtime(timezone.now())
        today = now.date()
        start_date = today - timedelta(days=days-1)
        
        start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

        # 1. 每日新增用户
        new_users_qs = User.objects.filter(
            date_joined__gte=start_dt,
            is_admin=False
        ).values('date_joined')
        
        daily_new_users = {}
        for u in new_users_qs:
            local_dt = timezone.localtime(u['date_joined'])
            date_str = local_dt.strftime('%Y-%m-%d')
            daily_new_users[date_str] = daily_new_users.get(date_str, 0) + 1

        # 2. 每日登录用户
        logins_qs = UserLog.objects.filter(
            created_at__gte=start_dt,
            action='login'
        ).values('created_at', 'user_id')
        
        daily_logins = {}
        seen_logins = set()
        
        for log in logins_qs:
            local_dt = timezone.localtime(log['created_at'])
            date_str = local_dt.strftime('%Y-%m-%d')
            key = (date_str, log['user_id'])
            
            if key not in seen_logins:
                seen_logins.add(key)
                daily_logins[date_str] = daily_logins.get(date_str, 0) + 1

        # 3. 组装结果
        result_daily_users = []
        result_daily_logins = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_key = current_date.strftime('%Y-%m-%d')
            
            result_daily_users.append({
                'date': date_key,
                'count': daily_new_users.get(date_key, 0)
            })
            
            result_daily_logins.append({
                'date': date_key,
                'count': daily_logins.get(date_key, 0)
            })
        
        # 用户订购行为
        user_orders = Order.objects.filter(
            status__in=['paid', 'shipped', 'delivered', 'completed']
        ).values('user').annotate(
            order_count=Count('id'),
            total_spent=Sum('pay_amount')
        ).order_by('-total_spent')[:10]
        
        return Response({
            'daily_users': result_daily_users,
            'daily_logins': result_daily_logins,
            'top_buyers': list(user_orders),
        })
