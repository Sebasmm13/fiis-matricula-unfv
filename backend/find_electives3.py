import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

for c in Course.objects.filter(plan__name='Plan 2019', is_elective=True):
    print(c.curricular_code, c.name, c.semester)
