import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

print("Courses in plan 2010:")
for c in Course.objects.filter(plan_id=2, semester__lte=6).order_by('semester', 'curricular_code'):
    print(f"C{c.semester} | {c.curricular_code} - {c.name}")
