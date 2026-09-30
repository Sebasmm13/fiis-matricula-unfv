import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, FinalGrade, Course, Period

students_2010 = Student.objects.filter(plan__name__icontains='2010')
period_historico = Period.objects.filter(code='HISTORICO').first()

if not period_historico:
    period_historico = Period.objects.create(code='HISTORICO', status='closed', is_current=False)

for student in students_2010:
    courses = Course.objects.filter(plan=student.plan, semester__lte=6)
    for c in courses:
        score_val = random.randint(11, 19)
        FinalGrade.objects.update_or_create(
            student=student,
            course=c,
            period=period_historico,
            defaults={
                'score': score_val,
                'passed': True
            }
        )
    print(f"Assigned {courses.count()} approved grades to {student.full_name}.")

