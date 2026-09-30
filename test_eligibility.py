import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Student, Course, Section, Period
from core.services import passed_course_ids, eligible_course_ids, current_period

student = Student.objects.filter(plan__year=2019).first()
if not student:
    print("No Malla 2019 student found.")
else:
    print(f"Student: {student}, Plan: {student.plan}")
    
    passed = passed_course_ids(student)
    print(f"Passed courses count: {len(passed)}")
    
    eligible = eligible_course_ids(student, passed)
    print(f"Eligible courses IDs: {eligible}")
    eligible_courses = Course.objects.filter(id__in=eligible)
    print(f"Eligible courses: {[c.name for c in eligible_courses]}")
    
    period = current_period()
    print(f"Current Period: {period.code}")
    year = period.code[:4]
    annual_periods = Period.objects.filter(code__startswith=year)
    print(f"Annual periods: {[p.code for p in annual_periods]}")
    
    sections = Section.objects.filter(period__in=annual_periods, published=True, course_id__in=eligible)
    print(f"Available sections: {sections.count()}")
    for s in sections:
        print(f" - {s.course.name} ({s.period.code})")
