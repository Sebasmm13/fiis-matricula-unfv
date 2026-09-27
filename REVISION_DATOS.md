# Revisión de la malla y los horarios adjuntos

El sistema conserva los JSON de horarios originales. En una instalación nueva, importa **85 cursos** (67 cursos base, 15 electivos y 3 cursos añadidos para distinguir asignaturas) y **219 secciones**. Cada sección está vinculada a un curso. Los códigos de la malla y los códigos impresos en el horario son identificadores diferentes.

## Correspondencias usadas en la importación

| Asignatura en el horario | Curso que registra el sistema | Estado de la decisión |
| --- | --- | --- |
| Programación Aplicada II, código 101523, ciclo V | Programación Aplicada II (38), curso regular del ciclo V | Confirmada por el estudiante. |
| Investigación Operativa, código 101520, ciclo IV | Investigación Operativa I (28), ciclo IV | Confirmada por el estudiante. |
| Programación Aplicada III, código 101529, ciclo VI | Curso regular PA3-2026, ciclo VI | Confirmado por el estudiante con 3 créditos y Programación Aplicada II como prerrequisito. |
| Investigación Operativa II | Eliminada de la malla | El estudiante confirmó que no pertenece al quinto ciclo. |
| Programming with SQL, código 101560, ciclo VI | Nuevo curso SQL-101560 | Confirmado como asignatura distinta del electivo Administración de Bases de Datos. Créditos pendientes. |
| Configuración de Routers y Switches, código 101556 | Electivo E-3.2, Routing and Switching | Cambio de denominación aceptado por el estudiante. Créditos pendientes. |
| Análisis de Sistemas: RUP y UML, electivo 4.2 del horario | Nuevo curso RUP-2026 | Se mantiene distinto del electivo E-4.2 Gestión de Servicios de TI. Créditos pendientes. |
| Programación en Arduino, electivo 5.2 del horario | Nuevo curso ARDUINO-2026 | Se mantiene distinto del electivo E-5.2 Sistemas Embebidos. Validar la correspondencia antes de publicar; créditos pendientes. |
| Trabajo de Investigación, ciclo X | Taller de Tesis II (57), ciclo IX en la malla | El estudiante confirmó equivalencia con Taller de Tesis; **elegir Taller de Tesis II es una interpretación provisional** por tratarse del ciclo final. El horario conserva la oferta en ciclo X. |
| Gestión de Proyectos y Fundamentos - PMBOOK | Electivo E-4.4, PMBOK | Correspondencia confirmada; se conserva el nombre original del horario. Créditos pendientes. |
| Programación Avanzada Java | Electivo E-1.2, Programación Avanzada | Es un cambio de denominación, según la aclaración del estudiante. Créditos pendientes. |

En una base recién creada hay **15 secciones sin publicar**, todas por falta de créditos confirmados: **10 de 2026-1 y 5 de 2026-2**. Están asociadas a cursos, pero no aparecen para matrícula hasta que el administrador complete los créditos y publique cada sección. Las horas académicas de teoría y práctica también requieren la fuente oficial; los minutos de sesión del horario se muestran por separado.

## Propuesta para los cruces

`REVISION_CRUCES.csv` documenta **105 pares de sesiones superpuestas en los horarios originales** para cursos distintos del mismo ciclo y sección (64 en 2026-1; 41 en 2026-2). Un mismo par puede figurar en días diferentes. Algunos electivos podrían ser alternativas deliberadas; el informe registra coincidencias sin asignarles una causa.

El generador `python scripts/build_schedules.py` crea dos JSON propuestos a partir de los originales. La propuesta mueve **101 sesiones de 2026-1 y 69 de 2026-2**; `HORARIOS_PROPUESTOS_CAMBIOS.csv` indica día y hora originales y propuestos por fila. Se conservan duración, docente, salón, códigos y número de secciones. El importador usa esa misma lógica en bases nuevas y evita superposiciones de grupo, docente y aula en cada período. No se conocen la disponibilidad real ni la aprobación institucional: **antes de usarla, FIIS debe validar las 170 reubicaciones**. Las fuentes originales no se reescriben.

La matrícula mantiene una comprobación adicional para impedir que cada alumno confirme cursos cuyas sesiones se crucen, incluso si el administrador edita después los horarios. La importación repetida conserva registros y sesiones existentes; para recibir la propuesta corregida en una instalación previa, usa una base nueva de prueba o actualiza los horarios existentes desde administración con revisión académica.
