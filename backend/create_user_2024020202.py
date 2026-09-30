import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DJANGO_SECRET_KEY"] = "test"
os.environ["DJANGO_DEBUG"] = "1"
django.setup()

from django.contrib.auth.models import User
from core.models import Student, Plan, Course, FinalGrade, Period, AccountSecurity
from decimal import Decimal

# 1. Get or create user
username = "2024020202"
code = "2024020202"
email = "2024020202@unfv.edu.pe"
password = "2024020202"

user, created = User.objects.get_or_create(username=username, defaults={"email": email})
user.set_password(password)
user.is_active = True
user.save()

security, _ = AccountSecurity.objects.get_or_create(user=user)
security.must_change_password = False
security.activation_pending = False
security.save()

# 2. Get 2019 Plan
plan = Plan.objects.filter(name__icontains="2019").first() or Plan.objects.filter(active=True).first()

# 3. Create/update Student
student, _ = Student.objects.get_or_create(
    student_code=code,
    defaults={
        "user": user,
        "full_name": "Alumno Malla 2019 3er Ciclo",
        "plan": plan,
        "active": True
    }
)
student.user = user
student.plan = plan
student.active = True
student.save()

# 4. Add passing grades for 1st and 2nd cycle courses
prev_period = Period.objects.filter(code="2026-1").first() or Period.objects.first()
courses_1_2 = Course.objects.filter(plan=plan, semester__in=[1, 2])

created_grades = 0
for course in courses_1_2:
    fg, created = FinalGrade.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            "period": prev_period,
            "score": Decimal("16.00"),
            "passed": True
        }
    )
    if not fg.passed:
        fg.passed = True
        fg.score = Decimal("16.00")
        fg.save()
    created_grades += 1

print(f"SUCCESS: User {code} created with password '{password}', plan '{plan.name}', and {created_grades} passed courses for semesters 1 & 2.")
