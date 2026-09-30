import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

student = Student.objects.filter(student_code='2023023807').first()
for g in FinalGrade.objects.filter(student=student):
    print(g.course.curricular_code, g.course.name)
