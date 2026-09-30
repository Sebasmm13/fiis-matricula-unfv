import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course, FinalGrade

# Fix SQL-101560 credits
sql_course = Course.objects.filter(curricular_code='SQL-101560').first()
if sql_course:
    sql_course.credits = 2
    sql_course.save()
    print("Fixed SQL-101560 credits to 2")

# Delete grades for RUP-2026, PA3-2026, ARDUINO-2026
fake_codes = ['RUP-2026', 'PA3-2026', 'ARDUINO-2026']
deleted, _ = FinalGrade.objects.filter(
    course__curricular_code__in=fake_codes
).delete()
print(f"Deleted {deleted} grades for fake/other electives: {fake_codes}")

# Are there other courses without credits? Let's check them.
for g in FinalGrade.objects.filter(course__credits__isnull=True):
    print(f"Grade without credits: {g.student.code} - {g.course.curricular_code} - {g.course.name}")
