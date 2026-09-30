import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

# Delete grades for all electives in 2019 plan except 'Base de Datos' or 'Data Design' or something similar
# Let's find out the exact name
for g in FinalGrade.objects.filter(course__plan__name='Plan 2019', course__curricular_code__startswith='E-'):
    print(g.course.curricular_code, g.course.name)

