import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

# Student 2023023807
student = Student.objects.filter(student_code='2023023807').first()

if student:
    grades = FinalGrade.objects.filter(student=student)
    print("Grades for 2023023807:")
    for g in grades.order_by('course__semester'):
        print(f"[{g.course.curricular_code}] {g.course.name} - Score: {g.score} - Passed: {g.passed}")
