
import os
import sys
import traceback

LOG_FILE = 'verify_log.txt'

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str(msg) + '\n')
    print(msg)

try:
    # Setup Django environment
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    log("Importing django...")
    import django
    django.setup()
    log("Django setup complete.")

    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDate
    from apps.orders.models import Order

    log(f"Current Time: {timezone.now()}")
    log("-" * 50)

    # 1. Check Total Orders
    total_orders = Order.objects.count()
    log(f"Total Orders in DB: {total_orders}")

    # 2. Check Recent Orders (Last 7 Days)
    days = 7
    today = timezone.now().date()
    start_date = today - timedelta(days=days-1)
    
    log(f"Checking orders from {start_date} to {today}")
    
    recent_orders = Order.objects.filter(
        created_at__date__gte=start_date
    ).order_by('-created_at')
    
    log(f"Recent Orders Count: {recent_orders.count()}")
    
    if recent_orders.exists():
        log("\nSample Recent Orders:")
        for order in recent_orders[:5]:
            log(f"Order: {order.order_no}, Status: {order.status}, Created: {order.created_at}, Amount: {order.pay_amount}")
    else:
        log("NO ORDERS FOUND in the last 7 days.")

    # 3. Simulate Dashboard Query
    log("-" * 50)
    log("Simulating Dashboard Query logic...")
    
    daily_sales_qs = Order.objects.filter(
        created_at__date__gte=start_date,
        status__in=['paid', 'shipped', 'delivered', 'completed']
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('pay_amount'),
        count=Count('id')
    ).order_by('date')
    
    results = list(daily_sales_qs)
    log(f"Dashboard Query Result: {results}")

    if not results:
        log("Dashboard query returned EMPTY list.")
        
except Exception:
    log("CRASHED!")
    log(traceback.format_exc())
