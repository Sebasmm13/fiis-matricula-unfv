import json
import re
import unicodedata
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Course, FinalGrade, Meeting, Period, Plan, Section, Student, Teacher
from core.schedule_adjust import adjusted_schedule

DATA = Path(__file__).resolve().parents[3] / "data"
ROMAN = {v: i for i, v in enumerate(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"], 1)}
DAYS = {"LUNES": 0, "MARTES": 1, "MIERCOLES": 2, "JUEVES": 3, "VIERNES": 4, "SABADO": 5, "DOMINGO": 6}
# Únicamente equivalencias de denominación evidentes. Casos dudosos permanecen en revisión.
ALIASES = {
    "FUNDAMENTODEBASEDEDATOS": "33",
    "ADMINISTRACIONYGESTIONDEBASEDEDATOS": "46",
    "DISENODEBASEDEDATOS": "40",
    "TOPICOSESPECIALESENINTERNETDELASCOSAS": "53",
    "SEGURIDADDEREDESYSISTEMASDEINFORMACION": "55",
}


def norm(value):
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFD", value.upper()).encode("ascii", "ignore").decode())


class Command(BaseCommand):
    help = "Importa malla FIIS y ambos horarios 2026; opcionalmente crea usuarios locales."

    def add_arguments(self, parser):
        parser.add_argument("--demo-users", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        malla = json.loads((DATA / "malla_curricular.json").read_text(encoding="utf8"))
        plan, _ = Plan.objects.get_or_create(
            name="Ingeniería de Sistemas - malla adjunta",
            defaults={"source": "Malla adjunta con aclaraciones del estudiante y horarios propuestos 2026"},
        )
        indexed = {}
        for semester in malla["semestres"]:
            for row in semester["cursos"]:
                obj, _ = Course.objects.get_or_create(
                    plan=plan,
                    curricular_code=row["id"],
                    defaults={"name": row["asignatura"], "semester": semester["semestre"], "credits": row["creditos"]},
                )
                indexed[row["id"]] = obj
        # Correcciones curriculares confirmadas: no existe Investigación
        # Operativa II en V; Programación Aplicada II pertenece a V y
        # Programación Aplicada III es un curso regular de VI.
        Course.objects.filter(plan=plan, curricular_code="31", name__iexact="INVESTIGACIÓN OPERATIVA II").delete()
        applied_ii = indexed["38"]
        if applied_ii.semester != 5:
            applied_ii.semester = 5
            applied_ii.save(update_fields=["semester"])
        applied_iii = indexed["PA3-2026"]
        if applied_iii.semester != 6:
            applied_iii.semester = 6
            applied_iii.save(update_fields=["semester"])
        # Cursos distintos de los electivos que compartían posición o etiqueta.
        separate = {}
        for key, name in [
            ("SQL-101560", "PROGRAMMING WITH SQL"),
            ("RUP-2026", "ANÁLISIS DE SISTEMAS: RUP Y UML"),
            ("ARDUINO-2026", "PROGRAMACIÓN EN ARDUINO"),
        ]:
            separate[key], _ = Course.objects.get_or_create(
                plan=plan, curricular_code=key, defaults={"name": name, "semester": 6, "credits": None}
            )
        electives = {}
        for track in malla["certificaciones_progresivas_electivos"]:
            for row in track["cursos"]:
                key = row["codigo_electivo"]
                obj, _ = Course.objects.get_or_create(
                    plan=plan,
                    curricular_code=f"E-{key}",
                    defaults={
                        "name": row["asignatura"],
                        "semester": row["ciclo"],
                        "credits": None,
                        "elective_track": track["mencion"],
                    },
                )
                electives[key] = obj
        for semester in malla["semestres"]:
            for row in semester["cursos"]:
                indexed[row["id"]].prerequisites.set([indexed[p] for p in row["prerrequisitos"] if p in indexed])
        for track in malla["certificaciones_progresivas_electivos"]:
            for row in track["cursos"]:
                electives[row["codigo_electivo"]].prerequisites.set(
                    [
                        indexed[p] if p in indexed else electives[p]
                        for p in row["prerrequisitos"]
                        if p in indexed or p in electives
                    ]
                )
        by_name = {norm(c.name): c for c in indexed.values()}
        unmatched = []
        imported = 0
        for file, code in [("horario_2026_1.json", "2026-1"), ("horario_2026_2.json", "2026-2")]:
            payload = json.loads((DATA / file).read_text(encoding="utf8"))
            original_rows = payload["cursos"] if isinstance(payload, dict) else payload
            rows, changes = adjusted_schedule(original_rows, code)
            period, _ = Period.objects.get_or_create(
                code=code,
                defaults={
                    "status": "closed" if code == "2026-1" else "pre",
                    "is_current": code == "2026-2",
                    "max_credits": 24,
                },
            )
            for i, row in enumerate(rows):
                original = row["asignatura"]
                n = norm(original)
                course = by_name.get(n) or indexed.get(ALIASES.get(n, ""))
                match = re.search(r"\(\s*Electivo\s+(\d+\.\d+)\s*\)", original, re.I)
                if match:
                    candidate = electives.get(match.group(1))
                    base = norm(re.sub(r"\(\s*Electivo.*?\)", "", original, flags=re.I))
                    course = candidate if candidate and base == norm(candidate.name) else None
                # Correspondencias confirmadas y cursos distintos; RUP y UML,
                # SQL y Arduino no heredan los créditos de otros electivos.
                overrides = {
                    ("2026-1", "101523"): applied_ii,
                    ("2026-2", "101520"): indexed["28"],
                    ("2026-2", "101529"): applied_iii,
                    ("2026-2", "101560"): separate["SQL-101560"],
                    ("2026-2", "101556"): electives["3.2"],
                    ("2026-2", "ELECT-4"): separate["RUP-2026"],
                    ("2026-2", "ELECT-5"): separate["ARDUINO-2026"],
                    ("2026-2", "INVEST-X"): indexed["57"],
                }
                course = overrides.get((code, str(row.get("codigo") or "")), course)
                if code == "2026-1" and match and match.group(1) == "4.4" and norm(original).find("PMBOOK") >= 0:
                    course = electives["4.4"]
                if (
                    code == "2026-2"
                    and match
                    and match.group(1) == "1.2"
                    and norm(original).startswith("PROGRAMACIONAVANZADAJAVA")
                ):
                    course = electives["1.2"]
                if (
                    course
                    and course.semester != ROMAN.get(row["ciclo"])
                    and (code, str(row.get("codigo"))) != ("2026-2", "INVEST-X")
                ):
                    course = None  # El ciclo del horario no coincide con el de la malla.
                if not course:
                    unmatched.append(
                        {
                            "period": code,
                            "row": i + 1,
                            "name": original,
                            "code": row.get("codigo"),
                            "section": row["seccion"],
                        }
                    )
                teacher_name = (row.get("docente") or "").strip()
                teacher = (
                    Teacher.objects.get_or_create(name=teacher_name)[0]
                    if teacher_name and teacher_name.upper() not in ("CCNN", "POR ASIGNAR")
                    else None
                )
                section, created = Section.objects.get_or_create(
                    period=period,
                    source_row=str(i + 1),
                    defaults={
                        "course": course,
                        "section_code": row["seccion"],
                        "official_code": str(row.get("codigo") or ""),
                        "raw_name": original,
                        "cycle": row["ciclo"],
                        "teacher": teacher,
                        "classroom": row.get("aula") or "",
                        "capacity": 35,
                        "published": bool(course and course.credits),
                    },
                )
                if created:
                    for session in row.get("sesiones", row.get("horario", [])):
                        day = DAYS.get(norm(session["dia"]))
                        if day is None:
                            raise ValueError(f"Día desconocido: {session['dia']}")
                        Meeting.objects.create(section=section, day=day, start=session["inicio"], end=session["fin"])
                    imported += 1
            self.stdout.write(
                f"  {code}: {len(changes)} sesiones ajustadas para evitar cruces de sección, docente o aula."
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Plan: {len(indexed)} cursos base y {len(electives)} electivos; {imported} secciones nuevas; {len(unmatched)} filas pendientes de revisión."
            )
        )
        for r in unmatched:
            self.stdout.write(f"  REVISAR {r['period']} fila {r['row']} {r['name']} / {r['section']}")
        if options["demo_users"]:
            demo, _ = User.objects.get_or_create(username="demo")
            demo.email = "demo@unfv.edu.pe"
            demo.is_staff = True
            demo.is_superuser = True
            demo.set_password("demo")
            demo.save()
            demo_student = Student.objects.filter(student_code="DEMO2026001").first()
            if demo_student:
                demo_student.user = demo
                demo_student.save(update_fields=["user"])
            else:
                demo_student = Student.objects.create(
                    user=demo, student_code="DEMO2026001", full_name="Alumno de demostración", plan=plan
                )

            # Migra instalaciones creadas con las tres cuentas demo antiguas.
            legacy_usernames = ["alumno.demo", "admin.demo", "docente.demo"]
            Teacher.objects.filter(user__username__in=legacy_usernames).update(user=None)
            User.objects.filter(username__in=legacy_usernames).update(is_active=False)

            student_codes = ["2024023935", "2024023953", "2024024193", "2024035007", "2024024406"]
            students = [demo_student]
            for code in student_codes:
                user, _ = User.objects.get_or_create(username=code)
                user.email = f"{code}@unfv.edu.pe"
                user.set_password(code)
                user.save()
                student = Student.objects.filter(student_code=code).first()
                if student:
                    if student.user_id != user.id:
                        student.user = user
                        student.save(update_fields=["user"])
                else:
                    student = Student.objects.create(
                        user=user, student_code=code, full_name=f"Alumno {code}", plan=plan
                    )
                students.append(student)

            example = (
                Section.objects.filter(period__code="2026-2", teacher__isnull=False, teacher__user__isnull=True)
                .select_related("teacher")
                .first()
            )
            if example and not Teacher.objects.filter(user=demo).exists():
                example.teacher.user = demo
                example.teacher.save(update_fields=["user"])
            prev = Period.objects.get(code="2026-1")
            for student in students:
                for course in Course.objects.filter(plan=plan, semester=1):
                    FinalGrade.objects.get_or_create(
                        student=student, course=course, period=prev, defaults={"score": 15, "passed": True}
                    )
            self.stdout.write("Cuentas DEMO activadas. Cambia sus contraseñas antes de usar datos reales.")
