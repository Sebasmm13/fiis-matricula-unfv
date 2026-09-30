import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

removed_any_total = False
while True:
    removed_any = False
    grades = FinalGrade.objects.all()
    # Unpassed courses are those where passed=False
    passed_ids = set(grades.filter(passed=True).values_list('course_id', flat=True))
    
    for g in grades:
        if not g.passed: continue
        reqs = g.course.prerequisites.all()
        for r in reqs:
            # Did the SAME STUDENT pass the prereq?
            has_passed_req = FinalGrade.objects.filter(student=g.student, course=r, passed=True).exists()
            if not has_passed_req:
                print(f"Removing {g.course.name} for {g.student.student_code} because prereq {r.name} is not passed.")
                g.delete()
                removed_any = True
                removed_any_total = True
                break
    
    if not removed_any:
        break

if not removed_any_total:
    print("No violations found.")

