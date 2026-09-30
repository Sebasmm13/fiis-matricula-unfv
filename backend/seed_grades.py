import os
import django
import random
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DATABASE_URL"] = "postgresql://postgres.byypgkguuyviypwntcav:Morancito132@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
os.environ["DJANGO_SECRET_KEY"] = "x"
django.setup()

from core.models import Student, Course, FinalGrade, Period

def get_student(name_snippet):
    student = Student.objects.filter(full_name__icontains=name_snippet).first()
    if not student:
        print(f"ERROR: No se encontró alumno con '{name_snippet}'")
    return student

def seed_grades():
    historical_period = Period.objects.get(code='HISTORICO')
    luis = get_student("luis")
    lenin = get_student("lenin")
    juan = get_student("juan")
    denzel = get_student("denzel")
    moran = get_student("moran")

    if not all([luis, lenin, juan, denzel, moran]):
        print("Faltan alumnos en la BD. Por favor revisa los nombres.")
        return

    # Limpiamos notas anteriores para estos alumnos si las hubiere
    FinalGrade.objects.filter(student__in=[luis, lenin, juan, denzel, moran]).delete()

    print("Limpiadas las notas anteriores.")

    def assign_grades(student, up_to_cycle, failed_courses=[]):
        courses = Course.objects.filter(plan=student.plan, semester__lte=up_to_cycle)
        grades_created = 0
        for course in courses:
            is_failed = course.curricular_code in failed_courses or course.name in failed_courses
            score = random.randint(1, 10) if is_failed else random.randint(11, 20)
            
            FinalGrade.objects.create(
                student=student,
                course=course,
                period=historical_period,
                score=Decimal(score),
                passed=(score >= 11)
            )
            grades_created += 1
        print(f"-> Asignadas {grades_created} notas a {student.full_name} (Hasta ciclo {up_to_cycle})")

    print("\n--- INICIANDO ASIGNACIÓN DE NOTAS ---")
    
    # 1. Luis Arturo: Limpio hasta 6to ciclo
    print("\n1. Luis Arturo (Limpio hasta 6to ciclo)")
    assign_grades(luis, 6)

    # 2. Lenin Alvarez: Hasta 2do ciclo, pero jala MATEMÁTICA (que debe ser de 1ro o 2do)
    # Buscamos un curso de 1er o 2do ciclo que tenga prerrequisitos. 'MATEMÁTICA' o 'FÍSICA' o el código que aplique.
    # En la malla adjunta, el 07 es MATEMÁTICA.
    print("\n2. Lenin Alvarez (Hasta 2do ciclo, jala curso clave)")
    assign_grades(lenin, 2, failed_courses=["07", "MATEMÁTICA", "FÍSICA", "MATEMATICA"])

    # 3. Juan David: Hasta 4to ciclo, con 2 jalados
    print("\n3. Juan David (Hasta 4to ciclo, 2 jalados)")
    # Seleccionamos dos cursos al azar de su malla de 3er y 4to ciclo para que los jale.
    juan_courses = Course.objects.filter(plan=juan.plan, semester__in=[3, 4])
    juan_failed = list(juan_courses.values_list('curricular_code', flat=True)[:2])
    assign_grades(juan, 4, failed_courses=juan_failed)

    # 4. Denzel: Hasta 6to ciclo, con 1 jalado
    print("\n4. Denzel (Hasta 6to ciclo, 1 jalado en 5to)")
    denzel_courses = Course.objects.filter(plan=denzel.plan, semester=5)
    denzel_failed = list(denzel_courses.values_list('curricular_code', flat=True)[:1])
    assign_grades(denzel, 6, failed_courses=denzel_failed)

    # 5. Moran: Hasta 8vo ciclo, limpio (o le ponemos algún jalado leve? El usuario dijo Moran hasta 8vo ciclo limpio)
    # Releyendo: "y a los demas usuarios ... llenales hasta 4to 6to y 8vo ... en 2 de esos ponles que jalo uno o dos cursos".
    # Juan jaló 2, Denzel jaló 1. Moran irá limpio hasta el 8vo.
    print("\n5. Moran (Hasta 8vo ciclo, limpio)")
    assign_grades(moran, 8)

    print("\n--- ¡ASIGNACIÓN COMPLETADA EXITOSAMENTE! ---")

if __name__ == "__main__":
    seed_grades()
