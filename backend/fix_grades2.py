import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade, Course

students_2010 = Student.objects.filter(plan__name__icontains='2010')

for student in students_2010:
    while True:
        removed_any = False
        grades = FinalGrade.objects.filter(student=student)
        passed_ids = set(grades.filter(passed=True).values_list('course_id', flat=True))
        
        for g in grades:
            reqs = g.course.prerequisites.all()
            for r in reqs:
                if r.id not in passed_ids:
                    print(f"Removing {g.course.name} for {student.student_code} because prereq {r.name} is not passed.")
                    g.delete()
                    removed_any = True
                    break
        
        if not removed_any:
            break
            
