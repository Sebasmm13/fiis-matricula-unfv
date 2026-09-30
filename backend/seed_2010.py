import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres.byypgkguuyviypwntcav:Morancito132@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
os.environ['DJANGO_SECRET_KEY'] = 'x'
os.environ['DJANGO_DEBUG'] = '1'
django.setup()

from core.models import Plan, Course

data = """
**PRIMER CICLO**
* **Código:** 2A0125 | **Asignatura:** LÓGICA Y ALGORITMOS | **Créditos:** 3 | **Pre-requisitos:** NINGUNO
* **Código:** 380058 | **Asignatura:** ALGEBRA LINEAL | **Créditos:** 2 | **Pre-requisitos:** NINGUNO
* **Código:** 5A0060 | **Asignatura:** COMPUTACIÓN E INFORMÁTICA BÁSICA | **Créditos:** 4 | **Pre-requisitos:** NINGUNO
* **Código:** 2C0187 | **Asignatura:** LENGUAJE Y REDACCIÓN | **Créditos:** 4 | **Pre-requisitos:** NINGUNO
* **Código:** 600037 | **Asignatura:** METODOLOGÍA DE LA INVESTIGACIÓN | **Créditos:** 3 | **Pre-requisitos:** NINGUNO
* **Código:** 880116 | **Asignatura:** INTRODUCCIÓN A LA INGENIERÍA DE SISTEMAS | **Créditos:** 2 | **Pre-requisitos:** NINGUNO
* **Código:** 380103 | **Asignatura:** MATEMÁTICA BÁSICA | **Créditos:** 5 | **Pre-requisitos:** NINGUNO

**SEGUNDO CICLO**
* **Código:** 3A0014 | **Asignatura:** FÍSICA | **Créditos:** 4 | **Pre-requisitos:** MATEMATICA BASICA (380103)
* **Código:** 700080 | **Asignatura:** ECONOMÍA | **Créditos:** 3 | **Pre-requisitos:** NINGUNO
* **Código:** 380165 | **Asignatura:** CÁLCULO DIFERENCIAL E INTEGRAL | **Créditos:** 5 | **Pre-requisitos:** MATEMATICA BASICA (380103)
* **Código:** 880109 | **Asignatura:** ALGORITMOS Y ESTRUCTURA DE DATOS | **Créditos:** 4 | **Pre-requisitos:** LOGICA Y ALGORITMOS (2A0125)
* **Código:** 780192 | **Asignatura:** CONTABILIDAD GENERAL | **Créditos:** 3 | **Pre-requisitos:** NINGUNO
* **Código:** 7A0472 | **Asignatura:** ADMINISTRACIÓN DE NEGOCIOS | **Créditos:** 3 | **Pre-requisitos:** NINGUNO

**TERCER CICLO**
* **Código:** 8F0123 | **Asignatura:** ELECTROMAGNETISMO Y ONDAS | **Créditos:** 4 | **Pre-requisitos:** FISICA (3A0014)
* **Código:** 5B0110 | **Asignatura:** ESTADÍSTICA Y PROBABILIDADES | **Créditos:** 4 | **Pre-requisitos:** MATEMATICA BASICA (380103)
* **Código:** 3B0166 | **Asignatura:** ECUACIONES DIFERENCIALES | **Créditos:** 4 | **Pre-requisitos:** CALCULO DIFERENCIAL E INTEGRAL (380165)
* **Código:** 8E0035 | **Asignatura:** LENGUAJE DE PROGRAMACIÓN ESTRUCTURADO | **Créditos:** 4 | **Pre-requisitos:** ALGORITMOS Y ESTRUCTURA DE DATOS (880109), COMPUTACION E INFORMATICA BASICA (5A0060)
* **Código:** 880073 | **Asignatura:** TEORÍA DE SISTEMAS | **Créditos:** 3 | **Pre-requisitos:** INTRODUCCION A LA INGENIERIA DE SISTEMAS (880116)
* **Código:** 8E0039 | **Asignatura:** PROGRAMACIÓN LINEAL | **Créditos:** 3 | **Pre-requisitos:** ALGEBRA LINEAL (380058)

**CUARTO CICLO**
* **Código:** 8F0127 | **Asignatura:** SISTEMAS DIGITALES | **Créditos:** 4 | **Pre-requisitos:** ELECTROMAGNETISMO Y ONDAS (8F0123)
* **Código:** 580021 | **Asignatura:** ESTADÍSTICA INFERENCIAL | **Créditos:** 4 | **Pre-requisitos:** ESTADISTICA Y PROBABILIDADES (5B0110)
* **Código:** 380170 | **Asignatura:** MATEMÁTICAS DISCRETAS | **Créditos:** 4 | **Pre-requisitos:** ECUACIONES DIFERENCIALES (380166)
* **Código:** 8E0036 | **Asignatura:** LENGUAJE DE PROGRAMACIÓN ORIENTADO A OBJETOS | **Créditos:** 4 | **Pre-requisitos:** LENGUAJE DE PROGRAMACION ESTRUCTURADO (8E0035)
* **Código:** 600006 | **Asignatura:** INVESTIGACIÓN OPERATIVA | **Créditos:** 3 | **Pre-requisitos:** ESTADISTICA Y PROBABILIDADES (5B0110)
* **Código:** 780184 | **Asignatura:** COSTOS Y PRESUPUESTOS | **Créditos:** 3 | **Pre-requisitos:** CONTABILIDAD GENERAL (780192), ECONOMIA (700080)

**QUINTO CICLO**
* **Código:** SA0063 | **Asignatura:** FUNDAMENTOS DE BASE DE DATOS | **Créditos:** 4 | **Pre-requisitos:** ALGORITMOS Y ESTRUCTURA DE DATOS (880109)
* **Código:** 8E0037 | **Asignatura:** LENGUAJE DE PROGRAMACIÓN ORIENTADO A WEB | **Créditos:** 3 | **Pre-requisitos:** LENGUAJE DE PROGRAMACION ORIENTADO A OBJETOS (8E0036)
* **Código:** 8E0003 | **Asignatura:** SISTEMAS OPERATIVOS | **Créditos:** 4 | **Pre-requisitos:** LENGUAJE DE PROGRAMACION ESTRUCTURADO (8E0035)
* **Código:** 780197 | **Asignatura:** INGENIERÍA DE PROCESOS DE NEGOCIOS | **Créditos:** 4 | **Pre-requisitos:** ADMINISTRACION DE NEGOCIOS (7A0472)
* **Código:** 5A0015 | **Asignatura:** ARQUITECTURA DEL COMPUTADOR | **Créditos:** 3 | **Pre-requisitos:** SISTEMAS DIGITALES (8F0127)
* **Código:** 880110 | **Asignatura:** ANÁLISIS Y DISEÑO DE SISTEMAS DE INFORMACIÓN | **Créditos:** 4 | **Pre-requisitos:** TEORIA DE SISTEMAS (880073), LENGUAJE DE PROGRAMACION ORIENTADO A OBJETOS (8E0036)

**SEXTO CICLO**
* **Código:** 2H0033 | **Asignatura:** FUNDAMENTOS DE COMUNICACIONES | **Créditos:** 4 | **Pre-requisitos:** ARQUITECTURA DEL COMPUTADOR (5A0015)
* **Código:** 7C0081 | **Asignatura:** INGENIERÍA ECONÓMICA | **Créditos:** 3 | **Pre-requisitos:** COSTOS Y PRESUPUESTOS (780184)
* **Código:** 880068 | **Asignatura:** SISTEMAS DE BASE DE DATOS | **Créditos:** 4 | **Pre-requisitos:** FUNDAMENTOS DE BASE DE DATOS (SA0063)
* **Código:** 2A0124 | **Asignatura:** FILOSOFÍA Y ÉTICA | **Créditos:** 4 | **Pre-requisitos:** LENGUAJE Y REDACCION (2C0187)
* **Código:** 200109 | **Asignatura:** SISTEMAS DE GESTIÓN DEL POTENCIAL HUMANO | **Créditos:** 3 | **Pre-requisitos:** ANALISIS Y DISEÑO DE SISTEMAS DE INFORMACION (880110)
* **Código:** 880059 | **Asignatura:** INGENIERÍA DE SOFTWARE I | **Créditos:** 4 | **Pre-requisitos:** ANALISIS Y DISEÑO DE SISTEMAS DE INFORMACION (880110)

**SÉPTIMO CICLO**
* **Código:** 8B0111 | **Asignatura:** ARQUITECTURA Y CONECTIVIDAD DE REDES | **Créditos:** 3 | **Pre-requisitos:** FUNDAMENTOS DE COMUNICACIONES (2H0033)
* **Código:** 7A0480 | **Asignatura:** MARKETING EMPRESARIAL | **Créditos:** 3 | **Pre-requisitos:** INGENIERIA DE PROCESOS DE NEGOCIOS (780197)
* **Código:** 880085 | **Asignatura:** DINÁMICA DE SISTEMAS | **Créditos:** 3 | **Pre-requisitos:** MATEMATICAS DISCRETAS (380170)
* **Código:** 7A0013 | **Asignatura:** ADMINISTRACIÓN FINANCIERA | **Créditos:** 3 | **Pre-requisitos:** INGENIERIA ECONOMICA (7C0081)
* **Código:** 880114 | **Asignatura:** INGENIERÍA DE SOFTWARE II | **Créditos:** 3 | **Pre-requisitos:** INGENIERIA DE SOFTWARE I (880059)
* **Código:** 880071 | **Asignatura:** TALLER DE BASE DE DATOS | **Créditos:** 4 | **Pre-requisitos:** SISTEMAS DE BASE DE DATOS (880068)
* **Código:** 210230 | **Asignatura:** GEOPOLÍTICA Y DEFENSA NACIONAL | **Créditos:** 3 | **Pre-requisitos:** FILOSOFIA Y ETICA (2A0124)

**OCTAVO CICLO**
* **Código:** 880108 | **Asignatura:** ADMINISTRACIÓN DE REDES | **Créditos:** 4 | **Pre-requisitos:** ARQUITECTURA Y CONECTIVIDAD DE REDES (8B0111)
* **Código:** 210229 | **Asignatura:** DERECHO INFORMÁTICO Y EMPRESARIAL | **Créditos:** 3 | **Pre-requisitos:** MARKETING EMPRESARIAL (7A0480)
* **Código:** 880072 | **Asignatura:** TALLER DE INTEGRACIÓN DE SISTEMAS | **Créditos:** 4 | **Pre-requisitos:** INGENIERIA DE SOFTWARE II (880114)
* **Código:** 7A0482 | **Asignatura:** PLANEAMIENTO ESTRATÉGICO DE NEGOCIOS | **Créditos:** 4 | **Pre-requisitos:** MARKETING EMPRESARIAL (7A0480)
* **Código:** 8B0067 | **Asignatura:** SIMULACIÓN DE SISTEMAS | **Créditos:** 3 | **Pre-requisitos:** DINAMICA DE SISTEMAS (880085)
* **Código:** 8F0126 | **Asignatura:** NEGOCIOS ELECTRÓNICOS | **Créditos:** 4 | **Pre-requisitos:** INGENIERIA DE PROCESOS DE NEGOCIOS (780197)

**NOVENO CICLO**
* **Código:** GA0062 | **Asignatura:** PRÁCTICAS PRE PROFESIONALES I | **Créditos:** 6 | **Pre-requisitos:** TALLER DE INTEGRACION DE SISTEMAS (880072), ARQUITECTURA Y CONECTIVIDAD DE REDES (8B0111)
* **Código:** 7A0477 | **Asignatura:** LIDERAZGO Y CREATIVIDAD EMPRESARIAL | **Créditos:** 3 | **Pre-requisitos:** PLANEAMIENTO ESTRATEGICO DE NEGOCIOS (7A0482)
* **Código:** 5A0062 | **Asignatura:** FORMULACIÓN Y VALUACIÓN DE PROYECTOS INFORMÁTICOS | **Créditos:** 4 | **Pre-requisitos:** PLANEAMIENTO ESTRATEGICO DE NEGOCIOS (7A0482)
* **Código:** 8B0074 | **Asignatura:** TÓPICOS ESPECIALES EN INGENIERÍA DE SISTEMAS I | **Créditos:** 3 | **Pre-requisitos:** TALLER DE INTEGRACION DE SISTEMAS (880072)
* **Código:** 8F0124 | **Asignatura:** INTELIGENCIA ARTIFICIAL | **Créditos:** 4 | **Pre-requisitos:** SIMULACION DE SISTEMAS (8B0067)
* **Código:** 880118 | **Asignatura:** SEGURIDAD EN REDES Y SISTEMAS DE INFORMACIÓN | **Créditos:** 3 | **Pre-requisitos:** ADMINISTRACION DE REDES (880108)

**DÉCIMO CICLO**
* **Código:** GA0063 | **Asignatura:** PRÁCTICAS PRE PROFESIONALES II | **Créditos:** 6 | **Pre-requisitos:** PRACTICAS PRE PROFESIONALES I (GA0062)
* **Código:** HC0107 | **Asignatura:** SEMINARIO DE TESIS | **Créditos:** 2 | **Pre-requisitos:** FORMULACION Y EVALUACION DE PROYECTOS INFORMATICOS (5A0062)
* **Código:** BA0328 | **Asignatura:** GESTIÓN DEL CONOCIMIENTO | **Créditos:** 3 | **Pre-requisitos:** INTELIGENCIA ARTIFICIAL (8F0124)
* **Código:** 880112 | **Asignatura:** GERENCIA DE PROYECTOS DE TECNOLOGÍA DE INFORMACIÓN Y COMUNICACIONES | **Créditos:** 4 | **Pre-requisitos:** PLANEAMIENTO ESTRATEGICO DE NEGOCIOS (7A0482), SEGURIDAD EN REDES Y SISTEMAS DE INFORMACION (880118)
* **Código:** 8B0121 | **Asignatura:** TÓPICOS ESPECIALES EN INGENIERÍA DE SISTEMAS II | **Créditos:** 4 | **Pre-requisitos:** TOPICOS ESPECIALES EN INGENIERIA DE SISTEMAS I (8B0074)
* **Código:** 8B0003 | **Asignatura:** AUDITORÍA DE SISTEMAS | **Créditos:** 4 | **Pre-requisitos:** SEGURIDAD EN REDES Y SISTEMAS DE INFORMACION (880118)
"""

# Parse data
plan_name = "PLAN CURRICULAR 2010 - INGENIERÍA DE SISTEMAS"
plan, created = Plan.objects.get_or_create(name=plan_name, defaults={"source": "Resolución Rectoral N° 10578-2010-CU-UNFV (15.03.2010)"})

current_semester = 0
courses = []

for line in data.split('\n'):
    line = line.strip()
    if not line:
        continue
    
    if line.startswith('**PRIMER CICLO**'): current_semester = 1
    elif line.startswith('**SEGUNDO CICLO**'): current_semester = 2
    elif line.startswith('**TERCER CICLO**'): current_semester = 3
    elif line.startswith('**CUARTO CICLO**'): current_semester = 4
    elif line.startswith('**QUINTO CICLO**'): current_semester = 5
    elif line.startswith('**SEXTO CICLO**'): current_semester = 6
    elif line.startswith('**SÉPTIMO CICLO**'): current_semester = 7
    elif line.startswith('**OCTAVO CICLO**'): current_semester = 8
    elif line.startswith('**NOVENO CICLO**'): current_semester = 9
    elif line.startswith('**DÉCIMO CICLO**'): current_semester = 10
    
    elif line.startswith('* **Código:**'):
        parts = [p.strip() for p in line.split('|')]
        
        codigo = parts[0].replace('* **Código:**', '').strip()
        nombre = parts[1].replace('**Asignatura:**', '').strip()
        creditos = parts[2].replace('**Créditos:**', '').strip()
        prereqs_str = parts[3].replace('**Pre-requisitos:**', '').strip()
        
        prereq_codes = []
        if prereqs_str != 'NINGUNO':
            matches = re.findall(r'\(([A-Z0-9]+)\)', prereqs_str)
            prereq_codes = [m.strip() for m in matches]
        
        courses.append({
            'code': codigo,
            'name': nombre,
            'credits': int(creditos),
            'semester': current_semester,
            'prereqs': prereq_codes
        })

# Create courses
created_courses = {}
for c in courses:
    course, _ = Course.objects.update_or_create(
        curricular_code=c['code'],
        plan=plan,
        defaults={
            'name': c['name'],
            'credits': c['credits'],
            'semester': c['semester'],
            'academic_data_verified': True
        }
    )
    created_courses[c['code']] = course

# Link prerequisites
warnings = []
for c in courses:
    if c['prereqs']:
        course = created_courses[c['code']]
        for pr_code in c['prereqs']:
            if pr_code in created_courses:
                course.prerequisites.add(created_courses[pr_code])
            else:
                warnings.append(f"WARNING: Prerequisite {pr_code} not found for {c['code']}")

print(f"Plan and {len(courses)} courses successfully seeded!")
for w in warnings:
    print(w)
