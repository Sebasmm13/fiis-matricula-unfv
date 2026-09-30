import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Plan, Course

print("Plans:")
for p in Plan.objects.all():
    print(p.id, p.name)

print("\nCourses in plan 2019:")
for c in Course.objects.filter(plan_id=1, semester__lte=6).order_by('semester', 'curricular_code'):
    print(f"C{c.semester} | {c.curricular_code} - {c.name}")
