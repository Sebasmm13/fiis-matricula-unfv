import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade

student = Student.objects.filter(student_code='2023023807').first()
grades = FinalGrade.objects.filter(student=student)
passed_ids = set(grades.filter(passed=True).values_list('course_id', flat=True))

for g in grades:
    reqs = g.course.prerequisites.all()
    for r in reqs:
        if r.id not in passed_ids:
            print(f"Grade violation: {g.course.name} requires {r.name}")
            g.delete()

