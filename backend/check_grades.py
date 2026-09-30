import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

student = Student.objects.filter(student_code='2023023807').first()
grades = FinalGrade.objects.filter(student=student)

for g in grades.order_by('course__curricular_code')[:10]:
    print(f"{g.course.curricular_code} {g.course.name} | {g.score} | {g.passed}")

