import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, Course, Section, Period
from core.services import eligible_course_ids

student = Student.objects.filter(plan__active=True).first()
passed = set() # 0 passed courses
eligible = eligible_course_ids(student, passed)

period = Period.objects.get(code='2026-2')
year = period.code[:4]
annual_periods = Period.objects.filter(code__startswith=year)

sections = Section.objects.filter(period__in=annual_periods, published=True, course_id__in=eligible)
print("Sections found for 0 passed courses:", sections.count())
