import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period

p1 = Period.objects.get(code='2026-1')
p1.is_current = False
p1.save()

p2 = Period.objects.get(code='2026-2')
p2.is_current = True
p2.status = 'pre' # Or 'draft', but we need 'pre' or 'enroll' for students to see it
p2.save()

print("Set 2026-2 as current period.")
