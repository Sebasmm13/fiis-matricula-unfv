import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

for c in Course.objects.filter(curricular_code__in=['RUP-2026', 'PA3-2026', 'ARDUINO-2026']):
    print(f"{c.curricular_code} - {c.name}")
