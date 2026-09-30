import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

students_2010 = Student.objects.filter(plan__name__icontains='2010')
for student in students_2010:
    grades = FinalGrade.objects.filter(student=student)
    print(f"Student: {student.student_code} ({student.full_name}) has {grades.count()} grades.")
