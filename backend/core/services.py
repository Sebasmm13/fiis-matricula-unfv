from datetime import datetime

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Course, Enrollment, EnrollmentLine, FinalGrade, Period, Preselection, Section, Student

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def window_open(period, kind):
    if period.status != kind:
        return False
    now = timezone.now()
    start, end = (period.pre_start, period.pre_end) if kind == "pre" else (period.enroll_start, period.enroll_end)
    return (not start or start <= now) and (not end or now <= end)


def section_info(section):
    meetings = [
        {"day": m.day, "day_name": DAYS[m.day], "start": m.start.strftime("%H:%M"), "end": m.end.strftime("%H:%M")}
        for m in section.meetings.all()
    ]
    minutes = sum(
        (datetime.combine(timezone.localdate(), m.end) - datetime.combine(timezone.localdate(), m.start)).seconds // 60
        for m in section.meetings.all()
    )
    course = section.course
    occupied = getattr(section, "occupied", None)
    if occupied is None:
        occupied = section.enrollment_lines.count()
    return {
        "id": section.id,
        "course_id": course.id if course else None,
        "course_name": section.raw_name or (course.name if course else ""),
        "curricular_code": course.curricular_code if course else None,
        "official_code": section.official_code or None,
        "section": section.section_code,
        "teacher": section.teacher.name if section.teacher else "Por asignar",
        "teacher_id": section.teacher_id,
        "classroom": section.classroom or "Por asignar",
        "cycle": section.cycle,
        "capacity": section.capacity,
        "occupied": occupied,
        "available": max(0, section.capacity - occupied),
        "published": section.published,
        "review_required": course is None,
        "meetings": meetings,
        "scheduled_minutes": minutes,
        "theory_hours": course.theory_hours if course else None,
        "practice_hours": course.practice_hours if course else None,
    }


def course_info(course, passed=None, eligible_ids=None):
    return {
        "id": course.id,
        "plan_id": course.plan_id,
        "plan_name": course.plan.name,
        "code": course.curricular_code,
        "name": course.name,
        "semester": course.semester,
        "credits": course.credits,
        "theory_hours": course.theory_hours,
        "practice_hours": course.practice_hours,
        "elective_track": course.elective_track,
        "academic_data_verified": course.academic_data_verified,
        "prerequisites": [{"id": p.id, "code": p.curricular_code, "name": p.name} for p in course.prerequisites.all()],
        "passed": bool(passed is not None and course.id in passed),
        "eligible": bool(eligible_ids is not None and course.id in eligible_ids),
    }


def passed_course_ids(student):
    from .models import EnrollmentLine
    passed = set(FinalGrade.objects.filter(student=student, passed=True).values_list("course_id", flat=True))
    enrolled = set(EnrollmentLine.objects.filter(enrollment__student=student).values_list("section__course_id", flat=True))
    return passed | enrolled


def eligible_course_ids(student, passed=None):
    """Cursos que el alumno puede llevar: su ciclo actual y uno superior (máximo 2 ciclos en total), considerando aprobados o su primer curso pendiente."""
    passed = passed if passed is not None else passed_course_ids(student)
    courses = list(Course.objects.filter(plan=student.plan).prefetch_related("prerequisites").order_by("semester"))
    pending = [course for course in courses if course.pk not in passed]
    if not pending:
        return set()
    
    mandatory_pending = [course for course in pending if not course.elective_track]
    # Determinar el primer ciclo pendiente
    first_pending_cycle = mandatory_pending[0].semester if mandatory_pending and mandatory_pending[0].semester else (pending[0].semester or 1)

    if passed:
        passed_courses = [course for course in courses if course.pk in passed]
        passed_semesters = [c.semester for c in passed_courses if c.semester is not None]
        highest_passed_cycle = max(passed_semesters, default=0)
    else:
        highest_passed_cycle = 0
        
    # El ciclo actual es el mayor entre (último aprobado + 1) y el primer pendiente
    current_cycle = max(highest_passed_cycle + 1, first_pending_cycle)
    max_cycle = current_cycle + 1
    
    return {
        course.pk
        for course in pending
        if (course.semester is None or course.semester <= max_cycle) and all(prerequisite.pk in passed for prerequisite in course.prerequisites.all())
    }


def check_course(student, course, passed, eligible=None):
    if course.plan_id != student.plan_id:
        raise ValidationError(f"{course.name} no pertenece al plan del alumno.")
    if course.pk in passed:
        raise ValidationError(f"{course.name} ya está aprobado.")
    missing = [p.name for p in course.prerequisites.all() if p.pk not in passed]
    if missing:
        raise ValidationError(f"Faltan prerrequisitos para {course.name}: {', '.join(missing)}.")
    eligible = eligible if eligible is not None else eligible_course_ids(student, passed)
    if course.pk not in eligible:
        raise ValidationError(f"{course.name} todavía no corresponde al ciclo habilitado del alumno.")


def has_conflicts(sections):
    items = []
    for s in sections:
        for m in s.meetings.all():
            for other_section, other in items:
                if m.day == other.day and m.start < other.end and other.start < m.end:
                    return f"Cruce entre {s.raw_name} ({s.section_code}) y {other_section.raw_name} ({other_section.section_code}), {DAYS[m.day]}."
            items.append((s, m))
    return None


def require_id_list(body, field):
    ids = body.get(field)
    if (
        not isinstance(ids, list)
        or not ids
        or any(not isinstance(v, int) or isinstance(v, bool) for v in ids)
        or len(ids) != len(set(ids))
    ):
        raise ValidationError({field: "Envía una lista no vacía de identificadores numéricos sin duplicados."})
    return ids


def save_preselection(student, period, section_ids=None, course_ids=None):
    if not window_open(period, "pre"):
        raise ValidationError("La prematrícula no está abierta.")
    year = period.code[:4]
    annual_periods = Period.objects.filter(code__startswith=year)
    section_ids = section_ids or []
    course_ids = course_ids or []
    
    pre_objs = []
    passed = passed_course_ids(student)
    eligible = eligible_course_ids(student, passed)

    if section_ids:
        sections = list(
            Section.objects.select_related("course")
            .prefetch_related("course__prerequisites", "meetings")
            .filter(id__in=section_ids, period__in=annual_periods, published=True, course__isnull=False)
        )
        if len(sections) != len(section_ids):
            raise ValidationError("Una sección no está publicada, no existe o necesita revisión.")
        courses_in_sections = [s.course_id for s in sections]
        if len(set(courses_in_sections)) != len(courses_in_sections):
            raise ValidationError("Elige una sola sección por curso.")
        for s in sections:
            check_course(student, s.course, passed, eligible)
            pre_objs.append(Preselection(student=student, period=s.period, course=s.course, preferred_section=s))

    if course_ids:
        added_course_ids = {obj.course_id for obj in pre_objs}
        cids_to_add = [cid for cid in course_ids if cid not in added_course_ids]
        courses = list(Course.objects.filter(id__in=cids_to_add))
        for c in courses:
            check_course(student, c, passed, eligible)
            pre_objs.append(Preselection(student=student, period=period, course=c, preferred_section=None))

    if not pre_objs:
        raise ValidationError("Debes elegir al menos un curso o sección.")

    with transaction.atomic():
        Preselection.objects.filter(student=student, period__in=annual_periods).delete()
        Preselection.objects.bulk_create(pre_objs)
    return len(pre_objs)


def confirm_enrollment(student, period, section_ids):
    if not window_open(period, "enroll"):
        raise ValidationError("La matrícula no está abierta.")
    year = period.code[:4]
    annual_periods = Period.objects.filter(code__startswith=year)
    # PostgreSQL bloquea cada sección en orden estable durante el conteo y la inserción.
    with transaction.atomic():
        Student.objects.select_for_update().get(pk=student.pk)
        if Enrollment.objects.filter(student=student, period=period).exists():
            raise ValidationError("Ya existe una matrícula confirmada. Solicita una rectificación al administrador.")
        sections = list(
            Section.objects.select_for_update()
            .select_related("course")
            .prefetch_related("course__prerequisites", "meetings")
            .filter(id__in=section_ids, period__in=annual_periods, published=True, course__isnull=False)
            .order_by("id")
        )
        if len(sections) != len(section_ids):
            raise ValidationError("Una sección no está publicada, no existe o necesita revisión.")
        if len(set(s.course_id for s in sections)) != len(sections):
            raise ValidationError("Elige una sola sección por curso.")
        passed = passed_course_ids(student)
        eligible = eligible_course_ids(student, passed)
        total_credits = 0
        for s in sections:
            check_course(student, s.course, passed, eligible)
            if s.course.credits is None:
                raise ValidationError(f"{s.course.name} requiere configurar sus créditos.")
            total_credits += s.course.credits
            if s.enrollment_lines.count() >= s.capacity:
                raise ValidationError(f"Se agotaron las vacantes de {s.raw_name}, sección {s.section_code}.")
        if total_credits > period.max_credits:
            raise ValidationError(f"Excede el máximo de {period.max_credits} créditos ({total_credits} seleccionados).")
        conflict = has_conflicts(sections)
        if conflict:
            raise ValidationError(conflict)
        enrollment = Enrollment.objects.create(student=student, period=period)
        EnrollmentLine.objects.bulk_create(
            [
                EnrollmentLine(
                    enrollment=enrollment,
                    section=s,
                    course=s.course,
                    snapshot={
                        key: section_info(s)[key]
                        for key in ["course_name", "official_code", "section", "teacher", "classroom", "meetings"]
                    }
                    | {"credits": s.course.credits},
                )
                for s in sections
            ]
        )
        return enrollment


def demand_report(period):
    return list(
        Preselection.objects.filter(period=period)
        .values("course_id", "course__curricular_code", "course__name", "preferred_section__section_code")
        .annotate(students=Count("student_id", distinct=True))
        .order_by("course__name", "preferred_section__section_code")
    )
