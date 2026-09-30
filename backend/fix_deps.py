import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

# Student 2023023807
student = Student.objects.filter(student_code='2023023807').first()

if student:
    grades = FinalGrade.objects.filter(student=student)
    for g in grades:
        if not g.passed:
            print(f"FAILED COURSE: {g.course.curricular_code} - {g.course.name}")
            # Find any course that requires this course
            deps = FinalGrade.objects.filter(student=student, course__prerequisites=g.course)
            for d in deps:
                print(f"  -> Deleting dependent course: {d.course.curricular_code} - {d.course.name}")
                d.delete()
