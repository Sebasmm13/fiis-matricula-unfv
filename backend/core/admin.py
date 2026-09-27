from django.contrib import admin

from .models import (
    AuditLog,
    Course,
    Enrollment,
    EnrollmentLine,
    FinalGrade,
    Meeting,
    Period,
    Plan,
    Preselection,
    Section,
    Student,
    Teacher,
)

for model in [
    Plan,
    Course,
    Teacher,
    Student,
    Period,
    Section,
    Meeting,
    FinalGrade,
    Preselection,
    Enrollment,
    EnrollmentLine,
    AuditLog,
]:
    admin.site.register(model)
