import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period

for p in Period.objects.all():
    print(p.code, p.is_current, p.status)
