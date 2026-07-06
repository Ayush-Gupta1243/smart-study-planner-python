"""
scheduler.py — Smart Study Planner Algorithm
=============================================
Priority Formula:
    Priority = (Difficulty Weight × 0.6) + (Exam Urgency Weight × 0.4)

Difficulty Weights:
    Easy   = 1
    Medium = 2
    Hard   = 3
"""

from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math

# ── Constants ────────────────────────────────────────────────────────────────
DIFFICULTY_WEIGHTS = {"Easy": 1, "Medium": 2, "Hard": 3}

SUBJECT_COLORS = [
    "#818cf8",  # indigo
    "#a78bfa",  # violet
    "#22d3ee",  # cyan
    "#34d399",  # emerald
    "#fb923c",  # orange
    "#f472b6",  # pink
    "#facc15",  # yellow
    "#60a5fa",  # blue
    "#f87171",  # red
    "#4ade80",  # green
]

STUDY_TIPS = {
    "Hard": [
        "Break into smaller topics — tackle one concept per session.",
        "Use active recall: flashcards and practice problems.",
        "Study when energy is highest (morning recommended).",
        "Teach-back method: explain concepts out loud.",
        "Solve previous year exam questions.",
    ],
    "Medium": [
        "Review notes within 24 hours of each session.",
        "Use mind maps to connect concepts visually.",
        "Practice past exam questions in the final week.",
        "Group similar topics together in one session.",
    ],
    "Easy": [
        "Use spaced repetition to lock in key facts.",
        "Quick daily reviews will keep knowledge fresh.",
        "Focus on edge cases and exceptions.",
    ],
}

# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class Subject:
    name: str
    total_hours: float
    difficulty: str
    exam_date: date
    color: str = ""
    remaining_hours: float = 0.0
    id: str = ""

    def __post_init__(self):
        if not self.color:
            self.color = _subject_color(self.name)
        if not self.remaining_hours:
            self.remaining_hours = self.total_hours
        if not self.id:
            self.id = self.name.lower().replace(" ", "_")

    @property
    def difficulty_weight(self) -> int:
        return DIFFICULTY_WEIGHTS.get(self.difficulty, 1)

    @property
    def days_until_exam(self) -> int:
        return max(1, (self.exam_date - date.today()).days)


@dataclass
class StudySession:
    subject_name: str
    hours: float
    difficulty: str
    color: str


@dataclass
class ScheduleResult:
    schedule: Dict[date, List[StudySession]]
    warnings: List[Dict]
    stats: Dict


# ── Core Algorithm ────────────────────────────────────────────────────────────

def calculate_priority(subject: Subject, current_date: date) -> float:
    """
    Priority = (Difficulty Weight × 0.6) + (Exam Urgency Weight × 0.4)
    Urgency is inversely proportional to days until exam.
    """
    diff_weight = subject.difficulty_weight

    days_left = max(1, (subject.exam_date - current_date).days)
    urgency_raw = min(30, days_left)
    # Scale: 3 when 1 day left, 1 when 30+ days left
    urgency_weight = 3 - ((urgency_raw - 1) / 29) * 2

    return (diff_weight * 0.6) + (urgency_weight * 0.4)


def generate_study_plan(
    subjects: List[Subject],
    start_date: date,
    daily_hours: float,
    session_length: float,
    break_duration: int = 15,
) -> ScheduleResult:
    """
    Generate an optimized day-by-day study schedule.

    Args:
        subjects      : List of Subject objects
        start_date    : When to start studying
        daily_hours   : Total available study hours per day
        session_length: Max hours per subject per day
        break_duration: Minutes between sessions (informational)

    Returns:
        ScheduleResult with schedule dict, warnings list, stats dict
    """
    if not subjects:
        return ScheduleResult({}, [], {})

    # Deep copy remaining hours
    remaining: Dict[str, float] = {s.id: s.total_hours for s in subjects}

    schedule: Dict[date, List[StudySession]] = {}

    # Date range: start → max exam date
    max_exam = max(s.exam_date for s in subjects)
    total_days = (max_exam - start_date).days + 1

    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)

        # Subjects still available today
        available = [
            s for s in subjects
            if remaining[s.id] > 0 and s.exam_date > current_date
        ]
        if not available:
            continue

        # Sort by priority score (highest first)
        available.sort(
            key=lambda s: calculate_priority(s, current_date),
            reverse=True
        )

        hours_left_today = daily_hours
        day_tasks: List[StudySession] = []

        for subj in available:
            if hours_left_today <= 0:
                break
            if remaining[subj.id] <= 0:
                continue

            hours_this = min(session_length, hours_left_today, remaining[subj.id])
            if hours_this < 0.25:
                continue

            hours_this = round(hours_this * 10) / 10
            day_tasks.append(StudySession(
                subject_name=subj.name,
                hours=hours_this,
                difficulty=subj.difficulty,
                color=subj.color,
            ))

            remaining[subj.id] -= hours_this
            remaining[subj.id] = round(remaining[subj.id] * 10) / 10
            hours_left_today -= hours_this

        if day_tasks:
            schedule[current_date] = day_tasks

    # ── Warnings ──────────────────────────────────────────────────────────────
    warnings = []
    for s in subjects:
        if remaining[s.id] > 0.5:
            done = s.total_hours - remaining[s.id]
            pct = round((done / s.total_hours) * 100) if s.total_hours else 0
            warnings.append({
                "subject": s.name,
                "message": f"⚠️ {s.name} may only reach {pct}% completion before exam on {s.exam_date}. Consider increasing daily hours.",
                "severity": "high" if remaining[s.id] > s.total_hours * 0.5 else "medium",
            })

    # ── Stats ──────────────────────────────────────────────────────────────────
    total_scheduled = sum(
        t.hours for tasks in schedule.values() for t in tasks
    )

    subject_breakdown = []
    for s in subjects:
        scheduled = round(s.total_hours - remaining[s.id], 1)
        pct = round((scheduled / s.total_hours) * 100) if s.total_hours else 0
        subject_breakdown.append({
            "name":      s.name,
            "total":     s.total_hours,
            "scheduled": scheduled,
            "pct":       pct,
            "color":     s.color,
            "difficulty": s.difficulty,
        })

    stats = {
        "total_days":        len(schedule),
        "total_hours":       round(total_scheduled, 1),
        "subject_breakdown": subject_breakdown,
    }

    return ScheduleResult(schedule, warnings, stats)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_subjects_from_text(text: str) -> List[Subject]:
    """
    Parse .txt file content into Subject objects.
    Format: SubjectName,TotalHours,Difficulty,ExamDate (YYYY-MM-DD)
    """
    from datetime import date as dt
    subjects = []

    for i, line in enumerate(text.strip().splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue

        name, hours_str, difficulty, exam_str = parts[:4]

        if difficulty not in DIFFICULTY_WEIGHTS:
            continue
        try:
            hours = float(hours_str)
            exam  = dt.fromisoformat(exam_str)
        except ValueError:
            continue

        subjects.append(Subject(
            name=name,
            total_hours=hours,
            difficulty=difficulty,
            exam_date=exam,
        ))

    return subjects


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_weekly_workload(schedule: Dict[date, List[StudySession]]) -> List[Dict]:
    """Aggregate study hours by week for charts."""
    weekly: Dict[date, Dict] = {}
    for d, tasks in sorted(schedule.items()):
        # Monday of the week
        monday = d - timedelta(days=d.weekday())
        if monday not in weekly:
            weekly[monday] = {"week": monday.strftime("%b %d"), "hours": 0, "sessions": 0}
        weekly[monday]["hours"]    += sum(t.hours for t in tasks)
        weekly[monday]["sessions"] += len(tasks)

    return [
        {**v, "hours": round(v["hours"], 1)}
        for v in weekly.values()
    ]


def generate_revision_days(subjects: List[Subject]) -> List[Dict]:
    """Recommend revision days 1-2 days before each exam."""
    result = []
    for s in subjects:
        rev_days = [
            (s.exam_date - timedelta(days=2)).isoformat(),
            (s.exam_date - timedelta(days=1)).isoformat(),
        ]
        result.append({
            "subject":      s.name,
            "color":        s.color,
            "exam_date":    s.exam_date.isoformat(),
            "revision_days": rev_days,
        })
    return result


def generate_focus_tips(subjects: List[Subject]) -> List[Dict]:
    """AI-style tips per subject based on difficulty."""
    tips = []
    for s in subjects:
        tips.append({
            "subject":    s.name,
            "color":      s.color,
            "difficulty": s.difficulty,
            "tips":       STUDY_TIPS.get(s.difficulty, []),
        })
    return tips


def get_today_sessions(schedule: Dict[date, List[StudySession]]) -> List[StudySession]:
    return schedule.get(date.today(), [])


def _subject_color(name: str) -> str:
    """Deterministic color from subject name."""
    h = 0
    for c in name:
        h = ord(c) + ((h << 5) - h)
    return SUBJECT_COLORS[abs(h) % len(SUBJECT_COLORS)]


# ── Sample Data ───────────────────────────────────────────────────────────────

SAMPLE_TEXT = """# Smart Study Planner - Sample Data
# Format: SubjectName,Hours,Difficulty,ExamDate
Mathematics,20,Hard,2026-07-10
Physics,15,Medium,2026-07-15
Chemistry,10,Easy,2026-07-20
Computer Science,18,Hard,2026-07-12
English Literature,8,Easy,2026-07-25
Biology,12,Medium,2026-07-18
"""
