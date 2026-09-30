import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period, Course, Teacher, Section, SectionMeeting

p1 = Period.objects.get(code='2027-1')
p2 = Period.objects.get(code='2027-2')
teachers = list(Teacher.objects.all())

# Get courses for odd semesters (I, III, V, VII, IX)
courses_odd = Course.objects.filter(semester__in=[1, 3, 5, 7, 9])
# Get courses for even semesters (II, IV, VI, VIII, X)
courses_even = Course.objects.filter(semester__in=[2, 4, 6, 8, 10])

for c in courses_odd:
    if Section.objects.filter(period=p1, course=c).exists():
        continue
    sec = Section.objects.create(
        period=p1, course=c, section="MA", classroom="B-101",
        teacher=random.choice(teachers) if teachers else None,
        capacity=35, available=35, published=True
    )
    SectionMeeting.objects.create(section=sec, day=1, start="08:00", end="09:40")

for c in courses_even:
    if Section.objects.filter(period=p2, course=c).exists():
        continue
    sec = Section.objects.create(
        period=p2, course=c, section="MA", classroom="B-102",
        teacher=random.choice(teachers) if teachers else None,
        capacity=35, available=35, published=True
    )
    SectionMeeting.objects.create(section=sec, day=2, start="10:00", end="11:40")

print('Mock sections created successfully')
