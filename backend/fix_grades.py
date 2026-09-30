import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade, Course

students_2010 = Student.objects.filter(plan__name__icontains='2010')

for student in students_2010:
    grades = FinalGrade.objects.filter(student=student)
    
    # Let's fix the grades so it makes logical sense
    # First, get all passed courses
    passed_courses_ids = set(grades.filter(passed=True).values_list('course_id', flat=True))
    
    # We need to iteratively remove courses whose prerequisites are not in the passed_courses_ids
    # Because dependencies can be chained, we'll do this until no more are removed
    while True:
        removed_any = False
        grades_to_check = FinalGrade.objects.filter(student=student)
        
        for g in grades_to_check:
            reqs = g.course.prerequisites.all()
            for r in reqs:
                if r.id not in passed_courses_ids:
                    print(f"Removing {g.course.name} because prerequisite {r.name} is not passed.")
                    if g.passed:
                        passed_courses_ids.remove(g.course.id)
                    g.delete()
                    removed_any = True
                    break
        
        if not removed_any:
            break
            
    # Also, the user showed "MATEMATICA" as "No aprobado" with 6.0
    # Wait, my script assigned 11 to 19. How did they get 6.0?
    # Maybe they had a previous grade?
    
