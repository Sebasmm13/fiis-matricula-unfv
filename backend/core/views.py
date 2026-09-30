import json
from io import BytesIO

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .access import available_roles, identity, need_admin, need_student, need_teacher
from .models import (
    AccountSecurity,
    AuditLog,
    Course,
    Enrollment,
    EnrollmentLine,
    FinalGrade,
    Meeting,
    Period,
    Plan,
    Preselection,
    ProfilePhoto,
    Section,
    Student,
    Teacher,
)
from .pdf import enrollment_pdf, teacher_report_pdf
from .services import (
    confirm_enrollment,
    course_info,
    demand_report,
    eligible_course_ids,
    passed_course_ids,
    require_id_list,
    save_preselection,
    section_info,
    window_open,
)


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@csrf_protect
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    try:
        body = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({"detail": "JSON inválido"}, status=400)
    identifier = str(body.get("email") or body.get("username") or "").strip()
    username = identifier
    if "@" in identifier:
        matches = list(User.objects.filter(email__iexact=identifier).values_list("username", flat=True)[:2])
        username = matches[0] if len(matches) == 1 else ""
    user = authenticate(request, username=username, password=body.get("password", ""))
    if not user or not user.is_active or not available_roles(user):
        return JsonResponse({"detail": "Credenciales inválidas"}, status=400)
    login(request, user)
    roles = available_roles(user)
    if len(roles) == 1:
        request.session["active_role"] = roles[0]
    else:
        request.session.pop("active_role", None)
    return JsonResponse(identity(user, request.session.get("active_role")))


def validate_new_password(password, user=None):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise ValidationError({"password": list(exc.messages)})


@csrf_protect
def change_password(request):
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    body = json.loads(request.body or "{}")
    if not request.user.check_password(body.get("current_password", "")):
        return JsonResponse({"detail": "La contraseña actual no es correcta."}, status=400)
    password = body.get("new_password", "")
    try:
        validate_new_password(password, request.user)
    except ValidationError as exc:
        return JsonResponse({"detail": exc.detail}, status=400)
    request.user.set_password(password)
    request.user.save(update_fields=["password"])
    security, _ = AccountSecurity.objects.get_or_create(user=request.user)
    security.must_change_password = False
    security.activation_pending = False
    security.password_changed_at = timezone.now()
    security.save()
    update_session_auth_hash(request, request.user)
    audit(request.user, "cuenta.contrasena_cambiada", request.user.username)
    return JsonResponse(identity(request.user, request.session.get("active_role")))


@csrf_protect
def activate_student(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    body = json.loads(request.body or "{}")
    code = str(body.get("student_code", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    name = " ".join(str(body.get("full_name", "")).split())
    student = Student.objects.select_related("user").filter(student_code=code, user__email__iexact=email).first()
    security = getattr(student.user, "security", None) if student else None
    if not student or not security or not security.activation_pending or len(name) < 5:
        return JsonResponse({"detail": "Los datos no coinciden con una cuenta pendiente de activación."}, status=400)
    password = body.get("password", "")
    try:
        validate_new_password(password, student.user)
    except ValidationError as exc:
        return JsonResponse({"detail": exc.detail}, status=400)
    with transaction.atomic():
        student.full_name = name
        student.active = True
        student.save(update_fields=["full_name", "active"])
        student.user.set_password(password)
        student.user.is_active = True
        student.user.save(update_fields=["password", "is_active"])
        security.activation_pending = False
        security.must_change_password = False
        security.password_changed_at = timezone.now()
        security.save()
        audit(student.user, "cuenta.alumno_activada", student)
    return JsonResponse({"ok": True})


@csrf_protect
def password_reset_request(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    body = json.loads(request.body or "{}")
    user = User.objects.filter(email__iexact=str(body.get("email", "")).strip(), is_active=True).first()
    response = {"detail": "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña."}
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        code = f"{uid}:{token}"
        send_mail(
            "Recuperación de acceso FIIS",
            f"Utiliza este código en el portal FIIS para restablecer tu contraseña:\n\n{code}",
            None,
            [user.email],
        )
        audit(user, "cuenta.recuperacion_solicitada", user.username)
        from django.conf import settings

        if settings.DEBUG:
            response["reset_code"] = code
    return JsonResponse(response)


@csrf_protect
def password_reset_confirm(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    body = json.loads(request.body or "{}")
    try:
        uid, token = str(body.get("code", "")).split(":", 1)
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (ValueError, TypeError, User.DoesNotExist):
        user = None
    if not user or not default_token_generator.check_token(user, token):
        return JsonResponse({"detail": "El código es inválido o ya venció."}, status=400)
    password = body.get("password", "")
    try:
        validate_new_password(password, user)
    except ValidationError as exc:
        return JsonResponse({"detail": exc.detail}, status=400)
    user.set_password(password)
    user.save(update_fields=["password"])
    security, _ = AccountSecurity.objects.get_or_create(user=user)
    security.must_change_password = False
    security.password_changed_at = timezone.now()
    security.save()
    audit(user, "cuenta.contrasena_restablecida", user.username)
    return JsonResponse({"ok": True})


@csrf_protect
def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)
    logout(request)
    return JsonResponse({"ok": True})


class SelectRole(APIView):
    def post(self, request):
        role = request.data.get("role")
        if role not in available_roles(request.user):
            raise PermissionDenied("La cuenta no tiene ese perfil.")
        request.session["active_role"] = role
        return Response(identity(request.user, role))


class MyPhoto(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        photo = ProfilePhoto.objects.filter(user=request.user).first()
        if not photo:
            raise NotFound("No hay foto de perfil.")
        return HttpResponse(
            bytes(photo.image),
            content_type="image/jpeg",
            headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
        )

    def post(self, request):
        from PIL import Image, ImageOps, UnidentifiedImageError

        upload = request.FILES.get("photo")
        if not upload or upload.size > 2_000_000:
            raise ValidationError("Selecciona una imagen JPEG, PNG o WebP de hasta 2 MB.")
        try:
            with Image.open(upload) as source:
                if source.format not in ("JPEG", "PNG", "WEBP") or source.width * source.height > 16_000_000:
                    raise ValueError("Formato o tamaño de imagen no admitido.")
                image = ImageOps.exif_transpose(source)
                image.thumbnail((512, 512))
                if image.mode in ("RGBA", "LA", "P"):
                    image = image.convert("RGBA")
                    base = Image.new("RGB", image.size, "white")
                    base.paste(image, mask=image.getchannel("A"))
                    image = base
                else:
                    image = image.convert("RGB")
                output = BytesIO()
                image.save(output, format="JPEG", quality=82, optimize=True)
                content = output.getvalue()
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            raise ValidationError("La foto no es una imagen JPEG, PNG o WebP válida.") from exc
        if len(content) > 400_000:
            raise ValidationError("La foto procesada es demasiado grande.")
        ProfilePhoto.objects.update_or_create(user=request.user, defaults={"image": content})
        audit(request.user, "perfil.foto_actualizada", request.user.username)
        return Response({"ok": True})

    def delete(self, request):
        ProfilePhoto.objects.filter(user=request.user).delete()
        audit(request.user, "perfil.foto_eliminada", request.user.username)
        return Response({"ok": True})


def teacher_sections(teacher, period):
    sections = list(
        Section.objects.filter(teacher=teacher, period=period)
        .select_related("course", "period", "teacher")
        .prefetch_related("meetings")
        .annotate(occupied=Count("enrollment_lines"))
        .order_by("cycle", "raw_name", "section_code")
    )
    enrolled = (
        EnrollmentLine.objects.filter(section__in=sections)
        .select_related("enrollment__student", "section")
        .order_by("enrollment__student__full_name")
    )
    rosters = {s.pk: [] for s in sections}
    for line in enrolled:
        student = line.enrollment.student
        rosters[line.section_id].append({"code": student.student_code, "name": student.full_name})
    return [dict(section_info(s), students=rosters[s.pk]) for s in sections]


class TeacherSections(APIView):
    def get(self, request):
        teacher = need_teacher(request.user)
        code = request.query_params.get("period")
        period = Period.objects.filter(code=code).first() if code else current_period()
        if not period:
            raise NotFound("Período no encontrado.")
        response = Response({"period": period.code, "sections": teacher_sections(teacher, period)})
        response["Cache-Control"] = "private, no-store"
        return response


class TeacherReport(APIView):
    def get(self, request):
        teacher = need_teacher(request.user)
        code = request.query_params.get("period")
        period = Period.objects.filter(code=code).first() if code else current_period()
        if not period:
            raise NotFound("Período no encontrado.")
        sections = teacher_sections(teacher, period)
        section_id = request.query_params.get("section_id")
        if section_id:
            if not section_id.isdigit():
                raise ValidationError("Sección inválida.")
            sections = [s for s in sections if s["id"] == int(section_id)]
            if not sections:
                raise NotFound("Sección no asignada al docente.")
        filename = f"horarios_y_alumnos_{period.code}.pdf"
        response = HttpResponse(
            teacher_report_pdf(teacher.name, period.code, sections),
            content_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "private, no-store"},
        )
        return response


def current_period():
    period = Period.objects.filter(is_current=True).first()
    if not period:
        raise NotFound("No hay período activo configurado.")
    return period


def audit(user, action, obj, detail=None):
    AuditLog.objects.create(actor=user, action=action, target=str(obj)[:160], detail=detail or {})


class Me(APIView):
    def get(self, request):
        role = request.session.get("active_role")
        data = identity(request.user, role)
        period = Period.objects.filter(is_current=True).first()
        data["period"] = (
            {"id": period.pk, "code": period.code, "status": period.status, "max_credits": period.max_credits}
            if period
            else None
        )
        if data["role"] == "student":
            student = need_student(request.user)
            data["student_code"] = student.student_code
            data["plan"] = student.plan.name
            data["plan_active"] = student.plan.active
        return Response(data)



CONVALIDATION_MAP = {
    "2C0187": "02", "2A0124": "03", "380103": "07", "380165": "15",
    "5B0110": "19", "3A0014": "22", "3B0166": "23", "380170": "30",
    "8E0035": "16", "880109": "24", "8E0036": "25", "880116": "08",
    "880073": "14", "600037": "21", "780192": "26", "600006": "28",
    "8F0123": "29", "780184": "32", "SA0063": "33", "780197": "34",
    "8F0127": "35", "8E0003": "36", "7A0472": "39", "880068": "40"
}

class ConvalidationView(APIView):
    def get(self, request):
        student = need_student(request.user)
        period = Period.objects.filter(is_current=True).first()
        if not period or not period.convalidation_active:
            return Response({"active": False})
            
        if student.plan.name.startswith("Ingenier"):
            return Response({"active": True, "done": True})

        grades = FinalGrade.objects.filter(student=student, passed=True).select_related('course')
        
        matches, unmatched = [], []
        plan_2019 = Plan.objects.filter(name__icontains="adjunta").first()
        if not plan_2019: return Response({"error": "Plan 2019 no encontrado"}, status=500)
            
        courses_2019 = {c.curricular_code: c for c in Course.objects.filter(plan=plan_2019)}

        for fg in grades:
            code_10 = fg.course.curricular_code
            if code_10 in CONVALIDATION_MAP:
                code_19 = CONVALIDATION_MAP[code_10]
                if code_19 in courses_2019:
                    c19 = courses_2019[code_19]
                    matches.append({
                        "old_code": code_10, "old_name": fg.course.name, "old_grade": fg.score,
                        "new_code": c19.curricular_code, "new_name": c19.name
                    })
                else: unmatched.append({"old_code": code_10, "old_name": fg.course.name, "old_grade": fg.score})
            else: unmatched.append({"old_code": code_10, "old_name": fg.course.name, "old_grade": fg.score})
                
        return Response({"active": True, "done": False, "matches": matches, "unmatched": unmatched})

    def post(self, request):
        student = need_student(request.user)
        period = Period.objects.filter(is_current=True).first()
        if not period or not period.convalidation_active:
            return Response({"error": "Convalidation not active"}, status=400)
            
        if student.plan.name.startswith("Ingenier"):
            return Response({"error": "Already migrated"}, status=400)

        with transaction.atomic():
            plan_2019 = Plan.objects.filter(name__icontains="adjunta").first()
            courses_2019 = {c.curricular_code: c for c in Course.objects.filter(plan=plan_2019)}
            
            grades = FinalGrade.objects.filter(student=student, passed=True).select_related('course')
            for fg in grades:
                code_10 = fg.course.curricular_code
                if code_10 in CONVALIDATION_MAP:
                    code_19 = CONVALIDATION_MAP[code_10]
                    if code_19 in courses_2019:
                        c19 = courses_2019[code_19]
                        FinalGrade.objects.update_or_create(
                            student=student, course=c19, period=fg.period,
                            defaults={"score": fg.score, "passed": True}
                        )
            
            student.plan = plan_2019
            student.save()
            audit(request.user, "Convalidation Done", student, detail={"plan": plan_2019.name})

        return Response({"success": True})

class Catalog(APIView):

    def get(self, request):
        student = need_student(request.user)
        period = current_period()
        year = period.code[:4]
        annual_periods = Period.objects.filter(code__startswith=year)
        passed = passed_course_ids(student)
        eligible = eligible_course_ids(student, passed)
        sections = (
            Section.objects.filter(period__in=annual_periods, published=True, course_id__in=eligible)
            .select_related("course")
            .prefetch_related("meetings", "course__prerequisites")
            .annotate(occupied=Count("enrollment_lines"))
            .order_by("course__semester", "course__name", "section_code")
        )
        return Response(
            {
                "period": {"code": period.code, "status": period.status, "max_credits": period.max_credits},
                "courses": [
                    course_info(c, passed)
                    for c in Course.objects.filter(plan=student.plan)
                    .select_related("plan")
                    .prefetch_related("prerequisites")
                    .order_by("semester", "curricular_code")
                ],
                "sections": [section_info(s) for s in sections],
            }
        )


class PreselectionView(APIView):
    def get(self, request):
        student = need_student(request.user)
        period = current_period()
        year = period.code[:4]
        annual_periods = Period.objects.filter(code__startswith=year)
        rows = Preselection.objects.filter(student=student, period__in=annual_periods).select_related("course", "preferred_section")
        return Response(
            [
                {"course_id": row.course_id, "course_name": row.course.name, "section_id": row.preferred_section_id}
                for row in rows
            ]
        )

    def post(self, request):
        student = need_student(request.user)
        period = current_period()
        section_ids = request.data.get("section_ids") or []
        course_ids = request.data.get("course_ids") or []
        count = save_preselection(student, period, section_ids=section_ids, course_ids=course_ids)
        audit(request.user, "prematricula.guardada", student, {"period": period.code, "courses": count})
        return Response({"saved": count, "message": "Preferencias guardadas. No ocupan vacantes."})

    def delete(self, request):
        student = need_student(request.user)
        period = current_period()
        year = period.code[:4]
        annual_periods = Period.objects.filter(code__startswith=year)
        if not window_open(period, "pre"):
            raise ValidationError("La prematrícula no está abierta.")
        Preselection.objects.filter(student=student, period__in=annual_periods).delete()
        audit(request.user, "prematricula.borrada", student, {"period": period.code})
        return Response({"ok": True})


class EnrollmentView(APIView):
    def get(self, request):
        student = need_student(request.user)
        results = []
        for enrollment in (
            Enrollment.objects.filter(student=student)
            .select_related("period")
            .prefetch_related("lines__section__meetings", "lines__course")
            .order_by("-confirmed_at")
        ):
            results.append(
                {
                    "id": enrollment.pk,
                    "period": enrollment.period.code,
                    "confirmed_at": enrollment.confirmed_at,
                    "sections": [section_info(line.section) for line in enrollment.lines.all()],
                }
            )
        return Response(results)

    def post(self, request):
        student = need_student(request.user)
        period = current_period()
        ids = require_id_list(request.data, "section_ids")
        enrollment = confirm_enrollment(student, period, ids)
        audit(request.user, "matricula.confirmada", enrollment, {"section_ids": ids})
        return Response(
            {"id": enrollment.pk, "message": "Matrícula confirmada. Puedes descargar la constancia."}, status=201
        )


class Receipt(APIView):
    def get(self, request, enrollment_id):
        student = need_student(request.user)
        enrollment = (
            Enrollment.objects.filter(pk=enrollment_id, student=student).select_related("student", "period").first()
        )
        if not enrollment:
            raise NotFound("Constancia no encontrada.")
        return HttpResponse(
            enrollment_pdf(enrollment),
            content_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="matricula_{enrollment.period.code}_{student.student_code}.pdf"',
                "Cache-Control": "private, no-store",
            },
        )


class Grades(APIView):
    def get(self, request):
        student = need_student(request.user)
        rows = (
            FinalGrade.objects.filter(student=student)
            .select_related("course", "period")
            .order_by("period__code", "course__name")
        )
        return Response(
            [
                {
                    "course_id": g.course_id,
                    "course": g.course.name,
                    "code": g.course.curricular_code,
                    "period": g.period.code,
                    "score": float(g.score),
                    "passed": g.passed,
                    "credits": g.course.credits,
                    "semester": g.course.semester,
                }
                for g in rows
            ]
        )


class AdminData(APIView):
    def get(self, request):
        need_admin(request.user)
        periods = list(
            Period.objects.order_by("-code").values(
                "id",
                "code",
                "status",
                "max_credits",
                "is_current",
                "convalidation_active",
                "pre_start",
                "pre_end",
                "enroll_start",
                "enroll_end",
            )
        )
        courses = [
            course_info(c)
            for c in Course.objects.select_related("plan")
            .prefetch_related("prerequisites")
            .order_by("semester", "name")
        ]
        sections = [
            dict(section_info(s), period=s.period.code)
            for s in Section.objects.select_related("period", "course")
            .prefetch_related("meetings")
            .annotate(occupied=Count("enrollment_lines"))
            .order_by("-period__code", "cycle", "raw_name", "section_code")
        ]
        students = [
            {
                "id": s.id,
                "student_code": s.student_code,
                "full_name": s.full_name,
                "plan__name": s.plan.name,
                "active": s.active and s.user.is_active,
                "email": s.user.email,
                "activation_pending": getattr(getattr(s.user, "security", None), "activation_pending", False),
            }
            for s in Student.objects.select_related("plan", "user", "user__security")
        ]
        teachers = [
            {
                "id": t.id,
                "name": t.name,
                "active": t.active and (t.user.is_active if t.user_id else True),
                "username": t.user.username if t.user_id else None,
                "email": t.user.email if t.user_id else None,
            }
            for t in Teacher.objects.select_related("user").order_by("name")
        ]
        return Response(
            {
                "periods": periods,
                "plans": list(Plan.objects.values("id", "name", "active")),
                "courses": courses,
                "sections": sections,
                "students": students,
                "teachers": teachers,
            }
        )


def int_value(value, name, min_value=0):
    try:
        result = int(value)
        if result < min_value:
            raise ValueError()
        return result
    except (ValueError, TypeError):
        raise ValidationError({name: "Debe ser un número entero válido."})


class AdminPeriod(APIView):
    def post(self, request):
        need_admin(request.user)
        code = str(request.data.get("code", "")).strip()
        if not code or len(code) > 20:
            raise ValidationError("Código de período obligatorio (máximo 20).")
        if Period.objects.filter(code=code).exists():
            raise ValidationError("El período ya existe.")
        period = Period.objects.create(
            code=code, max_credits=int_value(request.data.get("max_credits", 24), "max_credits", 1)
        )
        audit(request.user, "periodo.creado", period)
        return Response({"id": period.id}, status=201)

    def patch(self, request, pk):
        need_admin(request.user)
        obj = Period.objects.filter(pk=pk).first()
        if not obj:
            raise NotFound()
        if "status" in request.data:
            if request.data["status"] not in dict(Period._meta.get_field("status").choices):
                raise ValidationError("Estado inválido.")
            obj.status = request.data["status"]
        if "max_credits" in request.data:
            obj.max_credits = int_value(request.data["max_credits"], "max_credits", 1)
        for field in ["pre_start", "pre_end", "enroll_start", "enroll_end"]:
            if field in request.data:
                from django.utils.dateparse import parse_datetime

                value = request.data[field]
                parsed = parse_datetime(value) if value else None
                if value and not parsed:
                    raise ValidationError({field: "Fecha inválida. Usa ISO 8601."})
                if parsed and parsed.tzinfo is None:
                    from django.utils import timezone

                    parsed = timezone.make_aware(parsed)
                setattr(obj, field, parsed)
        if request.data.get("is_current") is True:
            Period.objects.filter(is_current=True).exclude(pk=pk).update(is_current=False)
            obj.is_current = True
        if "convalidation_active" in request.data:
            obj.convalidation_active = bool(request.data["convalidation_active"])
        obj.save()
        audit(request.user, "periodo.actualizado", obj)
        return Response({"ok": True})


class AdminPlan(APIView):
    def post(self, request):
        need_admin(request.user)
        name = str(request.data.get("name", "")).strip()
        source = Plan.objects.filter(pk=request.data.get("clone_from")).first()
        if not source or len(name) < 5 or Plan.objects.filter(name=name).exists():
            raise ValidationError("Indica un nombre nuevo y el plan que deseas copiar.")
        with transaction.atomic():
            plan = Plan.objects.create(name=name, source=f"Versión derivada de {source.name}")
            originals = list(Course.objects.filter(plan=source).prefetch_related("prerequisites"))
            copy = {}
            for old in originals:
                copy[old.pk] = Course.objects.create(
                    plan=plan,
                    curricular_code=old.curricular_code,
                    name=old.name,
                    semester=old.semester,
                    credits=old.credits,
                    theory_hours=old.theory_hours,
                    practice_hours=old.practice_hours,
                    elective_track=old.elective_track,
                )
            for old in originals:
                copy[old.pk].prerequisites.set([copy[p.pk] for p in old.prerequisites.all() if p.pk in copy])
        audit(request.user, "plan.versionado", plan, {"original": source.pk})
        return Response({"id": plan.pk, "courses_copied": len(copy)}, status=201)


class AdminCourse(APIView):
    def post(self, request):
        need_admin(request.user)
        plan = Plan.objects.filter(pk=request.data.get("plan_id")).first()
        if not plan:
            raise ValidationError("Plan inválido.")
        code = str(request.data.get("curricular_code", "")).strip()
        name = str(request.data.get("name", "")).strip()
        if not code or not name:
            raise ValidationError("Indica código y nombre.")
        if Course.objects.filter(plan=plan, curricular_code=code).exists():
            raise ValidationError("Código repetido en el plan.")
        course = Course.objects.create(
            plan=plan,
            curricular_code=code,
            name=name,
            semester=int_value(request.data.get("semester"), "semester", 1),
            credits=int_value(request.data.get("credits"), "credits", 1),
        )
        audit(request.user, "curso.creado", course)
        return Response({"id": course.pk}, status=201)

    def patch(self, request, pk):
        need_admin(request.user)
        obj = Course.objects.filter(pk=pk).first()
        if not obj:
            raise NotFound()
        for field in ["name", "curricular_code", "elective_track"]:
            if field in request.data:
                setattr(obj, field, str(request.data[field]).strip())
        for field in ["semester", "credits", "theory_hours", "practice_hours"]:
            if field in request.data:
                setattr(
                    obj,
                    field,
                    None
                    if request.data[field] is None and field != "semester"
                    else int_value(request.data[field], field, 1 if field in ["semester", "credits"] else 0),
                )
        if "prerequisite_ids" in request.data:
            ids = request.data["prerequisite_ids"]
            if (
                not isinstance(ids, list)
                or any(not isinstance(v, int) for v in ids)
                or len(ids) != len(set(ids))
                or obj.pk in ids
            ):
                raise ValidationError("Prerrequisitos inválidos.")
            prerequisites = list(Course.objects.filter(id__in=ids, plan=obj.plan))
            if len(prerequisites) != len(ids) or any(p.semester >= obj.semester for p in prerequisites):
                raise ValidationError("Los prerrequisitos deben pertenecer al plan y a ciclos anteriores.")
        if "academic_data_verified" in request.data:
            verified = request.data["academic_data_verified"]
            if not isinstance(verified, bool):
                raise ValidationError("La verificación debe ser booleana.")
            effective = {
                "credits": request.data.get("credits", obj.credits),
                "theory_hours": request.data.get("theory_hours", obj.theory_hours),
                "practice_hours": request.data.get("practice_hours", obj.practice_hours),
            }
            if verified and any(value is None for value in effective.values()):
                raise ValidationError("Completa créditos, horas teóricas y prácticas antes de verificar el curso.")
            obj.academic_data_verified = verified
        obj.save()
        if "prerequisite_ids" in request.data:
            obj.prerequisites.set(prerequisites)
        audit(request.user, "curso.actualizado", obj, {"fields": list(request.data.keys())})
        return Response({"ok": True})


class AdminSection(APIView):
    def post(self, request):
        need_admin(request.user)
        period = Period.objects.filter(pk=request.data.get("period_id")).first()
        course = Course.objects.filter(pk=request.data.get("course_id")).first()
        if not period or not course:
            raise ValidationError("Período o curso inválido.")
        meetings = request.data.get("meetings", [])
        if not isinstance(meetings, list) or not meetings:
            raise ValidationError("Se requiere un horario.")
        code = str(request.data.get("section", "")).strip()
        if not code:
            raise ValidationError("Se requiere una sección.")
        with transaction.atomic():
            Period.objects.select_for_update().get(pk=period.pk)
            section = Section.objects.create(
                period=period,
                course=course,
                raw_name=course.name,
                cycle=str(course.semester),
                section_code=code,
                official_code=str(request.data.get("official_code", "")).strip(),
                teacher=Teacher.objects.filter(pk=request.data.get("teacher_id")).first(),
                classroom=str(request.data.get("classroom", "")).strip(),
                capacity=int_value(request.data.get("capacity", 35), "capacity", 1),
                published=False,
            )
            save_meetings(section, meetings)
        audit(request.user, "seccion.creada", section)
        return Response({"id": section.pk}, status=201)

    @transaction.atomic
    def patch(self, request, pk):
        need_admin(request.user)
        section = Section.objects.filter(pk=pk).first()
        if not section:
            raise NotFound()
        Period.objects.select_for_update().get(pk=section.period_id)
        if "course_id" in request.data:
            course = Course.objects.filter(pk=request.data["course_id"]).first()
            if not course:
                raise ValidationError("Curso inválido.")
            if section.enrollment_lines.exists():
                raise ValidationError("No se puede reasignar una sección con matrículas.")
            section.course = course
        if "teacher_id" in request.data:
            teacher = Teacher.objects.filter(pk=request.data["teacher_id"]).first()
            if not teacher:
                raise ValidationError("Docente inválido.")
            section.teacher = teacher
        for field in ["classroom", "official_code"]:
            if field in request.data:
                setattr(section, field, str(request.data[field]).strip())
        if "capacity" in request.data:
            n = int_value(request.data["capacity"], "capacity", 1)
            if n < section.enrollment_lines.count():
                raise ValidationError("Capacidad inferior a las matrículas confirmadas.")
            section.capacity = n
        if "published" in request.data:
            if not isinstance(request.data["published"], bool):
                raise ValidationError("Publicado debe ser booleano.")
            if request.data["published"] and (
                not section.course_id
                or not section.course.credits
                or not section.course.academic_data_verified
                or not section.meetings.exists()
            ):
                raise ValidationError("Primero vincula el curso, verifica sus datos académicos y configura el horario.")
            section.published = request.data["published"]
        if "meetings" in request.data:
            if section.enrollment_lines.exists():
                raise ValidationError("No se puede cambiar el horario con matrículas confirmadas.")
            section.meetings.all().delete()
            save_meetings(section, request.data["meetings"])
        elif "teacher_id" in request.data or "classroom" in request.data:
            for meeting in section.meetings.all():
                check_meeting_resources(section, meeting)
        section.save()
        audit(request.user, "seccion.actualizada", section, {"fields": list(request.data.keys())})
        return Response({"ok": True})


def save_meetings(section, meetings):
    from django.utils.dateparse import parse_time

    if not isinstance(meetings, list) or not meetings:
        raise ValidationError("Proporciona sesiones.")
    rows = []
    for m in meetings:
        day = int_value(m.get("day"), "day")
        a, b = parse_time(m.get("start", "")), parse_time(m.get("end", ""))
        if day > 6 or not a or not b or a >= b:
            raise ValidationError("Día u horas de sesión inválidos.")
        rows.append(Meeting(section=section, day=day, start=a, end=b))
    for i, m in enumerate(rows):
        if any(m.day == n.day and m.start < n.end and n.start < m.end for n in rows[:i]):
            raise ValidationError("La sección tiene sesiones superpuestas.")
        check_meeting_resources(section, m)
    Meeting.objects.bulk_create(rows)


def check_meeting_resources(section, meeting):
    overlaps = (
        Meeting.objects.filter(
            section__period_id=section.period_id, day=meeting.day, start__lt=meeting.end, end__gt=meeting.start
        )
        .exclude(section_id=section.pk)
        .select_related("section")
    )
    for existing in overlaps:
        other = existing.section
        if (
            other.cycle == section.cycle
            and other.section_code == section.section_code
            or section.teacher_id
            and other.teacher_id == section.teacher_id
            or section.classroom
            and other.classroom.casefold() == section.classroom.casefold()
        ):
            raise ValidationError(
                f"Cruce de horario con {other.raw_name}, sección {other.section_code}: mismo grupo, docente o salón."
            )


class AdminTeacher(APIView):
    def post(self, request):
        need_admin(request.user)
        name = str(request.data.get("name", "")).strip().upper()
        if len(name) < 5:
            raise ValidationError("Indica el nombre completo del docente.")
        email = str(request.data.get("email") or request.data.get("username") or "").strip().lower()
        password = request.data.get("password", "")
        if not email.endswith("@unfv.edu.pe"):
            raise ValidationError("Indica un correo institucional válido.")
        existing_user = User.objects.filter(email__iexact=email).first()
        if not existing_user and len(password) < 12:
            raise ValidationError("Las cuentas nuevas requieren una contraseña de al menos 12 caracteres.")
        with transaction.atomic():
            teacher, created = Teacher.objects.get_or_create(name=name)
            if teacher.user_id:
                raise ValidationError("El docente ya tiene una cuenta vinculada.")
            user = existing_user or User.objects.create_user(username=email, email=email, password=password)
            if hasattr(user, "teacher"):
                raise ValidationError("El correo ya está vinculado a otro docente.")
            teacher.user = user
            teacher.save(update_fields=["user"])
            if not existing_user:
                AccountSecurity.objects.update_or_create(user=user, defaults={"must_change_password": True})
        audit(request.user, "docente.creado" if created else "docente.acceso_creado", teacher)
        return Response({"id": teacher.pk, "email": email}, status=201)

    def patch(self, request, pk):
        need_admin(request.user)
        teacher = Teacher.objects.select_related("user").filter(pk=pk).first()
        if not teacher:
            raise NotFound()
        if "name" in request.data:
            name = " ".join(str(request.data["name"]).split()).upper()
            if len(name) < 5 or Teacher.objects.exclude(pk=pk).filter(name=name).exists():
                raise ValidationError("Nombre docente inválido o repetido.")
            teacher.name = name
        if "active" in request.data:
            if not isinstance(request.data["active"], bool):
                raise ValidationError("Activo debe ser booleano.")
            teacher.active = request.data["active"]
            if teacher.user_id:
                teacher.user.is_active = teacher.active
                teacher.user.save(update_fields=["is_active"])
        if "temporary_password" in request.data:
            if not teacher.user_id:
                raise ValidationError("El docente todavía no tiene una cuenta.")
            password = request.data["temporary_password"]
            validate_new_password(password, teacher.user)
            teacher.user.set_password(password)
            teacher.user.save(update_fields=["password"])
            AccountSecurity.objects.update_or_create(user=teacher.user, defaults={"must_change_password": True})
        teacher.save()
        audit(request.user, "docente.cuenta_actualizada", teacher, {"fields": list(request.data.keys())})
        return Response({"ok": True})


class AdminStudent(APIView):
    def post(self, request):
        need_admin(request.user)
        plan = Plan.objects.filter(pk=request.data.get("plan_id")).first()
        if not plan:
            raise ValidationError("Plan inválido.")
        code = str(request.data.get("student_code", "")).strip()
        name = str(request.data.get("full_name", "")).strip()
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        if not code or not name or not email.endswith("@unfv.edu.pe"):
            raise ValidationError("Se requieren código, nombre y correo institucional.")
        if password:
            validate_new_password(password)
        if (
            User.objects.filter(username=code).exists()
            or User.objects.filter(email__iexact=email).exists()
            or Student.objects.filter(student_code=code).exists()
        ):
            raise ValidationError("El código o correo ya está registrado.")
        with transaction.atomic():
            user = User.objects.create_user(username=code, email=email, password=password or None)
            pending = not bool(password)
            user.is_active = not pending
            user.save(update_fields=["is_active"])
            student = Student.objects.create(
                user=user, student_code=code, full_name=name, plan=plan, active=not pending
            )
            AccountSecurity.objects.create(user=user, must_change_password=bool(password), activation_pending=pending)
        audit(request.user, "alumno.creado", student)
        return Response({"id": student.pk}, status=201)

    def patch(self, request, pk):
        need_admin(request.user)
        student = Student.objects.select_related("user", "plan").filter(pk=pk).first()
        if not student:
            raise NotFound()
        if "full_name" in request.data:
            name = " ".join(str(request.data["full_name"]).split())
            if len(name) < 5:
                raise ValidationError("Nombre inválido.")
            student.full_name = name
        if "email" in request.data:
            email = str(request.data["email"]).strip().lower()
            if (
                not email.endswith("@unfv.edu.pe")
                or User.objects.exclude(pk=student.user_id).filter(email__iexact=email).exists()
            ):
                raise ValidationError("Correo institucional inválido o repetido.")
            student.user.email = email
        if "active" in request.data:
            if not isinstance(request.data["active"], bool):
                raise ValidationError("Activo debe ser booleano.")
            student.active = request.data["active"]
            student.user.is_active = request.data["active"]
        if "temporary_password" in request.data:
            password = request.data["temporary_password"]
            validate_new_password(password, student.user)
            student.user.set_password(password)
            AccountSecurity.objects.update_or_create(
                user=student.user, defaults={"must_change_password": True, "activation_pending": False}
            )
            student.active = True
            student.user.is_active = True
        if request.data.get("enable_activation") is True:
            student.user.set_unusable_password()
            student.user.is_active = False
            student.active = False
            AccountSecurity.objects.update_or_create(
                user=student.user,
                defaults={"must_change_password": False, "activation_pending": True},
            )
        student.user.save()
        student.save()
        audit(request.user, "alumno.cuenta_actualizada", student, {"fields": list(request.data.keys())})
        return Response({"ok": True})


class AdminGrade(APIView):
    def post(self, request):
        need_admin(request.user)
        student = Student.objects.filter(pk=request.data.get("student_id")).first()
        course = Course.objects.filter(pk=request.data.get("course_id")).first()
        period = Period.objects.filter(pk=request.data.get("period_id")).first()
        if not student or not course or not period or student.plan_id != course.plan_id:
            raise ValidationError("Alumno, curso o perodo invlido.")
        
        missing_reqs = []
        for req in course.prerequisites.all():
            if not FinalGrade.objects.filter(student=student, course=req, passed=True).exists():
                missing_reqs.append(req.curricular_code)
        
        if missing_reqs:
            raise ValidationError(f"No se puede asignar nota. El alumno no ha aprobado los prerrequisitos: {', '.join(missing_reqs)}")
        try:
            from decimal import Decimal

            score = Decimal(str(request.data["score"]))
            if score < 0 or score > 20:
                raise ValueError()
        except (KeyError, ValueError, TypeError, ArithmeticError):
            raise ValidationError("La nota debe estar entre 0 y 20.")
        # Criterio de aprobación configurable institucionalmente antes del uso real.
        passed = score >= Decimal("11")
        obj, created = FinalGrade.objects.update_or_create(
            student=student, course=course, period=period, defaults={"score": score, "passed": passed}
        )
        audit(
            request.user,
            "nota.registrada" if created else "nota.rectificada",
            student,
            {"course": course.curricular_code, "period": period.code, "score": str(score)},
        )
        return Response({"id": obj.pk, "passed": passed})


class AdminDemand(APIView):
    def get(self, request):
        need_admin(request.user)
        period = (
            Period.objects.filter(pk=request.query_params.get("period_id")).first()
            if request.query_params.get("period_id")
            else current_period()
        )
        if not period:
            raise NotFound()
        rows = demand_report(period)
        totals = {}
        for row in rows:
            key = row["course_id"]
            if key not in totals:
                totals[key] = {
                    "course_id": key,
                    "code": row["course__curricular_code"],
                    "course": row["course__name"],
                    "students": 0,
                    "suggested_sections": 0,
                    "preferences": [],
                }
            totals[key]["students"] += row["students"]
            totals[key]["preferences"].append(
                {"section": row["preferred_section__section_code"], "students": row["students"]}
            )
        size = int_value(request.query_params.get("capacity", 35), "capacity", 1)
        for item in totals.values():
            item["suggested_sections"] = (item["students"] + size - 1) // size
        total_students = Preselection.objects.filter(period=period).values("student_id").distinct().count()
        course_summary = ", ".join(f"{item['course']}: {item['students']}" for item in totals.values())
        notification = (
            f"{total_students} estudiante(s) registraron su prematrícula. Demanda por curso: {course_summary}."
            if total_students
            else "Todavía no se registraron preferencias de prematrícula."
        )
        return Response(
            {
                "period": period.code,
                "capacity_assumption": size,
                "total_students": total_students,
                "notification": notification,
                "courses": list(totals.values()),
            }
        )


class AdminAudit(APIView):
    def get(self, request):
        need_admin(request.user)
        return Response(
            [
                {
                    "actor": r.actor.username if r.actor else "desconocido",
                    "action": r.action,
                    "target": r.target,
                    "detail": r.detail,
                    "created_at": r.created_at,
                }
                for r in AuditLog.objects.select_related("actor").order_by("-created_at")[:100]
            ]
        )
