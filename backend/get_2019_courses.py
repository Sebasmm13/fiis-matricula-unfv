import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

print("2019 Courses (cycles 1-6):")
for c in Course.objects.filter(plan__name__icontains='2019', semester__lte=6).order_by('semester', 'curricular_code'):
    print(f"C{c.semester} | {c.curricular_code} - {c.name}")
