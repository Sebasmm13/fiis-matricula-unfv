import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period

for p in Period.objects.filter(is_current=True):
    print(p.code, p.is_current, p.status)
