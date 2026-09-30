import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Plan
for p in Plan.objects.all():
    print(p.name, p.id)
