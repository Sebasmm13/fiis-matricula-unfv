import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

print('Deleting all elective grades except E-2.* (Data Design track)...')
deleted, _ = FinalGrade.objects.filter(
    course__elective_track__isnull=False
).exclude(
    course__curricular_code__startswith='E-2'
).delete()

print(f"Deleted {deleted} grades.")
