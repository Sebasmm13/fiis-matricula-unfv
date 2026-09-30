import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

print('Grades for student:')
for g in FinalGrade.objects.all():
    if g.course.curricular_code in ['E-2.2', 'E-4.2']:
        print(f"Student: {g.student.code}, Course: {g.course.curricular_code} - {g.course.name}, Track: {g.course.elective_track}")
