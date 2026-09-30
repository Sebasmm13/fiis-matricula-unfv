import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade, Course

students_2010 = Student.objects.filter(plan__name__icontains='2010')
print(f"Students with Plan 2010: {students_2010.count()}")

for student in students_2010:
    grades = FinalGrade.objects.filter(student=student)
    print(f"\nStudent: {student.student_code} ({student.full_name})")
    print(f"Total Grades: {grades.count()}")
    for g in grades.order_by('course__semester'):
        print(f" - C{g.course.semester} | {g.course.curricular_code} | {g.course.name} | {g.grade} | {g.status}")

