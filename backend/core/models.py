from django.conf import settings
from django.db import models
from django.db.models import Q


class Plan(models.Model):
    name = models.CharField(max_length=140, unique=True)
    active = models.BooleanField(default=True)
    source = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="courses")
    curricular_code = models.CharField(max_length=20)
    name = models.CharField(max_length=220)
    semester = models.PositiveSmallIntegerField()
    credits = models.PositiveSmallIntegerField(null=True, blank=True)
    theory_hours = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Horas académicas semanales")
    practice_hours = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Horas académicas semanales")
    elective_track = models.CharField(max_length=120, blank=True)
    academic_data_verified = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["plan", "curricular_code"], name="unique_course_in_plan")]

    def __str__(self):
        return f"{self.curricular_code} {self.name}"


class Teacher(models.Model):
    name = models.CharField(max_length=180, unique=True)
    active = models.BooleanField(default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="teacher"
    )

    def __str__(self):
        return self.name


class ProfilePhoto(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile_photo")
    image = models.BinaryField()
    updated_at = models.DateTimeField(auto_now=True)


class AccountSecurity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="security")
    must_change_password = models.BooleanField(default=False)
    activation_pending = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True, blank=True)


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="student")
    student_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=180)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class Period(models.Model):
    code = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Borrador"), ("pre", "Prematrícula"), ("enroll", "Matrícula"), ("closed", "Cerrado")],
        default="draft",
    )
    max_credits = models.PositiveSmallIntegerField(default=44)
    pre_start = models.DateTimeField(null=True, blank=True)
    pre_end = models.DateTimeField(null=True, blank=True)
    enroll_start = models.DateTimeField(null=True, blank=True)
    enroll_end = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    convalidation_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["is_current"], condition=Q(is_current=True), name="single_current_period")
        ]

    def __str__(self):
        return self.code


class Section(models.Model):
    period = models.ForeignKey(Period, on_delete=models.PROTECT, related_name="sections")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True, blank=True, related_name="sections")
    section_code = models.CharField(max_length=15)
    official_code = models.CharField(max_length=30, blank=True)
    raw_name = models.CharField(max_length=220)
    cycle = models.CharField(max_length=10, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, null=True, blank=True)
    classroom = models.CharField(max_length=60, blank=True)
    capacity = models.PositiveSmallIntegerField(default=35)
    published = models.BooleanField(default=False)
    source_row = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.period.code} {self.raw_name} {self.section_code}"


class Meeting(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="meetings")
    day = models.PositiveSmallIntegerField(
        choices=[
            (i, n) for i, n in enumerate(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        ]
    )
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(end__gt=models.F("start")), name="meeting_positive_duration")]


class FinalGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="grades")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    score = models.DecimalField(max_digits=4, decimal_places=2)
    passed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "course", "period"], name="unique_grade_attempt"),
            models.CheckConstraint(condition=Q(score__gte=0) & Q(score__lte=20), name="valid_score_range"),
        ]


class Preselection(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="preselections")
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    preferred_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "period", "course"], name="one_preference_per_course")
        ]


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "period"], name="one_enrollment_per_period")]


class EnrollmentLine(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lines")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="enrollment_lines")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    snapshot = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "course"], name="one_section_per_course"),
            models.UniqueConstraint(fields=["enrollment", "section"], name="no_duplicate_enrollment_line"),
        ]


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=80)
    target = models.CharField(max_length=160)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
