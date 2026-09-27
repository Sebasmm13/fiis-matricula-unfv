"""Sustituye nombres docentes por identificadores estables para datos públicos."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "backend" / "data" / "horario_2026_1.json",
    ROOT / "backend" / "data" / "horario_2026_2.json",
]
PLACEHOLDERS = {"", "CCNN", "NO ESPECIFICADO", "POR ASIGNAR"}


def rows(document: object) -> list[dict[str, object]]:
    if isinstance(document, dict):
        return document["cursos"]
    if isinstance(document, list):
        return document
    raise ValueError("Formato de horario no reconocido")


def main() -> None:
    documents = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in FILES]
    names = sorted(
        {
            str(row.get("docente") or "").strip()
            for _, document in documents
            for row in rows(document)
            if str(row.get("docente") or "").strip().upper() not in PLACEHOLDERS
        },
        key=str.casefold,
    )
    mapping = {name: f"DOCENTE {index:03d}" for index, name in enumerate(names, 1)}
    changed = 0
    for path, document in documents:
        for row in rows(document):
            original = str(row.get("docente") or "").strip()
            if original in mapping:
                row["docente"] = mapping[original]
                changed += 1
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Anonimizados {len(mapping)} docentes en {changed} secciones.")


if __name__ == "__main__":
    main()
