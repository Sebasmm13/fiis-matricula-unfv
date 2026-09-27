from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .services import section_info


def enrollment_pdf(enrollment):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if path.exists() and "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", str(path)))
    font = "DejaVu" if path.exists() else "Helvetica"
    out = BytesIO()
    p = canvas.Canvas(out, pagesize=landscape(A4))
    w, h = landscape(A4)
    p.setTitle(f"Constancia de matrícula {enrollment.period.code}")
    p.setFillColorRGB(0.12, 0.11, 0.10)
    p.rect(0, h - 110, w, 110, stroke=0, fill=1)
    p.setFillColorRGB(0.78, 0.29, 0.09)
    p.rect(0, h - 114, w, 4, stroke=0, fill=1)
    p.setFillColorRGB(1, 1, 1)
    p.setFont(font, 15)
    p.drawString(40, h - 42, "UNFV · FIIS")
    p.setFont(font, 12)
    p.drawString(40, h - 68, "CONSTANCIA DE MATRÍCULA")
    p.setFont(font, 9)
    p.drawString(40, h - 91, "Escuela Profesional de Ingeniería de Sistemas")
    p.setFillColorRGB(0.1, 0.2, 0.3)
    p.setFont(font, 9)
    student = enrollment.student
    p.drawString(40, h - 138, f"Alumno: {student.full_name}     Código: {student.student_code}")
    p.drawString(
        40,
        h - 157,
        f"Plan: {student.plan.name}     Período: {enrollment.period.code}     Confirmado: {enrollment.confirmed_at:%d/%m/%Y %H:%M}     N.° matrícula: {enrollment.pk}",
    )
    headings = [("Código", 40), ("Curso", 120), ("Sección / salón", 420), ("Docente", 530), ("Créditos", 760)]
    p.setFillColorRGB(0.99, 0.92, 0.86)
    p.rect(38, h - 190, w - 76, 22, fill=1, stroke=0)
    p.setFillColorRGB(0.1, 0.2, 0.3)
    p.setFont(font, 8)
    for title, x in headings:
        p.drawString(x, h - 183, title)
    y = h - 208
    lines = (
        enrollment.lines.select_related("section", "course")
        .prefetch_related("section__meetings")
        .order_by("course__semester", "course__name")
    )
    for row in lines:
        info = row.snapshot or section_info(row.section)
        if y < 68:
            p.showPage()
            y = h - 50
            p.setFont(font, 8)
        p.setFont(font, 7.5)
        p.drawString(40, y, (info.get("official_code") or "SIN CÓDIGO")[:16])
        p.drawString(120, y, info["course_name"][:43])
        p.drawString(420, y, f"{info['section']} / {info['classroom']}"[:22])
        p.drawString(530, y, info["teacher"][:36])
        p.drawString(760, y, str(info.get("credits", row.course.credits) or "-"))
        y -= 13
        for m in info["meetings"]:
            p.setFillColorRGB(0.32, 0.38, 0.45)
            p.drawString(122, y, f"{m['day_name']} {m['start']}-{m['end']}")
            y -= 12
        p.setStrokeColorRGB(0.87, 0.9, 0.93)
        p.line(40, y + 3, w - 40, y + 3)
        y -= 9
        p.setFillColorRGB(0.1, 0.2, 0.3)
    total_credits = sum((row.snapshot or {}).get("credits", row.course.credits) or 0 for row in lines)
    p.setFont(font, 8)
    p.drawString(40, max(47, y - 8), f"Total: {len(lines)} cursos · {total_credits} créditos")
    p.save()
    return out.getvalue()


def teacher_report_pdf(teacher_name, period_code, sections):
    """Reporte privado de carga horaria y alumnos con paginación automática."""
    out = BytesIO()
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if font_path.exists() and "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font_path)))
    font = "DejaVu" if font_path.exists() else "Helvetica"
    accent = colors.HexColor("#C85219")
    styles = getSampleStyleSheet()
    heading = ParagraphStyle(
        "fiis_title", parent=styles["Title"], fontName=font, fontSize=15, leading=21, textColor=accent
    )
    body = ParagraphStyle("fiis_body", parent=styles["Normal"], fontName=font, fontSize=9, leading=14)
    small = ParagraphStyle("fiis_small", parent=body, fontSize=8, leading=11)
    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=44,
        bottomMargin=46,
        title=f"Horarios y alumnos {period_code}",
    )
    story = [
        Paragraph("FIIS · UNFV | HORARIOS Y ALUMNOS", heading),
        Paragraph(f"Docente: {escape(teacher_name)} · Período: {escape(period_code)}", body),
        Spacer(1, 12),
    ]
    if not sections:
        story.append(Paragraph("No tienes secciones asignadas para este período.", body))
    for s in sections:
        info = f"{escape(s['course_name'])} · {escape(s['official_code'] or 'Código pendiente')} · Sección {escape(s['section'])} · Salón {escape(s['classroom'] or 'Por asignar')}"
        hours = ", ".join(f"{m['day_name']} {m['start']}–{m['end']}" for m in s["meetings"]) or "Horario pendiente"
        introduction = [
            Paragraph(info, body),
            Paragraph(f"Horario: {escape(hours)}", small),
            Paragraph(f"Alumnos matriculados: {len(s['students'])}", small),
            Spacer(1, 5),
        ]
        cells = [[Paragraph("Código", small), Paragraph("Alumno matriculado", small)]]
        cells.extend(
            [
                [Paragraph(escape(student["code"]), small), Paragraph(escape(student["name"]), small)]
                for student in s["students"]
            ]
        )
        if not s["students"]:
            cells.append([Paragraph("—", small), Paragraph("Sin matrículas confirmadas", small)])
        table = Table(cells, colWidths=[115, 395], repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FCEBDD")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FCF8F4")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#E7DAD0")),
                ]
            )
        )
        story.extend([KeepTogether(introduction), table, Spacer(1, 17)])
    doc.build(story)
    return out.getvalue()
