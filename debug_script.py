
import os
import sys
import traceback

print("Starting checks...")
try:
    import django
    print("Django imported")
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    print("Settings configured")
    django.setup()
    print("Django setup complete")
    
    from apps.orders.models import Order
    print(f"Order model imported. Count: {Order.objects.count()}")

except Exception:
    print("CRASHED!")
    traceback.print_exc()
