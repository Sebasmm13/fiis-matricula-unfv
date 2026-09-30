import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course, FinalGrade

# Assign SQL-101560 to Mención 2
sql_course = Course.objects.filter(curricular_code='SQL-101560').first()
if sql_course:
    sql_course.elective_track = 'Mención 2: Gestión de Datos'
    sql_course.save()
    print("Fixed SQL-101560 elective track")

# Delete all grades for electives except the Mención 2 ones
deleted, _ = FinalGrade.objects.filter(
    course__elective_track__gt=''
).exclude(
    course__curricular_code__in=['E-2.1', 'SQL-101560', 'E-2.3']
).delete()
print(f"Deleted {deleted} elective grades from other tracks")

# Delete grades for E-2.2
deleted_e22, _ = FinalGrade.objects.filter(course__curricular_code='E-2.2').delete()
print(f"Deleted {deleted_e22} grades for fake elective E-2.2")

# Delete E-2.2 because it's a mistake in the DB
Course.objects.filter(curricular_code='E-2.2').delete()
print("Deleted fake elective E-2.2")

