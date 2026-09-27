"""Exporta los datos de SQLite como SQL compatible con PostgreSQL.

El esquema debe crearse primero con ``python manage.py migrate``. Esto permite
que Django genere tipos, restricciones e índices exactamente como corresponde
en PostgreSQL; el archivo resultante se ocupa de restaurar los datos y ajustar
las secuencias de claves primarias.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

OPERATIONAL_TABLES = {
    "django_session",
    "django_admin_log",
    "core_auditlog",
    "core_preselection",
    "core_enrollmentline",
    "core_enrollment",
    "core_profilephoto",
}


def identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def literal(value: object, declared_type: str) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        return f"decode('{value.hex()}', 'hex')"
    if "BOOL" in declared_type.upper():
        return "TRUE" if bool(value) else "FALSE"
    if isinstance(value, (int, float)):
        return repr(value)
    text = str(value).replace("\x00", "").replace("'", "''")
    return "'" + text + "'"


def ordered_tables(connection: sqlite3.Connection, tables: list[str]) -> list[str]:
    available = set(tables)
    dependencies: dict[str, set[str]] = {}
    for table in tables:
        referenced = {
            row[2]
            for row in connection.execute(f"PRAGMA foreign_key_list({identifier(table)})")
            if row[2] in available and row[2] != table
        }
        dependencies[table] = referenced

    ordered: list[str] = []
    pending = set(tables)
    while pending:
        ready = sorted(table for table in pending if dependencies[table] <= set(ordered))
        if not ready:
            # No se espera un ciclo en el esquema actual. Este fallback mantiene
            # el resultado determinista y deja que PostgreSQL reporte el detalle.
            ready = [sorted(pending)[0]]
        ordered.extend(ready)
        pending.difference_update(ready)
    return ordered


def export(source: Path, destination: Path) -> tuple[int, int]:
    connection = sqlite3.connect(source)
    tables = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "AND name <> 'django_migrations' ORDER BY name"
        )
    ]
    tables = ordered_tables(connection, tables)

    lines = [
        "-- Respaldo de datos FIIS para PostgreSQL",
        "-- 1. Crea la base y configura DATABASE_URL.",
        "-- 2. Ejecuta: python manage.py migrate",
        "-- 3. Importa: psql -d fiis_matricula -f fiis_matricula_postgresql.sql",
        "-- No incluye sesiones, auditoría, fotos, prematrículas ni matrículas operativas.",
        "\\set ON_ERROR_STOP on",
        "SET client_encoding = 'UTF8';",
        "BEGIN;",
        "",
    ]
    if tables:
        lines.append(
            "TRUNCATE TABLE " + ", ".join(identifier(table) for table in tables) + " RESTART IDENTITY CASCADE;"
        )
        lines.append("")

    total_rows = 0
    for table in tables:
        columns = list(connection.execute(f"PRAGMA table_info({identifier(table)})"))
        names = [column[1] for column in columns]
        types = [column[2] or "" for column in columns]
        rows = [] if table in OPERATIONAL_TABLES else list(connection.execute(f"SELECT * FROM {identifier(table)}"))
        if not rows:
            continue
        lines.append(f"-- {table}: {len(rows)} filas")
        column_sql = ", ".join(identifier(name) for name in names)
        for row in rows:
            values = ", ".join(literal(value, types[index]) for index, value in enumerate(row))
            lines.append(f"INSERT INTO {identifier(table)} ({column_sql}) VALUES ({values});")
        lines.append("")
        total_rows += len(rows)

    for table in tables:
        columns = list(connection.execute(f"PRAGMA table_info({identifier(table)})"))
        if any(column[1] == "id" and column[5] for column in columns):
            table_literal = identifier(table).replace("'", "''")
            lines.append(
                f"SELECT setval(pg_get_serial_sequence('{table_literal}', 'id'), "
                f'COALESCE(MAX("id"), 1), MAX("id") IS NOT NULL) FROM {identifier(table)};'
            )
    lines.extend(["", "COMMIT;", ""])
    destination.write_text("\n".join(lines), encoding="utf-8")
    connection.close()
    return len(tables), total_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    table_count, row_count = export(args.source, args.destination)
    print(f"Exportadas {row_count} filas de {table_count} tablas a {args.destination}")


if __name__ == "__main__":
    main()
