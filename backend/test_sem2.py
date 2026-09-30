import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, Course, Section, Period
from core.services import eligible_course_ids

student = Student.objects.filter(plan__active=True).first()
if not student:
    sys.exit(0)

# Simulate passing all Semester 1 courses (IDs 1-8)
passed = {1, 2, 3, 4, 5, 6, 7, 8}

eligible = eligible_course_ids(student, passed)
print("Eligible:", eligible)
eligible_courses = Course.objects.filter(id__in=eligible)
print("Eligible courses:", [f"{c.name} (Sem {c.semester})" for c in eligible_courses])

period = Period.objects.get(code='2026-2')
sections = Section.objects.filter(period=period, published=True, course_id__in=eligible)
print("Sections found:", sections.count())
for s in sections:
    print(f" - {s.course.name} ({s.period.code})")
