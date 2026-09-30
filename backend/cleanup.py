import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

while True:
    removed_any = False
    for g in FinalGrade.objects.all():
        # Get passed IDs for this student
        passed_ids = set(FinalGrade.objects.filter(student=g.student, passed=True).values_list('course_id', flat=True))
        
        for r in g.course.prerequisites.all():
            if r.id not in passed_ids:
                print(f"Deleting grade {g.course.name} for {g.student.student_code} because prereq {r.name} not passed.")
                g.delete()
                removed_any = True
                break
    if not removed_any:
        break

print("Finished cleanup.")
