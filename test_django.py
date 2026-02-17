import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

output = []
try:
    import django
    django.setup()
    output.append("Django setup OK")

    from django.core.management import call_command
    call_command('check')
    output.append("Django check OK")
except Exception as e:
    output.append(f"Error: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
