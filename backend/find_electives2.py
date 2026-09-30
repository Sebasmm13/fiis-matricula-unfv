import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course, FinalGrade

print('All 2019 Electives:')
for c in Course.objects.filter(plan__name='Plan 2019', curricular_code__startswith='E'):
    print(c.curricular_code, c.name, c.semester)
