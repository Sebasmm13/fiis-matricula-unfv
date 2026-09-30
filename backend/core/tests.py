from datetime import time
from decimal import Decimal
from io import BytesIO, StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from pypdf import PdfReader
from rest_framework.exceptions import ValidationError

from .models import (
    AccountSecurity,
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
from .pdf import enrollment_pdf
from .services import confirm_enrollment, demand_report, save_preselection


class EnrollmentRulesTests(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name="Plan de pruebas")
        self.period = Period.objects.create(code="T-1", status="pre", is_current=True, max_credits=20)
        self.user = User.objects.create_user("test.alumno", password="clave-segura-pruebas")
        self.student = Student.objects.create(
            user=self.user, student_code="T001", full_name="Estudiante de prueba", plan=self.plan
        )
        self.pre = Course.objects.create(
            plan=self.plan, curricular_code="01", name="Introducción", semester=1, credits=3
        )
        self.c1 = Course.objects.create(
            plan=self.plan, curricular_code="02", name="Programación", semester=2, credits=4
        )
        self.c1.prerequisites.add(self.pre)
        self.c2 = Course.objects.create(
            plan=self.plan, curricular_code="03", name="Base de datos", semester=2, credits=4
        )
        self.a = self.section(self.c1, "A", time(8), time(9, 40), 1)
        self.b = self.section(self.c1, "B", time(10), time(11, 40), 2)
        self.c = self.section(self.c2, "A", time(8, 30), time(10), 2)

    def section(self, course, code, start, end, capacity):
        s = Section.objects.create(
            period=self.period,
            course=course,
            section_code=code,
            raw_name=course.name,
            official_code="100001",
            classroom="B-101",
            capacity=capacity,
            published=True,
        )
        Meeting.objects.create(section=s, day=0, start=start, end=end)
        return s

    def pass_prerequisite(self):
        p = Period.objects.create(code="T-0", status="closed")
        FinalGrade.objects.create(student=self.student, course=self.pre, period=p, score=Decimal("15"), passed=True)

    def test_preselection_counts_demand_but_does_not_use_seat(self):
        self.pass_prerequisite()
        self.assertEqual(save_preselection(self.student, self.period, [self.a.id]), 1)
        self.assertEqual(Preselection.objects.count(), 1)
        self.assertEqual(self.a.enrollment_lines.count(), 0)
        self.assertEqual(demand_report(self.period)[0]["students"], 1)
        self.assertEqual(save_preselection(self.student, self.period, [self.b.id]), 1)
        self.assertEqual(Preselection.objects.count(), 1)

    def test_prerequisite_conflict_capacity_and_duplicate(self):
        self.period.status = "enroll"
        self.period.save()
        with self.assertRaises(ValidationError):
            confirm_enrollment(self.student, self.period, [self.a.id])
        self.pass_prerequisite()
        with self.assertRaises(ValidationError):
            confirm_enrollment(self.student, self.period, [self.a.id, self.c.id])
        self.assertEqual(EnrollmentLine.objects.count(), 0)
        enrollment = confirm_enrollment(self.student, self.period, [self.a.id])
        self.assertEqual(enrollment.lines.count(), 1)
        with self.assertRaises(ValidationError):
            confirm_enrollment(self.student, self.period, [self.b.id])
        another_user = User.objects.create_user("otro")
        another = Student.objects.create(user=another_user, student_code="T002", full_name="Otro", plan=self.plan)
        FinalGrade.objects.create(
            student=another, course=self.pre, period=Period.objects.get(code="T-0"), score=Decimal("15"), passed=True
        )
        with self.assertRaises(ValidationError):
            confirm_enrollment(another, self.period, [self.a.id])
        self.assertEqual(self.a.enrollment_lines.count(), 1)

    def test_pdf_contains_student_course_room_and_code(self):
        self.pass_prerequisite()
        self.period.status = "enroll"
        self.period.save()
        obj = confirm_enrollment(self.student, self.period, [self.a.id])
        payload = enrollment_pdf(obj)
        self.assertTrue(payload.startswith(b"%PDF"))
        from pypdf import PdfReader

        page = PdfReader(BytesIO(payload)).pages[0].extract_text()
        for value in ["T001", "Programación", "B-101", "100001", "Sección"]:
            self.assertIn(value, page)
        self.c1.name = "Nombre cambiado"
        self.c1.save()
        self.a.classroom = "B-999"
        self.a.save()
        original = PdfReader(BytesIO(enrollment_pdf(obj))).pages[0].extract_text()
        self.assertIn("Programación", original)
        self.assertIn("B-101", original)
        self.assertNotIn("Nombre cambiado", original)

    def test_student_cannot_read_another_receipt(self):
        self.pass_prerequisite()
        self.period.status = "enroll"
        self.period.save()
        obj = confirm_enrollment(self.student, self.period, [self.a.id])
        other_user = User.objects.create_user("outsider")
        Student.objects.create(user=other_user, student_code="T999", full_name="Persona externa", plan=self.plan)
        self.client.force_login(other_user)
        self.assertEqual(self.client.get(f"/api/enrollments/{obj.pk}/pdf/").status_code, 404)


class SeedTests(TestCase):
    def test_new_plan_preserves_course_prerequisites(self):
        call_command("seed_fiis", "--demo-users", stdout=StringIO())
        self.assertEqual(User.objects.get(username="demo").teacher.active, True)
        call_command("seed_fiis", "--demo-users", stdout=StringIO())
        self.assertEqual(Teacher.objects.filter(user__username="demo").count(), 1)
        student_codes = ["2024023935", "2024023953", "2024024193", "2024035007", "2024024406"]
        self.assertEqual(Student.objects.filter(student_code__in=student_codes).count(), 5)
        self.assertTrue(User.objects.get(username="2024023935").check_password("2024023935"))
        teacher_credentials = {
            "rojas@unfv.edu.pe": "Rojas",
            "cano@unfv.edu.pe": "Cano",
            "peterlik@unfv.edu.pe": "Peterlik",
            "salazar@unfv.edu.pe": "Salazar",
        }
        for email, password in teacher_credentials.items():
            user = User.objects.get(email=email)
            self.assertTrue(user.check_password(password))
            self.assertTrue(hasattr(user, "teacher"))
        self.assertTrue(User.objects.get(email="salazar@unfv.edu.pe").is_staff)
        original = Plan.objects.get(name="Ingeniería de Sistemas - malla adjunta")
        self.client.force_login(User.objects.get(username="demo"))
        import json

        response = self.client.post(
            "/api/admin/plans/",
            data=json.dumps({"name": "Plan académico copia 2027", "clone_from": original.pk}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        copied = Plan.objects.get(pk=response.json()["id"])
        self.assertEqual(copied.courses.count(), 85)
        self.assertEqual(
            list(copied.courses.get(curricular_code="09").prerequisites.values_list("curricular_code", flat=True)),
            ["01"],
        )

    def test_attached_data_imports_and_marks_uncertain_names(self):
        call_command("seed_fiis", stdout=StringIO())
        self.assertEqual(Course.objects.count(), 85)
        self.assertFalse(Course.objects.filter(name="INVESTIGACIÓN OPERATIVA II").exists())
        self.assertEqual(Course.objects.get(curricular_code="38").semester, 5)
        self.assertEqual(Course.objects.get(curricular_code="PA3-2026").semester, 6)
        self.assertEqual(Section.objects.count(), 219)
        self.assertEqual(Section.objects.filter(course__isnull=True).count(), 0)
        self.assertEqual(Section.objects.filter(published=False).count(), 15)
        self.assertEqual(Course.objects.get(curricular_code="38").semester, 5)
        moved = Section.objects.get(period__code="2026-1", source_row="4")
        self.assertTrue(moved.meetings.filter(day=1, start=time(8), end=time(9, 40)).exists())
        self.assertGreaterEqual(
            Section.objects.filter(period__code="2026-2", course__curricular_code="09", published=True).count(), 2
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-1", official_code="101523", course__curricular_code="38", published=True
            ).count(),
            3,
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-2", official_code="101529", course__curricular_code="PA3-2026", published=True
            ).count(),
            3,
        )
        self.assertEqual(
            Section.objects.filter(period__code="2026-2", official_code="101520", course__curricular_code="28").count(),
            3,
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-2", official_code="101560", course__curricular_code="SQL-101560", published=False
            ).count(),
            1,
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-2", official_code="101556", course__curricular_code="E-3.2"
            ).count(),
            1,
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-2", official_code="ELECT-4", course__curricular_code="RUP-2026", published=False
            ).count(),
            1,
        )
        self.assertEqual(
            Section.objects.filter(
                period__code="2026-2", official_code="INVEST-X", course__curricular_code="57"
            ).count(),
            3,
        )

    def test_adjusted_schedules_keep_duration_and_have_no_resource_overlaps(self):
        import json
        from pathlib import Path

        from .schedule_adjust import adjusted_schedule, minutes

        directory = Path(__file__).resolve().parent.parent / "data"
        for period, file in [("2026-1", "horario_2026_1.json"), ("2026-2", "horario_2026_2.json")]:
            raw = json.loads((directory / file).read_text(encoding="utf8"))
            original = raw["cursos"] if isinstance(raw, dict) else raw
            proposal, changes = adjusted_schedule(original, period)
            self.assertTrue(changes)
            self.assertEqual(adjusted_schedule(proposal, period)[1], [])
            for before, after in zip(original, proposal):
                old_sessions = before.get("sesiones", before.get("horario", []))
                new_sessions = after.get("sesiones", after.get("horario", []))
                for old, new in zip(old_sessions, new_sessions):
                    self.assertEqual(
                        minutes(old["fin"]) - minutes(old["inicio"]), minutes(new["fin"]) - minutes(new["inicio"])
                    )
            self.assertEqual(len(proposal), len(original))


class EndToEndApiTests(TestCase):
    def test_student_can_activate_account_and_set_full_name(self):
        call_command("seed_fiis", "--demo-users", stdout=StringIO())
        user = User.objects.get(username="2024023935")
        user.set_unusable_password()
        user.is_active = False
        user.save()
        user.student.active = False
        user.student.save(update_fields=["active"])
        AccountSecurity.objects.update_or_create(user=user, defaults={"activation_pending": True})
        response = self.client.post(
            "/api/auth/activate/",
            data='{"student_code":"2024023935","email":"2024023935@unfv.edu.pe","full_name":"María Alumna Villarreal","password":"ClaveNueva2026!"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("ClaveNueva2026!"))
        self.assertEqual(user.student.full_name, "María Alumna Villarreal")

    def test_student_preference_admin_demand_enrollment_and_receipt(self):
        call_command("seed_fiis", "--demo-users", stdout=StringIO())
        from django.test import Client

        from .models import Period

        client = Client(enforce_csrf_checks=True)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        response = client.post(
            "/api/auth/login/",
            data='{"email":"2024023935@unfv.edu.pe","password":"2024023935"}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
            HTTP_ORIGIN="http://localhost:5173",
        )
        self.assertEqual(response.status_code, 200)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        catalog = client.get("/api/catalog/").json()
        course_semesters = {course["id"]: course["semester"] for course in catalog["courses"]}
        self.assertTrue({course_semesters[section["course_id"]] for section in catalog["sections"]}.issubset({2, 3}))
        sections = [s for s in catalog["sections"] if s["curricular_code"] == "09"]
        self.assertGreaterEqual(len(sections), 2)
        selected = sections[0]["id"]
        import json

        self.assertEqual(
            client.post(
                "/api/preselection/",
                data=json.dumps({"section_ids": [selected]}),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            200,
        )
        self.assertEqual(Section.objects.get(pk=selected).enrollment_lines.count(), 0)
        client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=token)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        admin_login = client.post(
            "/api/auth/login/",
            data='{"username":"demo","password":"demo"}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(admin_login.status_code, 200)
        self.assertEqual(set(admin_login.json()["roles"]), {"admin", "teacher", "student"})
        self.assertIsNone(admin_login.json()["role"])
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        selected_role = client.post(
            "/api/auth/role/", data='{"role":"admin"}', content_type="application/json", HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(selected_role.json()["role"], "admin")
        self.assertEqual(client.get("/api/admin/demand/").json()["total_students"], 1)
        period = Period.objects.get(code="2026-2")
        self.assertEqual(
            client.patch(
                f"/api/admin/periods/{period.pk}/",
                data='{"status":"enroll"}',
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            200,
        )
        client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=token)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        self.assertEqual(
            client.post(
                "/api/auth/login/",
                data='{"email":"2024023935@unfv.edu.pe","password":"2024023935"}',
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            200,
        )
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        response = client.post(
            "/api/enrollments/",
            data=json.dumps({"section_ids": [selected]}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201, response.content)
        receipt = client.get(f"/api/enrollments/{response.json()['id']}/pdf/")
        self.assertEqual(receipt.status_code, 200)
        self.assertTrue(receipt.content.startswith(b"%PDF"))


class TeacherAndPhotoTests(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name="Plan de docencia")
        self.period = Period.objects.create(code="DOC-1", status="enroll", is_current=True)
        self.course = Course.objects.create(
            plan=self.plan, curricular_code="DOC1", name="Prácticas", semester=1, credits=3
        )
        self.teacher_user = User.objects.create_user("docente1", password="DocentePrueba2026!")
        self.teacher = Teacher.objects.create(name="PROFESOR UNO", user=self.teacher_user)
        self.other_teacher_user = User.objects.create_user("docente2", password="DocentePrueba2026!")
        self.other_teacher = Teacher.objects.create(name="PROFESOR DOS", user=self.other_teacher_user)
        self.section = Section.objects.create(
            period=self.period,
            course=self.course,
            teacher=self.teacher,
            raw_name="Prácticas",
            section_code="A",
            official_code="DOC-101",
            classroom="LAB-1",
            published=True,
        )
        other_section = Section.objects.create(
            period=self.period,
            course=self.course,
            teacher=self.other_teacher,
            raw_name="Prácticas",
            section_code="B",
            official_code="DOC-102",
            classroom="LAB-2",
            published=True,
        )
        Meeting.objects.create(section=self.section, day=1, start=time(8), end=time(9))
        Meeting.objects.create(section=other_section, day=2, start=time(10), end=time(11))
        for i, (section, name) in enumerate(
            [(self.section, "ALUMNA AUTORIZADA"), (other_section, "ALUMNO DE OTRO DOCENTE")]
        ):
            user = User.objects.create_user(f"alumno{i}")
            student = Student.objects.create(user=user, student_code=f"DOC-S{i}", full_name=name, plan=self.plan)
            enrollment = Enrollment.objects.create(student=student, period=self.period)
            EnrollmentLine.objects.create(enrollment=enrollment, section=section, course=self.course)

    def test_teacher_sees_only_own_roster_and_can_download_private_pdf(self):
        self.client.force_login(self.teacher_user)
        self.assertEqual(self.client.get("/api/me/").json()["role"], "teacher")
        data = self.client.get("/api/teacher/sections/").json()
        self.assertEqual(len(data["sections"]), 1)
        self.assertEqual(data["sections"][0]["students"], [{"code": "DOC-S0", "name": "ALUMNA AUTORIZADA"}])
        pdf = self.client.get("/api/teacher/report/pdf/?period=DOC-1")
        self.assertEqual(pdf.status_code, 200)
        content = PdfReader(BytesIO(pdf.content)).pages[0].extract_text()
        self.assertIn("ALUMNA AUTORIZADA", content)
        self.assertNotIn("ALUMNO DE OTRO DOCENTE", content)
        self.assertEqual(
            self.client.get(
                f"/api/teacher/report/pdf/?period=DOC-1&section_id={self.other_teacher.section_set.first().pk}"
            ).status_code,
            404,
        )
        self.client.force_login(Student.objects.first().user)
        self.assertEqual(self.client.get("/api/teacher/sections/").status_code, 403)
        self.client.force_login(
            User.objects.create_superuser("administrador", "admin@example.com", "AdminDePrueba2026!")
        )
        self.assertEqual(self.client.get("/api/teacher/sections/").status_code, 403)

    def test_photo_is_validated_and_private_for_every_role(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        self.client.force_login(self.teacher_user)
        image = Image.new("RGB", (800, 600), (220, 110, 40))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        upload = SimpleUploadedFile("foto.png", buffer.getvalue(), content_type="image/png")
        self.assertEqual(self.client.post("/api/profile/photo/", {"photo": upload}).status_code, 200)
        response = self.client.get("/api/profile/photo/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(Image.open(BytesIO(response.content)).size, (512, 384))
        self.assertTrue(self.client.get("/api/me/").json()["has_photo"])
        self.client.force_login(Student.objects.first().user)
        self.assertEqual(self.client.get("/api/profile/photo/").status_code, 404)
        self.assertEqual(
            self.client.post(
                "/api/profile/photo/",
                {"photo": SimpleUploadedFile("alumno.png", buffer.getvalue(), content_type="image/png")},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/profile/photo/",
                {"photo": SimpleUploadedFile("invalida.gif", b"GIF89a", content_type="image/gif")},
            ).status_code,
            400,
        )
        self.client.force_login(
            User.objects.create_superuser("admin.photo", "adminphoto@example.com", "AdminDePrueba2026!")
        )
        self.assertEqual(
            self.client.post(
                "/api/profile/photo/",
                {"photo": SimpleUploadedFile("admin.png", buffer.getvalue(), content_type="image/png")},
            ).status_code,
            200,
        )
        self.assertEqual(ProfilePhoto.objects.count(), 3)
        self.client.force_login(self.teacher_user)
        self.assertEqual(self.client.delete("/api/profile/photo/").status_code, 200)
        self.assertFalse(ProfilePhoto.objects.filter(user=self.teacher_user).exists())

    def test_admin_links_imported_teacher_to_new_account(self):
        admin = User.objects.create_superuser("admin2", "admin2@example.com", "AdminDePrueba2026!")
        imported = Teacher.objects.create(name="DOCENTE IMPORTADO")
        self.client.force_login(admin)
        result = self.client.post(
            "/api/admin/teachers/",
            data='{"name":"DOCENTE IMPORTADO","email":"docente.importado@unfv.edu.pe","password":"ContrasenaDemo2026!"}',
            content_type="application/json",
        )
        self.assertEqual(result.status_code, 201, result.content)
        imported.refresh_from_db()
        self.assertFalse(imported.user.is_staff)
        self.assertEqual(imported.user.email, "docente.importado@unfv.edu.pe")
        self.assertEqual(
            self.client.post(
                "/api/admin/teachers/",
                data='{"name":"DOCENTE IMPORTADO","email":"otro.docente@unfv.edu.pe","password":"ContrasenaDemo2026!"}',
                content_type="application/json",
            ).status_code,
            400,
        )

    def test_admin_cannot_schedule_teacher_or_room_twice(self):
        import json

        admin = User.objects.create_superuser("admin3", "admin3@example.com", "AdminDePrueba2026!")
        self.client.force_login(admin)
        data = {
            "period_id": self.period.id,
            "course_id": self.course.id,
            "section": "C",
            "teacher_id": self.teacher.id,
            "classroom": "LAB-3",
            "meetings": [{"day": 1, "start": "08:30", "end": "10:00"}],
        }
        self.assertEqual(
            self.client.post(
                "/api/admin/sections/", data=json.dumps(data), content_type="application/json"
            ).status_code,
            400,
        )
        data.update(teacher_id=self.other_teacher.id, classroom="lab-1")
        self.assertEqual(
            self.client.post(
                "/api/admin/sections/", data=json.dumps(data), content_type="application/json"
            ).status_code,
            400,
        )
        self.assertFalse(Section.objects.filter(section_code="C").exists())


class PostgreSQLConcurrencyTests(TransactionTestCase):
    def test_simultaneous_last_seat(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requiere PostgreSQL local")
        from concurrent.futures import ThreadPoolExecutor

        plan = Plan.objects.create(name="Concurrencia")
        period = Period.objects.create(code="T-POSTGRES", status="enroll", max_credits=10)
        course = Course.objects.create(plan=plan, curricular_code="R", name="Redes", semester=1, credits=3)
        section = Section.objects.create(
            period=period, course=course, section_code="A", raw_name="Redes", capacity=1, published=True
        )
        Meeting.objects.create(section=section, day=0, start=time(8), end=time(9))
        students = []
        for i in range(2):
            user = User.objects.create_user(f"competidor{i}")
            students.append(Student.objects.create(user=user, plan=plan, student_code=f"C{i}", full_name=f"Alumno {i}"))

        def compete(student):
            close_old_connections()
            try:
                confirm_enrollment(student, period, [section.pk])
                return True
            except ValidationError:
                return False
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(compete, students))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(EnrollmentLine.objects.count(), 1)
