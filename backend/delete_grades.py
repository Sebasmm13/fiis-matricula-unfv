import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade, Course

print('Deleting all 2019 elective grades except E-2.* (Data Design track)...')
deleted, _ = FinalGrade.objects.filter(
    course__plan__name='Plan 2019',
    course__elective_track__isnull=False
).exclude(
    course__curricular_code__startswith='E-2'
).delete()

print(f"Deleted {deleted} grades.")
