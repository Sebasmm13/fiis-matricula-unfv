import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

for c in Course.objects.filter(curricular_code__startswith='E-2'):
    print(c.curricular_code, c.name, c.elective_track)

for c in Course.objects.filter(name__icontains='SQL'):
    print(c.curricular_code, c.name, c.elective_track)
