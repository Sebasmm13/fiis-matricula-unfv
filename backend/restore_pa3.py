import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course, FinalGrade, Period, Student

pa3 = Course.objects.filter(curricular_code='PA3-2026').first()
if pa3:
    if pa3.credits is None:
        pa3.credits = 3
        pa3.save()
        print("Set PA3 credits to 3")

    historical_period = Period.objects.get(code='HISTORICO')
    luis = Student.objects.filter(full_name__icontains='luis').first()
    
    # Restore grade for Luis
    FinalGrade.objects.create(
        student=luis,
        course=pa3,
        period=historical_period,
        score=Decimal(14),
        passed=True
    )
    print("Restored PA3 grade for Luis")
