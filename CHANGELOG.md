# Entrega inicial

- Dos perfiles con login, control de acceso por servidor y auditoría de acciones.
- Malla y horarios de los tres JSON, importación reproducible y marcadores de revisión.
- Prematrícula para estimación de demanda, matrícula transaccional y PDF de elección.
- Administración de planes, cursos, profesores, alumnos, notas, horarios, vacantes y períodos.
- Pruebas del flujo completo y prueba de concurrencia habilitada para PostgreSQL.

## Correcciones de malla y horario

- Se registran las aclaraciones sobre Programación Aplicada II y III, Investigación Operativa, Programming with SQL, Routing and Switching y Taller de Tesis; se conservan como cursos distintos RUP y UML, Arduino y los electivos con otros nombres.
- El importador vincula las 219 secciones; 15 quedan sin publicar hasta validar créditos. Las propuestas de créditos y prerrequisito para Programación Aplicada III y la elección de Taller de Tesis II deben ser confirmadas por FIIS.
- Los archivos originales se conservan y se entregan dos horarios propuestos con 170 sesiones reubicadas, más un CSV con cada cambio.

## Acceso docente y perfiles

- Tercer rol docente con acceso restringido a sus horarios y alumnos matriculados; reporte privado en PDF por sección o período.
- Foto de perfil autogestionada para alumnos, docentes y personal administrativo. Las imágenes validadas se almacenan de forma separada en PostgreSQL; esquema actualizado a 24 tablas.
- La constancia de matrícula se descarga al confirmar y también queda accesible desde el panel del alumno.
- Interfaz en naranja y negro inspirada en los colores institucionales publicados por la UNFV.
