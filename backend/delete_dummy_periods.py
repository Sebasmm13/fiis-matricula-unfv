import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period
Period.objects.filter(code__in=['2026-1', '2026-2']).delete()
print('Dummy periods deleted')
