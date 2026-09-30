import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinalGrade

print('Deleting only non-Mencion 2 electives...')
deleted, _ = FinalGrade.objects.filter(
    course__elective_track__gt=''
).exclude(
    course__elective_track='Mención 2: Gestión de Datos'
).delete()

print(f"Deleted {deleted} grades.")
