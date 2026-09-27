"""Genera archivos propuestos y trazabilidad desde los JSON originales."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from core.schedule_adjust import adjusted_schedule  # noqa: E402

DATA = ROOT / "backend" / "data"
CHANGES = ROOT / "HORARIOS_PROPUESTOS_CAMBIOS.csv"
PERIODS = [("2026-1", "horario_2026_1.json"), ("2026-2", "horario_2026_2.json")]
FIELDNAMES = [
    "periodo",
    "fila",
    "ciclo",
    "seccion",
    "codigo",
    "curso",
    "dia_original",
    "inicio_original",
    "fin_original",
    "dia_propuesto",
    "inicio_propuesto",
    "fin_propuesto",
]


def main():
    all_changes = []
    for period, filename in PERIODS:
        original = json.loads((DATA / filename).read_text(encoding="utf-8"))
        rows = original["cursos"] if isinstance(original, dict) else original
        proposal, changes = adjusted_schedule(rows, period)
        all_changes.extend(changes)
        output = DATA / f"horario_propuesto_{period.replace('-', '_')}.json"
        document = {**original, "cursos": proposal} if isinstance(original, dict) else proposal
        output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{period}: {len(proposal)} secciones, {len(changes)} sesiones ajustadas -> {output.name}")
    with CHANGES.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_changes)
    print(f"Trazabilidad: {len(all_changes)} cambios -> {CHANGES.name}")


if __name__ == "__main__":
    main()
