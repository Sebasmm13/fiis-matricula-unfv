# Sistema de matrícula FIIS–UNFV

Sistema de matrícula para la Escuela Profesional de Ingeniería de Sistemas de la Facultad de Ingeniería Industrial y de Sistemas (FIIS). Incluye portal de alumno, panel de administración, API REST y PostgreSQL.

![Pantalla de acceso del portal FIIS](docs/screenshots/login.png)

## Requisitos

- Python 3.11 o superior (recomendado 3.12), Node.js 20.19+ o 22.12+, npm.
- Docker Desktop para levantar PostgreSQL con el `docker-compose.yml` incluido, o un servidor PostgreSQL propio.

## Inicio rápido en Windows PowerShell

Abre una consola en la carpeta que contiene este README:

```powershell
docker compose up -d db
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://fiis:fiis_local@127.0.0.1:5432/fiis_matricula"
$env:DJANGO_SECRET_KEY="clave-local-cambiar-para-produccion"
$env:DJANGO_DEBUG="1"
py manage.py migrate
py manage.py seed_fiis --demo-users
py manage.py runserver 127.0.0.1:8000
```

Si PowerShell bloquea el script de activación, ejecuta `.venv\Scripts\python.exe` en lugar de `py` en los comandos siguientes.

En una **segunda consola**:

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Vite envía `/api/` al backend en el puerto 8000; por eso ambos procesos deben seguir encendidos. No es necesario ejecutar `flask` ni crear manualmente las tablas.

Para Linux/macOS: sustituye `py` por `python3`, la activación por `source .venv/bin/activate` y la asignación de variables por `export VARIABLE=valor`.

### Cuentas locales de demostración

Se crean **únicamente** al pasar `--demo-users`:

| Perfil | Usuario o correo | Contraseña |
| --- | --- | --- |
| Alumno, docente y administrador | `demo` | `demo` |
| Alumno | `2024023935@unfv.edu.pe` | `2024023935` |
| Alumno | `2024023953@unfv.edu.pe` | `2024023953` |
| Alumno | `2024024193@unfv.edu.pe` | `2024024193` |
| Alumno | `2024035007@unfv.edu.pe` | `2024035007` |
| Alumno | `2024024406@unfv.edu.pe` | `2024024406` |

La cuenta `demo` tiene los tres perfiles y muestra el selector de acceso después de iniciar sesión. Las cuentas numéricas tienen aprobados los cursos del primer ciclo para poder probar la prematrícula del segundo ciclo.

La importación es idempotente: se puede repetir y no sobrescribe cambios hechos en registros ya importados. **Si ya importaste la entrega anterior**, ejecutar el comando otra vez no cambiará sus sesiones existentes; para probar esta propuesta usa una base nueva o revisa y modifica los horarios desde administración. Cambia las contraseñas para cualquier entorno accesible a otras personas; en despliegues reales usa una clave secreta larga, `DJANGO_DEBUG=0`, HTTPS, credenciales nuevas, política de copias de seguridad y un método de autenticación institucional.

### Demostración guiada

1. Entra como **alumno**. Se importan las notas aprobadas del primer ciclo para que el alumno de ejemplo pueda escoger asignaturas del segundo ciclo.
2. Abre **Matrícula**, compara las secciones de `INGLÉS II` u otro curso disponible y pulsa **Guardar prematrícula**. En esta etapa no se reserva asiento.
3. Entra como **administrador**, revisa **Demanda y prematrícula** y cambia el estado de `2026-2` a `Matrícula` en **Configuración**.
4. Regresa como **alumno**, selecciona secciones sin cruces y pulsa **Confirmar matrícula**. La constancia PDF se descargará inmediatamente; en **Inicio** seguirán disponibles el horario semanal y el botón **Constancia PDF**.
5. Para observar el límite de vacantes, el administrador puede modificar la capacidad de una sección antes de que los alumnos se inscriban.
6. Entra como **docente** para consultar los horarios y los alumnos que ya confirmaron matrícula en tus secciones; exporta un PDF por sección o uno completo. Cada perfil puede actualizar su propia foto en **Mi perfil**.

**Nota:** si durante una prueba una cuenta ya confirmó su matrícula, usa otra de las cuentas de alumno para repetir el flujo en el mismo período. El sistema impide una segunda confirmación y deja las rectificaciones para administración.

## Datos importados y decisiones de modelado

- `backend/data/malla_curricular.json`: **67 cursos base y 15 electivos** de las cinco menciones, con créditos y prerrequisitos. Programación Aplicada II corresponde al quinto ciclo y Programación Aplicada III es un curso regular del sexto; Investigación Operativa II no forma parte del quinto ciclo. El importador añade **3 cursos distintos**: Programming with SQL, Análisis de Sistemas: RUP y UML y Programación en Arduino. Son **85 cursos en la base**.
- `backend/data/horario_2026_1.json` y `horario_2026_2.json`: **118 + 101 = 219 secciones** de ambos períodos, con código, sección, salón, docente y sesiones.
- La identificación curricular (`01`, `02`, etc.) es distinta del código oficial del curso en un horario (`100382`, etc.); se conservan ambas. La constancia muestra el código del horario.
- Las **219 secciones** están vinculadas a cursos; `REVISION_DATOS.md` registra las correcciones confirmadas y las decisiones provisionales. **15 secciones**, entre ellas SQL, RUP y UML y Arduino, **quedan sin publicar** hasta completar sus créditos y revisar su correspondencia académica.
- Las fuentes **no desglosan horas académicas teóricas y prácticas**. Se muestran como “por validar” hasta que administración las indique por curso; los minutos semanales del horario sí se calculan desde las sesiones y se identifican como tales. No se asume que una hora académica equivale a 60 minutos.
- La capacidad inicial es de **35 vacantes por sección** y puede modificarse desde administración.
- Antes de publicarse, los nombres de docentes de los JSON fueron sustituidos por identificadores estables (`DOCENTE 001`, etc.). `PRIVACY.md` documenta el criterio y `scripts/anonymize_teacher_names.py` permite repetir la limpieza.
- `horario_propuesto_2026_1.json` y `horario_propuesto_2026_2.json` reubican 170 sesiones para eliminar superposiciones de grupo, docente y aula, conservando duración, docente y salón. `HORARIOS_PROPUESTOS_CAMBIOS.csv` detalla cada cambio. El alumno no puede confirmar una elección con cruces.
- La nota mínima de aprobación configurada es **11/20**.
- Se permite copiar la malla a un plan nuevo para conservar la versión anterior. Los alumnos nuevos pueden asignarse a la nueva versión.

## Funciones

**Alumno:** consulta de plan, notas, cursos aprobados, prerrequisitos, opciones de sección, profesores, salón, vacantes y horario; prematrícula no vinculante, matrícula con validaciones, horario confirmado y PDF descargado al confirmar.

**Docente:** acceso a sus secciones por período, horario semanal y listado de alumnos con matrícula confirmada; PDF completo o por sección. No puede consultar alumnos de otros docentes.

**Administrador:** períodos, docentes y sus cuentas de acceso, alumnos, versiones de plan, cursos, horas teóricas y prácticas, prerrequisitos, secciones y sesiones, aforo, publicación, notas, demanda estimada y auditoría. Para dar acceso a un docente importado, abre **Oferta académica → Acceso docente**, selecciona su nombre en las sugerencias y define usuario y contraseña.

**Fotos de perfil:** alumnos, docentes y personal administrativo pueden subir o eliminar su propia foto en **Mi perfil**. Se aceptan JPEG, PNG y WebP de hasta 2 MB; el servidor comprueba el contenido, reduce la imagen a un máximo de 512 px, elimina metadatos al convertirla a JPEG y la sirve solo a su dueño. La tabla separada `core_profilephoto` almacena la imagen procesada; `core_teacher.user_id` vincula de forma única las cuentas docentes. El esquema tiene **24 tablas**, incluida la infraestructura de Django.

**Integridad:** autorización por perfil desde el servidor; controles de prerrequisitos, duplicados, plan, períodos, crédito máximo y cruces; en PostgreSQL, la confirmación bloquea filas de secciones con `SELECT FOR UPDATE`, comprueba el aforo y registra todo en la misma transacción para que dos personas no obtengan la última plaza. La prematrícula no resta vacantes. La foto se almacena una sola vez por cuenta y cada docente puede vincularse con una sola cuenta.

**Aspecto visual:** la interfaz usa naranja, negro y fondos claros inspirados en los colores académicos publicados por la UNFV. Los tonos CSS son una propuesta para este proyecto, no una reproducción certificada del manual gráfico de FIIS. Referencia: [UNFV, identidad institucional](https://www.unfv.edu.pe/transparencia_estandar/Datos_Generales/Normas_Emitidas/Resoluciones/Consejo_Universitario/2025/Resolucion_R_Nro_5439_2025_CU_UNFV.pdf).

## Arquitectura y flujo de matrícula

```mermaid
flowchart LR
    U[React + TypeScript] -->|sesión y CSRF · /api| D[Django]
    D --> P[(PostgreSQL)]
    D --> PDF[Constancias PDF]
    D --> A[Autorización por alumno, docente y administrador]
```

El correo identifica todos los perfiles asociados a una cuenta. Si una persona es, por ejemplo, administradora y docente, después del acceso elige el perfil con el que desea trabajar; las autorizaciones se vuelven a comprobar en el servidor para cada operación.

```mermaid
flowchart LR
    S[Alumno elige cursos habilitados] --> R[Guarda prematrícula]
    R --> N[Administrador consulta demanda agrupada]
    N --> O[Administrador abre el periodo de matrícula]
    O --> E[Alumno confirma secciones y vacantes]
    E --> C[Matrícula registrada]
    C --> F[Descarga de constancia PDF]
```

## Estructura

```text
backend/
  config/                 Configuración Django
  core/                   Modelos, reglas, API, constancia PDF, pruebas, migración
  data/                   Tres JSON fuente y dos horarios propuestos
frontend/
  src/                    React, TypeScript, vistas y estilos
  vite.config.ts          Proxy local al backend
docker-compose.yml        PostgreSQL local
.env.example              Variables de entorno de referencia
scripts/build_schedules.py Generador reproducible de horarios propuestos
REVISION_DATOS.md         Equivalencias y decisiones por validar
REVISION_CRUCES.csv       Cruces de los horarios originales
HORARIOS_PROPUESTOS_CAMBIOS.csv  Sesiones movidas, antes y después
```

API relevante: `POST /api/auth/login/`, `GET /api/catalog/`, `POST /api/preselection/`, `GET|POST /api/enrollments/`, `GET /api/enrollments/{id}/pdf/`, `GET /api/grades/`, `GET /api/teacher/sections/`, `GET /api/teacher/report/pdf/`, `GET|POST|DELETE /api/profile/photo/`, `GET /api/admin/demand/`. La API administrativa incluye planes, cursos, períodos, docentes, secciones, alumnos, notas y auditoría. El frontend usa sesión y token CSRF; la base de datos solo es accesible desde el backend.

## Respaldo para PostgreSQL

`fiis_matricula_postgresql.sql` es una carga inicial reproducible para PostgreSQL, generada desde una base nueva con `migrate` y `seed_fiis --demo-users`. No contiene sesiones, auditoría, fotos, prematrículas ni matrículas. Primero crea el esquema con las migraciones y luego importa el respaldo:

```powershell
$env:DATABASE_URL="postgresql://fiis:fiis_local@127.0.0.1:5432/fiis_matricula"
cd backend
.\.venv\Scripts\python.exe manage.py migrate
cd ..
psql -d fiis_matricula -f fiis_matricula_postgresql.sql
```

El importador limpia las tablas de aplicación, restaura los registros y sincroniza las secuencias. El exportador excluye automáticamente las tablas operativas; aun así, para una entrega se recomienda ejecutarlo sobre una base recién sembrada:

```powershell
.\backend\.venv\Scripts\python.exe scripts\export_postgresql_sql.py backend\dev.sqlite3 fiis_matricula_postgresql.sql
```

## Verificación

Con PostgreSQL levantado y `DATABASE_URL` definida:

```powershell
cd backend
py manage.py test core
```

Incluye una prueba de dos solicitudes simultáneas por la última vacante **que solo se ejecuta sobre PostgreSQL**. La misma suite puede ejecutarse con `DJANGO_USE_SQLITE=1` para comprobaciones locales rápidas, pero esa prueba se omitirá: SQLite no proporciona el bloqueo de filas de PostgreSQL.

Antes de enviar cambios ejecuta:

```powershell
.\backend\.venv\Scripts\python.exe -m ruff format --check backend scripts
.\backend\.venv\Scripts\python.exe -m ruff check backend scripts
$env:DJANGO_USE_SQLITE="1"
.\backend\.venv\Scripts\python.exe backend\manage.py test core
cd frontend
npm run format:check
npm run lint
npm run build
```

GitHub Actions repite estas verificaciones con PostgreSQL y Node.js en cada `push` y `pull_request`. El código se distribuye bajo la licencia MIT incluida en `LICENSE`; las pautas para colaborar están en `CONTRIBUTING.md`.

