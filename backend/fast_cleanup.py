import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade, Course

all_grades = list(FinalGrade.objects.select_related('course').prefetch_related('course__prerequisites').all())
student_passed_courses = {}

for g in all_grades:
    if g.passed:
        student_passed_courses.setdefault(g.student_id, set()).add(g.course_id)

deleted_count = 0

while True:
    removed_any = False
    for g in all_grades:
        if not g.id: continue # Already deleted locally
        
        has_all_reqs = True
        for r in g.course.prerequisites.all():
            if r.id not in student_passed_courses.get(g.student_id, set()):
                has_all_reqs = False
                break
                
        if not has_all_reqs:
            print(f"Deleting {g.course.curricular_code} - {g.course.name} for student {g.student_id}")
            g.delete()
            if g.passed:
                student_passed_courses[g.student_id].discard(g.course_id)
            g.id = None # Mark as deleted in our list
            removed_any = True
            deleted_count += 1
            
    if not removed_any:
        break

print(f"Finished. Deleted {deleted_count} incongruent grades.")
