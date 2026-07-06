"""
export_utils.py — PDF and CSV export helpers
"""

import io
import csv
from datetime import date
from typing import List, Dict
from fpdf import FPDF


# ── CSV Export ────────────────────────────────────────────────────────────────

def export_csv(schedule: dict, subjects: list) -> bytes:
    """Return CSV bytes of the full study schedule."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Day", "Subject", "Hours", "Difficulty", "Exam Date"])

    subj_map = {s.name: s for s in subjects}

    for d in sorted(schedule.keys()):
        tasks = schedule[d]
        day_name = d.strftime("%A")
        for task in tasks:
            sub = subj_map.get(task.subject_name)
            writer.writerow([
                d.isoformat(),
                day_name,
                task.subject_name,
                task.hours,
                task.difficulty,
                sub.exam_date.isoformat() if sub else "",
            ])

    return output.getvalue().encode("utf-8")


# ── PDF Export ────────────────────────────────────────────────────────────────

class StudyPlanPDF(FPDF):
    def header(self):
        self.set_fill_color(99, 102, 241)
        self.rect(0, 0, 210, 24, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.set_y(6)
        self.cell(0, 10, "Smart Study Planner AI", align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(160, 160, 180)
        self.cell(0, 8, f"Smart Study Planner AI  |  Page {self.page_no()}", align="C")


def export_pdf(schedule: dict, subjects: list, config: dict) -> bytes:
    """Return PDF bytes of the full study plan."""
    pdf = StudyPlanPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # ── Meta info ──
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 130)
    meta = (
        f"Generated: {date.today()}  |  "
        f"Daily Hours: {config.get('daily_hours', '-')}h  |  "
        f"Start: {config.get('start_date', '-')}  |  "
        f"Session: {config.get('session_length', '-')}h"
    )
    pdf.cell(0, 6, meta, align="C")
    pdf.ln(8)

    # ── Subject overview table ──
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 70)
    pdf.cell(0, 8, "Subject Overview", ln=True)
    pdf.ln(2)

    # Header row
    pdf.set_fill_color(99, 102, 241)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    col_w = [70, 35, 30, 45]
    for label, w in zip(["Subject", "Difficulty", "Hours", "Exam Date"], col_w):
        pdf.cell(w, 8, label, border=0, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for i, s in enumerate(subjects):
        fill = i % 2 == 0
        pdf.set_fill_color(245, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(40, 40, 70)
        pdf.cell(col_w[0], 7, s.name,               fill=fill, align="L")
        pdf.cell(col_w[1], 7, s.difficulty,          fill=fill, align="C")
        pdf.cell(col_w[2], 7, f"{s.total_hours}h",   fill=fill, align="C")
        pdf.cell(col_w[3], 7, s.exam_date.isoformat(),fill=fill, align="C")
        pdf.ln()

    pdf.ln(8)

    # ── Schedule table ──
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 70)
    pdf.cell(0, 8, "Daily Study Schedule", ln=True)
    pdf.ln(2)

    pdf.set_fill_color(99, 102, 241)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    s_col = [35, 25, 65, 25, 30]
    for label, w in zip(["Date", "Day", "Subject", "Hours", "Difficulty"], s_col):
        pdf.cell(w, 8, label, border=0, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    row_i = 0
    for d in sorted(schedule.keys()):
        for task in schedule[d]:
            fill = row_i % 2 == 0
            pdf.set_fill_color(248, 247, 255) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(40, 40, 70)
            pdf.cell(s_col[0], 6, d.isoformat(),        fill=fill, align="C")
            pdf.cell(s_col[1], 6, d.strftime("%a"),     fill=fill, align="C")
            pdf.cell(s_col[2], 6, task.subject_name,    fill=fill, align="L")
            pdf.cell(s_col[3], 6, f"{task.hours}h",     fill=fill, align="C")
            pdf.cell(s_col[4], 6, task.difficulty,      fill=fill, align="C")
            pdf.ln()
            row_i += 1

    return bytes(pdf.output())
