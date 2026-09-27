"""Generación de horarios ajustados sin modificar los JSON originales."""

import unicodedata
from copy import deepcopy

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]


def key(value):
    return "".join(
        char for char in unicodedata.normalize("NFD", (value or "").upper()) if unicodedata.category(char) != "Mn"
    )


DAY_INDEX = {key(name): index for index, name in enumerate(DAYS)}


def minutes(value):
    hours, rest = map(int, value.split(":"))
    return hours * 60 + rest


def clock(value):
    return f"{value // 60:02d}:{value % 60:02d}"


def sessions(row):
    return row.get("sesiones", row.get("horario", []))


def adjusted_schedule(rows, period):
    """Ubica sesiones conflictivas en la franja libre más cercana.

    Prioriza el día original, después un horario parecido en otro día. Evita
    coincidencias de grupo, docente y aula. Mantiene duración y docentes.
    """
    result = deepcopy(rows)
    assigned = []
    changes = []
    for index, row in enumerate(result, 1):
        for session in sessions(row):
            original_day = DAY_INDEX[key(session["dia"])]
            original_start = minutes(session["inicio"])
            duration = minutes(session["fin"]) - original_start
            if duration <= 0 or duration > 500:
                raise ValueError(f"Horario inválido: {period} fila {index}")
            name = row["asignatura"]
            section = row["seccion"]
            cycle = row["ciclo"]
            teacher = key(row.get("docente"))
            classroom = key(row.get("aula"))
            # La misma hora original puede no estar en la cuadrícula de 50 minutos.
            starts = sorted(set([original_start] + list(range(7 * 60, 22 * 60 + 11, 10))))
            candidates = []
            for day in range(6):
                for start in starts:
                    end = start + duration
                    if end > 22 * 60 + 10:
                        continue
                    day_distance = min(abs(day - original_day), 6 - abs(day - original_day))
                    # Conserva el día si el desplazamiento es pequeño; después,
                    # prefiere otro día con una hora parecida antes que mover 7 h.
                    band_penalty = 0
                    if section.startswith("M") and start >= 18 * 60:
                        band_penalty = 280
                    elif section.startswith("N") and start < 16 * 60:
                        band_penalty = 280
                    elif section.startswith("T") and start < 12 * 60:
                        band_penalty = 280
                    score = (
                        abs(start - original_start)
                        + 170 * day_distance
                        + (45 if day != original_day else 0)
                        + band_penalty,
                        day != original_day,
                        day_distance,
                        abs(start - original_start),
                        start,
                    )
                    candidates.append((score, day, start, end))
            candidates.sort()
            choice = None
            for _, day, start, end in candidates:
                conflict = False
                for old in assigned:
                    if old["day"] != day or not (start < old["end"] and old["start"] < end):
                        continue
                    if (
                        old["cycle"] == cycle
                        and old["section"] == section
                        or teacher
                        and teacher not in ("CCNN", "NO ESPECIFICADO", "POR ASIGNAR")
                        and teacher == old["teacher"]
                        or classroom
                        and classroom == old["classroom"]
                    ):
                        conflict = True
                        break
                if not conflict:
                    choice = (day, start, end)
                    break
            if choice is None:
                raise ValueError(f"No hay espacio para {period} fila {index}: {name}")
            day, start, end = choice
            if (day, start, end) != (original_day, original_start, original_start + duration):
                changes.append(
                    {
                        "periodo": period,
                        "fila": index,
                        "ciclo": cycle,
                        "seccion": section,
                        "codigo": row.get("codigo") or "",
                        "curso": name,
                        "dia_original": DAYS[original_day],
                        "inicio_original": clock(original_start),
                        "fin_original": clock(original_start + duration),
                        "dia_propuesto": DAYS[day],
                        "inicio_propuesto": clock(start),
                        "fin_propuesto": clock(end),
                    }
                )
            session.update(dia=DAYS[day], inicio=clock(start), fin=clock(end))
            assigned.append(
                {
                    "cycle": cycle,
                    "section": section,
                    "teacher": teacher,
                    "classroom": classroom,
                    "day": day,
                    "start": start,
                    "end": end,
                    "row": index,
                }
            )
    return result, changes
