import os
import sys
import django
from django.test import RequestFactory

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.views import Catalog
from django.contrib.auth.models import User
from core.models import Student, Section, Period, Course
from core.services import passed_course_ids, eligible_course_ids

student = Student.objects.filter(plan__active=True).first()
if not student:
    print("No active student found.")
    sys.exit(0)

period = Period.objects.filter(is_current=True).first()
year = period.code[:4]
annual_periods = Period.objects.filter(code__startswith=year)

passed = passed_course_ids(student)
eligible = eligible_course_ids(student, passed)

sections = Section.objects.filter(period__in=annual_periods, published=True, course_id__in=eligible)

print("Period:", period.code)
print("Annual periods:", [p.code for p in annual_periods])
print("Eligible:", eligible)
print("Sections found:", sections.count())

courses = Course.objects.filter(plan=student.plan)
print("Courses in plan:", courses.count())
