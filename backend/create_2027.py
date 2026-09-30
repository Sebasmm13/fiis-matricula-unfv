import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period
Period.objects.get_or_create(code="2027-I y II", defaults={"max_credits": 44, "status": "draft"})
print('Created 2027-I y II')
