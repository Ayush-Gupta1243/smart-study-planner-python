"""
app.py — Smart Study Planner AI (Streamlit)
============================================
Pure Python web app with:
- File upload OR manual subject entry
- Smart scheduling algorithm
- Interactive Plotly charts
- PDF + CSV export
- Dark premium UI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import io

# Local imports
from utils.scheduler import (
    Subject, generate_study_plan, parse_subjects_from_text,
    get_weekly_workload, generate_revision_days, generate_focus_tips,
    get_today_sessions, SAMPLE_TEXT,
)
from utils.export_utils import export_csv, export_pdf

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Study Planner AI",
    page_icon="🧠",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Dark background */
.stApp {
    background: linear-gradient(160deg, #070611 0%, #0d0b22 40%, #090d1f 100%);
    color: #e8e8ff;
}

/* Hide default streamlit header */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(255,255,255,0.5) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1rem 1.2rem !important;
    backdrop-filter: blur(20px);
}
[data-testid="stMetricValue"] { color: #e8e8ff !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.45) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 0.65rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.45) !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.75) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stDownloadButton > button:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #a5b4fc !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox select {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e8ff !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* Slider */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    overflow: hidden;
}

/* Alerts */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.25) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.25) !important; }
.stError   { background: rgba(239,68,68,0.1) !important;  border: 1px solid rgba(239,68,68,0.25) !important;  }
.stInfo    { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.25) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Radio buttons */
.stRadio > div { gap: 6px !important; }
.stRadio [data-baseweb="radio"] { background: rgba(255,255,255,0.04) !important; border-radius: 10px !important; padding: 6px 12px; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.8) !important;
}

/* ── Top header bar (replaces sidebar) ─────────────────────────────────── */
.app-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.3rem 0 0.6rem;
}
.app-header-icon { font-size: 1.9rem; line-height: 1; flex-shrink: 0; }
.app-header-title {
    font-size: 1.15rem;
    font-weight: 900;
    background: linear-gradient(135deg,#818cf8,#a78bfa,#22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.app-header-sub {
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 1px;
    margin-top: 1px;
}

/* Menu popover trigger button — match app button style */
[data-testid="stPopover"] button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    color: #e8e8ff !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}
[data-testid="stPopover"] button:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.4) !important;
}

/* Popover panel content (the mobile-friendly menu) */
[data-testid="stPopoverBody"] {
    max-height: 82vh;
    overflow-y: auto;
    min-width: 280px;
}

/* Tabs: allow horizontal scroll instead of squashing on narrow screens */
.stTabs [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { height: 4px; }
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.15);
    border-radius: 4px;
}
.stTabs [data-baseweb="tab"] { white-space: nowrap !important; flex-shrink: 0 !important; }

/* ── Responsive rules ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
    }

    /* Stack columns/cards vertically on small screens */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        row-gap: 0.6rem !important;
    }
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* Full-width buttons on mobile */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stPopover"] button {
        width: 100% !important;
    }

    /* Metric cards breathing room when stacked */
    [data-testid="stMetric"] { margin-bottom: 0.5rem; }

    /* Header sizing on small screens */
    .app-header-title { font-size: 1.05rem !important; }
    .app-header-icon { font-size: 1.6rem !important; }

    /* Tabs slightly tighter on mobile */
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 12px !important;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .block-container { padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Helper: HTML card ─────────────────────────────────────────────────────────
def card(content: str, border_color: str = "rgba(255,255,255,0.08)", bg: str = "rgba(255,255,255,0.04)"):
    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {border_color};
        border-radius:16px;
        padding:1.1rem 1.3rem;
        margin-bottom:0.75rem;
        backdrop-filter:blur(20px);
    ">{content}</div>
    """, unsafe_allow_html=True)

def badge(text: str, color: str) -> str:
    return f'<span style="background:{color}22;border:1px solid {color}44;color:{color};border-radius:6px;padding:2px 8px;font-size:11px;font-weight:600">{text}</span>'

def subject_pill(name: str, hours: float, color: str) -> str:
    return f'<span style="background:{color}18;border:1px solid {color}30;color:{color};border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;margin:2px;display:inline-block">● {name} · {hours}h</span>'

# ── Session state init ────────────────────────────────────────────────────────
for key, default in [
    ("subjects", []),
    ("schedule_result", None),
    ("config", {}),
    ("generated", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ════════════════════════════════════════════════════════════════════════════════
# TOP MENU BAR — mobile-friendly replacement for st.sidebar
# ════════════════════════════════════════════════════════════════════════════════
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown("""
    <div class="app-header">
        <div class="app-header-icon">🧠</div>
        <div>
            <div class="app-header-title">SmartStudy AI</div>
            <div class="app-header-sub">EXAM PLANNER</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    menu_popover = st.popover("☰ Menu", use_container_width=True)

subjects_ready: list[Subject] = []

with menu_popover:

    # ── Input Mode ────────────────────────────────────────────────────────────
    st.markdown("#### 📥 Input Mode")
    input_mode = st.radio(
        "input_mode_radio",
        ["📁 Upload .txt File", "✏️ Enter Manually"],
        label_visibility="collapsed",
    )

    st.divider()

    # ── FILE UPLOAD ───────────────────────────────────────────────────────────
    if input_mode == "📁 Upload .txt File":
        st.markdown("#### 📄 Upload Subject File")

        uploaded = st.file_uploader(
            "Choose a .txt file",
            type=["txt"],
            help="Format: SubjectName,Hours,Difficulty,ExamDate",
        )

        if uploaded:
            text = uploaded.read().decode("utf-8")
            parsed = parse_subjects_from_text(text)
            if parsed:
                st.session_state.subjects = parsed
                st.success(f"✅ {len(parsed)} subjects loaded!")
            else:
                st.error("❌ Invalid format. Check example below.")

        # Sample loader
        if st.button("📚 Load Sample Data", use_container_width=True):
            parsed = parse_subjects_from_text(SAMPLE_TEXT)
            st.session_state.subjects = parsed
            st.success(f"✅ {len(parsed)} sample subjects loaded!")

        # Format hint
        with st.expander("📋 File Format Example"):
            st.code("""# Format: Name,Hours,Difficulty,ExamDate
Mathematics,20,Hard,2026-07-10
Physics,15,Medium,2026-07-15
Chemistry,10,Easy,2026-07-20""", language="text")

        subjects_ready = st.session_state.subjects

    # ── MANUAL ENTRY ──────────────────────────────────────────────────────────
    else:
        st.markdown("#### ✏️ Add Subjects")

        if "manual_subjects" not in st.session_state:
            st.session_state.manual_subjects = [{"name":"","hours":10.0,"difficulty":"Medium","exam_date":date.today()+timedelta(days=14)}]

        # Add / Remove buttons
        col_add, col_clear = st.columns(2)
        with col_add:
            if st.button("➕ Add Subject", use_container_width=True):
                st.session_state.manual_subjects.append({
                    "name":"","hours":10.0,"difficulty":"Medium",
                    "exam_date": date.today() + timedelta(days=14)
                })
        with col_clear:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.manual_subjects = [{"name":"","hours":10.0,"difficulty":"Medium","exam_date":date.today()+timedelta(days=14)}]

        # Subject forms
        to_remove = []
        for i, subj in enumerate(st.session_state.manual_subjects):
            with st.expander(f"📚 Subject {i+1}: {subj['name'] or 'Untitled'}", expanded=True):
                subj["name"] = st.text_input(
                    "Subject Name *", value=subj["name"],
                    key=f"name_{i}", placeholder="e.g. Mathematics"
                )
                c1, c2 = st.columns(2)
                with c1:
                    subj["hours"] = st.number_input(
                        "Study Hours *", min_value=1.0, max_value=200.0,
                        value=float(subj["hours"]), step=0.5, key=f"hours_{i}"
                    )
                with c2:
                    subj["difficulty"] = st.selectbox(
                        "Difficulty *",
                        ["Easy","Medium","Hard"],
                        index=["Easy","Medium","Hard"].index(subj["difficulty"]),
                        key=f"diff_{i}"
                    )
                subj["exam_date"] = st.date_input(
                    "Exam Date *",
                    value=subj["exam_date"],
                    min_value=date.today() + timedelta(days=1),
                    key=f"exam_{i}"
                )

                # Difficulty badge
                diff_colors = {"Easy":"#10b981","Medium":"#f59e0b","Hard":"#ef4444"}
                diff_info   = {"Easy":"Lower priority","Medium":"Medium priority","Hard":"High priority — scheduled first"}
                dc = diff_colors.get(subj["difficulty"],"#6366f1")
                st.markdown(f"""<div style="margin-top:4px">{badge(f"● {subj['difficulty']} — {diff_info[subj['difficulty']]}", dc)}</div>""", unsafe_allow_html=True)

                if len(st.session_state.manual_subjects) > 1:
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        to_remove.append(i)

        for i in reversed(to_remove):
            st.session_state.manual_subjects.pop(i)
        if to_remove:
            st.rerun()

        # Build Subject objects from manual input
        manual_valid = []
        for s in st.session_state.manual_subjects:
            if s["name"].strip() and s["hours"] > 0:
                manual_valid.append(Subject(
                    name=s["name"].strip(),
                    total_hours=float(s["hours"]),
                    difficulty=s["difficulty"],
                    exam_date=s["exam_date"],
                ))
        subjects_ready = manual_valid

    st.divider()

    # ── Study Config ──────────────────────────────────────────────────────────
    st.markdown("#### ⚙️ Study Preferences")

    start_date = st.date_input(
        "📅 Study Start Date",
        value=date.today(),
        min_value=date.today(),
    )
    daily_hours = st.slider(
        "⏰ Daily Available Hours",
        min_value=1.0, max_value=14.0, value=6.0, step=0.5,
        help="Total hours you can study per day"
    )
    session_length = st.slider(
        "📖 Session Length (hours)",
        min_value=0.5, max_value=4.0, value=2.0, step=0.5,
        help="Max hours per subject per day"
    )
    break_duration = st.slider(
        "☕ Break Between Sessions (min)",
        min_value=5, max_value=60, value=15, step=5,
    )

    st.divider()

    # ── Generate Button ───────────────────────────────────────────────────────
    gen_btn = st.button("🚀 Generate Smart Plan", use_container_width=True, type="primary")

    if gen_btn:
        if not subjects_ready:
            st.error("⚠️ Add at least one subject first!")
        else:
            with st.spinner("Generating your optimized study plan..."):
                result = generate_study_plan(
                    subjects=subjects_ready,
                    start_date=start_date,
                    daily_hours=daily_hours,
                    session_length=session_length,
                    break_duration=break_duration,
                )
                st.session_state.subjects        = subjects_ready
                st.session_state.schedule_result = result
                st.session_state.generated       = True
                st.session_state.config          = {
                    "start_date":     start_date.isoformat(),
                    "daily_hours":    daily_hours,
                    "session_length": session_length,
                    "break_duration": break_duration,
                }
            st.success("✅ Plan generated!")
            st.rerun()

    # Status
    if st.session_state.generated:
        st.markdown("""
        <div style="text-align:center;margin-top:0.5rem">
            <span style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
                color:#34d399;border-radius:8px;padding:4px 12px;font-size:12px;font-weight:600">
                ✅ Plan Active
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='margin:0.2rem 0 1.2rem'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════════

# ── Hero (no data state) ──────────────────────────────────────────────────────
if not st.session_state.generated:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem 2rem">
        <div style="font-size:4rem;margin-bottom:1rem">🧠</div>
        <h1 style="font-size:3rem;font-weight:900;background:linear-gradient(135deg,#818cf8,#a78bfa,#22d3ee);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem">
            Smart Study Planner AI
        </h1>
        <p style="color:rgba(255,255,255,0.45);font-size:1.1rem;max-width:560px;margin:0 auto 2rem">
            Upload your subjects, set your schedule, and let AI generate an optimized study plan
            based on exam dates and difficulty levels.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    cols = st.columns(4)
    features = [
        ("⚡", "AI Prioritization",  "Difficulty + Urgency formula"),
        ("🎯", "Smart Scheduling",   "Balanced, no-overload days"),
        ("📊", "Visual Analytics",   "Charts, trends & insights"),
        ("🛡️", "Exam Warnings",      "Never miss a deadline"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            card(f"""
            <div style="font-size:2rem;margin-bottom:0.5rem">{icon}</div>
            <div style="font-weight:700;color:rgba(255,255,255,0.85);font-size:0.9rem">{title}</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.78rem;margin-top:0.2rem">{desc}</div>
            """)

    st.markdown("""
    <p style="text-align:center;color:rgba(255,255,255,0.2);font-size:0.85rem;margin-top:2rem">
        👆 Tap the ☰ Menu button above to add subjects and generate your plan
    </p>
    """, unsafe_allow_html=True)
    st.stop()

# ── Data ready — show tabs ─────────────────────────────────────────────────────
result   = st.session_state.schedule_result
subjects = st.session_state.subjects
schedule = result.schedule
stats    = result.stats
warnings = result.warnings
config   = st.session_state.config

# Page header
st.markdown("""
<div style="margin-bottom:1.5rem">
    <h1 style="font-size:1.8rem;font-weight:900;color:rgba(255,255,255,0.92);margin-bottom:0.2rem">
        📊 Your Study Plan
    </h1>
    <p style="color:rgba(255,255,255,0.38);font-size:0.9rem">
        AI-optimized schedule based on your subjects and preferences
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "📅 Study Plan", "📈 Analytics", "💡 AI Insights"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Stat Cards ──
    total_hours   = sum(s.total_hours for s in subjects)
    upcoming_exams= [s for s in subjects if s.exam_date >= date.today()]
    overall_pct   = round(sum(b["pct"] for b in stats["subject_breakdown"]) / len(stats["subject_breakdown"])) if stats["subject_breakdown"] else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Total Subjects",  len(subjects),           "Loaded")
    c2.metric("⏰ Study Hours",      f"{total_hours}h",       "Required")
    c3.metric("📅 Upcoming Exams",  len(upcoming_exams),     "In schedule")
    c4.metric("✅ Plan Coverage",   f"{overall_pct}%",       "Allocated")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Today's sessions ──
    today_tasks = get_today_sessions(schedule)
    if today_tasks:
        today_hours = sum(t.hours for t in today_tasks)
        pills = " ".join(subject_pill(t.subject_name, t.hours, t.color) for t in today_tasks)
        card(f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem">
            <div>
                <div style="font-weight:800;font-size:1rem;color:rgba(255,255,255,0.9);margin-bottom:0.5rem">
                    🔥 Today's Study Sessions
                </div>
                <div>{pills}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:1.8rem;font-weight:900;color:white">{today_hours}h</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.35)">{len(today_tasks)} sessions</div>
            </div>
        </div>
        """, border_color="rgba(99,102,241,0.35)", bg="rgba(99,102,241,0.08)")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.6])

    # ── Upcoming exams ──
    with col_left:
        st.markdown("##### 📅 Upcoming Exams")
        upcoming_sorted = sorted(upcoming_exams, key=lambda s: s.exam_date)
        for s in upcoming_sorted[:6]:
            days_left = (s.exam_date - date.today()).days
            if days_left <= 3:   urgency_color, urgency_label = "#ef4444", f"{days_left}d ⚠️"
            elif days_left <= 7: urgency_color, urgency_label = "#f59e0b", f"{days_left}d"
            else:                urgency_color, urgency_label = "#10b981", f"{days_left}d"

            card(f"""
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:10px;height:10px;border-radius:50%;background:{s.color};flex-shrink:0"></div>
                    <div>
                        <div style="font-weight:600;font-size:0.85rem;color:rgba(255,255,255,0.85)">{s.name}</div>
                        <div style="font-size:11px;color:rgba(255,255,255,0.35)">{s.exam_date}</div>
                    </div>
                </div>
                <span style="font-weight:700;font-size:0.85rem;color:{urgency_color}">{urgency_label}</span>
            </div>
            """)

    # ── Subject coverage ──
    with col_right:
        st.markdown("##### 🎯 Subject Coverage")
        for b in stats["subject_breakdown"]:
            pct_bar = f"""
            <div style="margin-bottom:0.85rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                    <div style="display:flex;align-items:center;gap:7px">
                        <div style="width:8px;height:8px;border-radius:50%;background:{b['color']}"></div>
                        <span style="font-size:0.82rem;font-weight:600;color:rgba(255,255,255,0.75)">{b['name']}</span>
                    </div>
                    <span style="font-size:0.78rem;color:rgba(255,255,255,0.38)">{b['scheduled']}h / {b['total']}h &nbsp; <b style="color:{b['color']}">{b['pct']}%</b></span>
                </div>
                <div style="height:6px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden">
                    <div style="height:100%;width:{b['pct']}%;background:{b['color']};border-radius:99px;
                        background:linear-gradient(90deg,{b['color']},{b['color']}aa)"></div>
                </div>
            </div>
            """
            st.markdown(pct_bar, unsafe_allow_html=True)

    # ── Warnings ──
    if warnings:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### ⚠️ Smart Warnings")
        for w in warnings:
            sev_color = "#ef4444" if w["severity"] == "high" else "#f59e0b"
            card(f"""
            <div style="display:flex;gap:10px;align-items:flex-start">
                <span style="font-size:1.1rem">⚠️</span>
                <span style="font-size:0.83rem;color:{sev_color};line-height:1.5">{w['message']}</span>
            </div>
            """, border_color=sev_color + "44", bg=sev_color + "11")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — STUDY PLAN
# ════════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("##### 📅 Day-by-Day Schedule")

    # Week selector
    sorted_dates  = sorted(schedule.keys())
    min_date      = sorted_dates[0]
    max_date      = sorted_dates[-1]
    total_weeks   = max(1, ((max_date - min_date).days // 7) + 1)

    week_n = st.select_slider(
        "Select Week",
        options=list(range(1, total_weeks + 2)),
        value=1,
        format_func=lambda w: f"Week {w}"
    )

    week_start = min_date + timedelta(weeks=week_n - 1)
    week_end   = week_start + timedelta(days=6)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    week_hours = sum(
        t.hours for d in week_dates for t in schedule.get(d, [])
    )
    st.markdown(f"""
    <p style="color:rgba(255,255,255,0.35);font-size:0.82rem;margin-bottom:1rem">
        📆 {week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')} &nbsp;·&nbsp;
        <b style="color:rgba(255,255,255,0.6)">{week_hours:.1f}h</b> this week
    </p>
    """, unsafe_allow_html=True)

    # Day rows
    for d in week_dates:
        tasks     = schedule.get(d, [])
        total_h   = sum(t.hours for t in tasks)
        is_today  = d == date.today()
        is_past   = d < date.today() and not is_today

        day_label = d.strftime("%A, %B %d")
        border    = "rgba(99,102,241,0.4)" if is_today else "rgba(255,255,255,0.06)"
        bg        = "rgba(99,102,241,0.07)" if is_today else "rgba(255,255,255,0.025)"
        opacity   = "0.45" if (is_past and not tasks) else "1"

        if tasks:
            pills = " ".join(
                f'<span style="background:{t.color}18;border:1px solid {t.color}30;color:{t.color};'
                f'border-radius:8px;padding:3px 10px;font-size:11px;font-weight:600;margin:2px;display:inline-block">'
                f'● {t.subject_name} · {t.hours}h</span>'
                for t in tasks
            )
            sessions_text = f'<div style="margin-top:6px">{pills}</div>'
        else:
            sessions_text = '<div style="font-size:11px;color:rgba(255,255,255,0.2);font-style:italic;margin-top:4px">Rest day</div>'

        today_tag = ' <span style="background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.4);color:#a5b4fc;border-radius:5px;padding:1px 7px;font-size:10px;font-weight:700;margin-left:6px">TODAY</span>' if is_today else ""
        done_tag  = ' <span style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);color:#34d399;border-radius:5px;padding:1px 7px;font-size:10px;font-weight:700;margin-left:4px">✓ Done</span>' if (is_past and tasks) else ""
        hours_tag = f'<span style="font-weight:800;color:rgba(255,255,255,0.7);float:right">{total_h:.1f}h</span>' if tasks else ""

        st.markdown(f"""
        <div style="opacity:{opacity};background:{bg};border:1px solid {border};border-radius:14px;
            padding:0.9rem 1.1rem;margin-bottom:0.5rem">
            <div style="font-weight:700;font-size:0.88rem;color:rgba(255,255,255,0.85)">
                {day_label}{today_tag}{done_tag}{hours_tag}
            </div>
            {sessions_text}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Full schedule dataframe ──
    st.markdown("##### 📋 Full Schedule Table")
    rows = []
    for d in sorted(schedule.keys()):
        for t in schedule[d]:
            rows.append({
                "Date":       d.isoformat(),
                "Day":        d.strftime("%A"),
                "Subject":    t.subject_name,
                "Hours":      t.hours,
                "Difficulty": t.difficulty,
            })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Export buttons ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📤 Export")
    exp_c1, exp_c2, exp_c3 = st.columns(3)

    with exp_c1:
        csv_bytes = export_csv(schedule, subjects)
        st.download_button(
            "📊 Download CSV",
            data=csv_bytes,
            file_name="study-timetable.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp_c2:
        pdf_bytes = export_pdf(schedule, subjects, config)
        st.download_button(
            "📄 Download PDF",
            data=pdf_bytes,
            file_name="study-plan.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with exp_c3:
        st.button("🖨️ Print Page", use_container_width=True,
                  help="Use Ctrl+P / Cmd+P to print")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS
# ════════════════════════════════════════════════════════════════════════════════
with tab3:

    breakdown = stats["subject_breakdown"]
    names     = [b["name"]      for b in breakdown]
    scheduled = [b["scheduled"] for b in breakdown]
    totals    = [b["total"]     for b in breakdown]
    colors    = [b["color"]     for b in breakdown]
    pcts      = [b["pct"]       for b in breakdown]

    # ── Summary strip ──
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("📚 Total Planned",    f"{sum(totals)}h")
    s2.metric("✅ Total Scheduled",  f"{sum(scheduled):.1f}h")
    s3.metric("📅 Study Days",       stats["total_days"])
    s4.metric("🎯 Avg Coverage",     f"{round(sum(pcts)/len(pcts))}%" if pcts else "0%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Pie + Bar ──
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### 🥧 Hour Distribution")
        fig_pie = go.Figure(data=[go.Pie(
            labels=names,
            values=scheduled,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
            textinfo="label+percent",
            textfont=dict(size=11, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value}h<extra></extra>",
        )])
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)", family="Inter"),
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("##### 📊 Planned vs Scheduled")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Planned",
            x=names, y=totals,
            marker=dict(color="rgba(99,102,241,0.25)", line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Planned: %{y}h<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            name="Scheduled",
            x=names, y=scheduled,
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Scheduled: %{y}h<extra></extra>",
        ))
        fig_bar.update_layout(
            barmode="group", bargap=0.3, bargroupgap=0.1,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.5)", family="Inter", size=11),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.6)")),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Weekly workload ──
    st.markdown("##### 📈 Weekly Study Workload")
    weekly_data = get_weekly_workload(schedule)
    if weekly_data:
        df_weekly = pd.DataFrame(weekly_data)
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=df_weekly["week"], y=df_weekly["hours"],
            name="Study Hours",
            fill="tozeroy",
            line=dict(color="#6366f1", width=2.5),
            fillcolor="rgba(99,102,241,0.12)",
            mode="lines+markers",
            marker=dict(size=6, color="#6366f1"),
            hovertemplate="<b>%{x}</b><br>Hours: %{y}h<extra></extra>",
        ))
        fig_area.add_trace(go.Scatter(
            x=df_weekly["week"], y=df_weekly["sessions"],
            name="Sessions",
            line=dict(color="#22d3ee", width=2, dash="dot"),
            mode="lines+markers",
            marker=dict(size=5, color="#22d3ee"),
            hovertemplate="<b>%{x}</b><br>Sessions: %{y}<extra></extra>",
        ))
        fig_area.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.5)", family="Inter", size=11),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.6)")),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
        )
        st.plotly_chart(fig_area, use_container_width=True)

    # ── Completion forecast ──
    st.markdown("##### 🎯 Completion Forecast")
    cols_per_row = 3
    rows_needed  = (len(breakdown) + cols_per_row - 1) // cols_per_row
    for row in range(rows_needed):
        cols = st.columns(cols_per_row)
        for col_i, col in enumerate(cols):
            idx = row * cols_per_row + col_i
            if idx >= len(breakdown):
                break
            b = breakdown[idx]
            with col:
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=b["pct"],
                    number=dict(suffix="%", font=dict(color=b["color"], size=28, family="Inter")),
                    title=dict(text=b["name"], font=dict(color="rgba(255,255,255,0.65)", size=12)),
                    gauge=dict(
                        axis=dict(range=[0,100], tickcolor="rgba(255,255,255,0.2)", tickwidth=1),
                        bar=dict(color=b["color"], thickness=0.6),
                        bgcolor="rgba(255,255,255,0.05)",
                        borderwidth=0,
                        steps=[dict(range=[0,100], color="rgba(255,255,255,0.04)")],
                    ),
                ))
                fig_g.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=180,
                    margin=dict(t=30, b=10, l=20, r=20),
                )
                st.plotly_chart(fig_g, use_container_width=True)
                st.markdown(f"""
                <p style="text-align:center;font-size:11px;color:rgba(255,255,255,0.3);margin-top:-1rem">
                    {b['scheduled']}h of {b['total']}h
                </p>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI INSIGHTS
# ════════════════════════════════════════════════════════════════════════════════
with tab4:

    focus_tips    = generate_focus_tips(subjects)
    revision_days = generate_revision_days(subjects)

    # ── Focus Tips ──
    st.markdown("##### 💡 AI Focus Suggestions")
    for tip in focus_tips:
        diff_colors = {"Easy":"#10b981","Medium":"#f59e0b","Hard":"#ef4444"}
        dc = diff_colors.get(tip["difficulty"], "#6366f1")
        tips_html = "".join(
            f'<li style="color:rgba(255,255,255,0.5);font-size:0.82rem;margin:5px 0;line-height:1.5">'
            f'<span style="color:{tip["color"]}">✓</span> {t}</li>'
            for t in tip["tips"]
        )
        card(f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">
            <div style="display:flex;align-items:center;gap:8px">
                <div style="width:10px;height:10px;border-radius:50%;background:{tip['color']};flex-shrink:0"></div>
                <span style="font-weight:700;font-size:0.9rem;color:rgba(255,255,255,0.85)">{tip['subject']}</span>
            </div>
            {badge(tip['difficulty'], dc)}
        </div>
        <ul style="margin:0;padding-left:0.5rem;list-style:none">{tips_html}</ul>
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revision Days ──
    st.markdown("##### 📖 Recommended Revision Days")
    rcols = st.columns(min(3, len(revision_days)))
    for i, r in enumerate(revision_days):
        with rcols[i % 3]:
            rev_pills = " ".join(
                f'<span style="background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);'
                f'color:#a78bfa;border-radius:7px;padding:3px 9px;font-size:11px;font-weight:600">{d}</span>'
                for d in r["revision_days"]
            )
            card(f"""
            <div style="display:flex;align-items:center;gap:7px;margin-bottom:0.5rem">
                <div style="width:8px;height:8px;border-radius:50%;background:{r['color']};flex-shrink:0"></div>
                <span style="font-weight:700;font-size:0.82rem;color:rgba(255,255,255,0.8)">{r['subject']}</span>
            </div>
            <div style="margin:4px 0">{rev_pills}</div>
            <div style="font-size:10px;color:rgba(255,255,255,0.28);margin-top:5px">Exam: {r['exam_date']}</div>
            """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Priority explanation ──
    st.markdown("##### 🧮 Algorithm Explanation")
    card(f"""
    <div style="font-weight:700;font-size:0.95rem;color:rgba(255,255,255,0.85);margin-bottom:0.8rem">
        Priority Formula
    </div>
    <div style="background:rgba(0,0,0,0.3);border-radius:10px;padding:0.8rem 1rem;font-family:monospace;
        font-size:0.9rem;color:#a5b4fc;margin-bottom:0.8rem">
        Priority = (Difficulty × 0.6) + (Urgency × 0.4)
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;margin-top:0.5rem">
        <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
            border-radius:10px;padding:0.6rem;text-align:center">
            <div style="font-weight:700;color:#34d399;font-size:1.1rem">1</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.5)">Easy</div>
        </div>
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);
            border-radius:10px;padding:0.6rem;text-align:center">
            <div style="font-weight:700;color:#fbbf24;font-size:1.1rem">2</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.5)">Medium</div>
        </div>
        <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);
            border-radius:10px;padding:0.6rem;text-align:center">
            <div style="font-weight:700;color:#f87171;font-size:1.1rem">3</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.5)">Hard</div>
        </div>
    </div>
    <p style="color:rgba(255,255,255,0.35);font-size:0.8rem;margin-top:0.8rem;line-height:1.5">
        Subjects with higher difficulty and closer exam dates are scheduled earlier each day.
        Urgency score is inversely proportional to days remaining (3 = 1 day left, 1 = 30+ days).
    </p>
    """)
