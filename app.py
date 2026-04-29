"""
app.py
------
Student Notes Hub — Supabase Edition
Main Streamlit application entry point.
"""

import streamlit as st
from datetime import datetime

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Student Notes Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ──────────────────────────────────────────────────────────────
from supabase_config import get_supabase_client
from storage import upload_file, validate_file
from database import (
    insert_note,
    get_all_notes,
    get_notes_by_subject,
    search_notes_db,
    get_subject_counts,
)
from utils import (
    SUBJECTS,
    search_notes,
    filter_by_subject,
    format_timestamp,
    format_size,
    file_badge,
    subject_color,
    subject_icon,
)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  —  clean minimal style
# ══════════════════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Tokens ── */
        :root {
            --cream:   #fafafa;
            --paper:   #f4f4f5;
            --ink:     #18181b;
            --ink2:    #3f3f46;
            --muted:   #71717a;
            --border:  #e4e4e7;
            --accent:  #2563eb;
            --accent2: #16a34a;
            --surface: #ffffff;
            --radius:  10px;
            --shadow:  0 1px 8px rgba(0,0,0,0.06);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            background: var(--cream) !important;
            color: var(--ink) !important;
        }

        /* ── Chrome ── */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container {
            padding: 2rem 2.5rem 4rem !important;
            max-width: 1400px !important;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: var(--ink) !important;
            border-right: none !important;
        }
        [data-testid="stSidebar"] * { color: #f4f4f5 !important; }
        [data-testid="stSidebar"] .block-container { padding: 1.8rem 1.4rem !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }

        /* ── Sidebar selectbox ── */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: rgba(255,255,255,0.08) !important;
            border-color: rgba(255,255,255,0.2) !important;
            color: #f4f4f5 !important;
        }

        /* ── Main inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background: var(--surface) !important;
            border: 1.5px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--ink) !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
        }

        /* ── Primary button ── */
        .stButton > button {
            background: var(--ink) !important;
            color: var(--cream) !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background: var(--accent) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 14px rgba(37,99,235,0.2) !important;
        }

        /* ── File uploader ── */
        [data-testid="stFileUploader"] {
            background: var(--paper) !important;
            border: 2px dashed var(--border) !important;
            border-radius: var(--radius) !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent) !important;
        }

        /* ── Note card ── */
        .note-card {
            background: var(--surface);
            border: 1.5px solid var(--border);
            border-radius: var(--radius);
            padding: 1.3rem 1.2rem 1rem;
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .note-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.09);
        }
        .note-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 3px;
            background: var(--card-accent, #2563eb);
            border-radius: 0 0 var(--radius) var(--radius);
        }
        .card-eyebrow {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            margin-bottom: 0.5rem;
        }
        .subj-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            color: #fff;
        }
        .type-chip {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            padding: 2px 7px;
            border-radius: 4px;
            background: var(--paper);
            color: var(--muted);
            border: 1px solid var(--border);
        }
        .card-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--ink);
            line-height: 1.35;
            margin: 0.3rem 0;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .card-desc {
            font-size: 0.82rem;
            color: var(--muted);
            line-height: 1.55;
            margin-bottom: 0.8rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.5em;
        }
        .card-meta {
            font-size: 0.74rem;
            color: var(--muted);
            margin-bottom: 0.9rem;
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
        }
        .card-actions {
            display: flex;
            gap: 0.5rem;
        }
        .btn-view, .btn-dl {
            flex: 1;
            padding: 0.42rem 0;
            border-radius: 7px;
            font-size: 0.8rem;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            transition: all 0.15s ease;
            display: block;
        }
        .btn-view {
            background: var(--paper);
            color: var(--ink2);
            border: 1.5px solid var(--border);
        }
        .btn-view:hover { background: var(--ink); color: #fff; border-color: var(--ink); }
        .btn-dl {
            background: var(--accent);
            color: #fff;
            border: 1.5px solid var(--accent);
        }
        .btn-dl:hover { background: #1d4ed8; }

        /* ── Stat card ── */
        .stat-pill {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .stat-num {
            font-size: 1.9rem;
            font-weight: 700;
            color: #f4f4f5;
            line-height: 1;
        }
        .stat-label {
            font-size: 0.72rem;
            color: rgba(244,244,245,0.5);
            margin-top: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
        }

        /* ── Page header ── */
        .page-header { margin-bottom: 1.8rem; }
        .page-header h1 {
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
            color: var(--ink);
            line-height: 1.1;
        }
        .page-header p {
            color: var(--muted);
            margin: 0.4rem 0 0;
            font-size: 0.92rem;
        }

        /* ── Section divider ── */
        .sec-div {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1.5rem 0 1rem;
        }
        .sec-div span {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--ink2);
            white-space: nowrap;
        }
        .sec-line { flex: 1; height: 1px; background: var(--border); }

        /* ── Alert boxes ── */
        .box-success {
            background: #f0fdf4; border: 1.5px solid #86efac;
            border-radius: 8px; padding: 0.8rem 1rem;
            color: #166534; font-size: 0.88rem;
        }
        .box-error {
            background: #fff1f2; border: 1.5px solid #fca5a5;
            border-radius: 8px; padding: 0.8rem 1rem;
            color: #991b1b; font-size: 0.88rem;
        }
        .box-info {
            background: #eff6ff; border: 1.5px solid #93c5fd;
            border-radius: 8px; padding: 0.8rem 1rem;
            color: #1e40af; font-size: 0.88rem;
        }

        /* ── Nav buttons in sidebar ── */
        .nav-btn {
            display: block;
            width: 100%;
            padding: 0.55rem 0.9rem;
            margin-bottom: 0.3rem;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: rgba(244,244,245,0.7) !important;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            text-align: left;
            transition: background 0.15s ease;
        }
        .nav-btn.active {
            background: rgba(37,99,235,0.25) !important;
            color: #93c5fd !important;
            font-weight: 600 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--paper) !important;
            border-radius: 10px !important;
            border: 1.5px solid var(--border) !important;
            padding: 4px !important;
            gap: 3px !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--muted) !important;
            border-radius: 7px !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--ink) !important;
            color: var(--cream) !important;
        }

        /* ── Analytics bar ── */
        .bar-wrap {
            display: flex; align-items: center; gap: 0.8rem;
            margin-bottom: 0.6rem;
        }
        .bar-label {
            width: 100px; font-size: 0.82rem;
            font-weight: 500; flex-shrink: 0;
        }
        .bar-track {
            flex: 1; height: 26px;
            background: var(--paper);
            border-radius: 6px; overflow: hidden;
            border: 1px solid var(--border);
        }
        .bar-fill {
            height: 100%; border-radius: 6px;
            transition: width 0.5s ease;
        }
        .bar-count {
            width: 28px; text-align: right;
            font-size: 0.82rem; font-weight: 700;
            color: var(--ink2);
        }

        /* ── Empty state ── */
        .empty-state {
            text-align: center; padding: 3rem 1rem;
            color: var(--muted);
        }
        .empty-state h4 {
            color: var(--ink2); margin: 0 0 0.5rem;
            font-size: 1rem; font-weight: 600;
        }

        /* ── Upload form panel ── */
        .upload-panel {
            background: var(--surface);
            border: 1.5px solid var(--border);
            border-radius: var(--radius);
            padding: 1.8rem;
        }

        hr { border-color: var(--border) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        "page": "Browse",
        "search_query": "",
        "subject_filter": "All",
        "notes_cache": None,
        "cache_ts": None,
        "flash": None,        # ("success"|"error"|"info", message)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════

def load_notes(client, force=False) -> list[dict]:
    """Cache notes in session state for up to 60 seconds."""
    now = datetime.utcnow()
    stale = (
        st.session_state["notes_cache"] is None
        or st.session_state["cache_ts"] is None
        or (now - st.session_state["cache_ts"]).seconds > 60
        or force
    )
    if stale:
        st.session_state["notes_cache"] = get_all_notes(client)
        st.session_state["cache_ts"] = now
    return st.session_state["notes_cache"]


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(client):
    with st.sidebar:
        # Brand
        st.markdown(
            """
            <div style="text-align:center;padding:0.5rem 0 1.6rem">
                <div style="font-family:'Inter',sans-serif;font-size:1.3rem;
                            font-weight:700;color:#f4f4f5;margin-top:0.3rem">
                    Notes Hub
                </div>
                <div style="font-size:0.72rem;color:rgba(244,244,245,0.45);
                            letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem">
                    Student Edition
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation ──
        pages = {
            "Browse Notes": "Browse",
            "Upload Note":  "Upload",
            "Analytics":    "Analytics",
        }
        for label, key in pages.items():
            active_cls = "active" if st.session_state["page"] == key else ""
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Subject filter ──
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:600;color:rgba(244,244,245,0.4);"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem'>"
            "Filter by Subject</div>",
            unsafe_allow_html=True,
        )
        options = ["All"] + SUBJECTS
        sel = st.selectbox(
            "subject_sel",
            options,
            index=options.index(st.session_state["subject_filter"]),
            label_visibility="collapsed",
        )
        if sel != st.session_state["subject_filter"]:
            st.session_state["subject_filter"] = sel
            st.session_state["page"] = "Browse"
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Mini stats ──
        notes = st.session_state.get("notes_cache") or []
        subjects_present = len({n.get("subject") for n in notes if n.get("subject")})

        c1, c2 = st.columns(2)
        c1.markdown(
            f"<div class='stat-pill'><div class='stat-num'>{len(notes)}</div>"
            "<div class='stat-label'>Notes</div></div>",
            unsafe_allow_html=True,
        )
        c2.markdown(
            f"<div class='stat-pill'><div class='stat-num'>{subjects_present}</div>"
            "<div class='stat-label'>Subjects</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh", use_container_width=True):
            load_notes(client, force=True)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# NOTE CARD
# ══════════════════════════════════════════════════════════════════════════════

def note_card(note: dict):
    color = subject_color(note.get("subject", "Other"))
    title = note.get("title", "Untitled")
    desc  = note.get("description") or "No description provided."
    subj  = note.get("subject", "Other")
    ftype = note.get("file_type", "PDF")
    fsize = format_size(note.get("file_size_kb", 0))
    ts    = format_timestamp(note.get("created_at"))
    url   = note.get("file_url", "#")

    size_html = f"<span>{fsize}</span><span>·</span>" if fsize else ""

    st.markdown(
        f"""
        <div class="note-card" style="--card-accent:{color}">
            <div class="card-eyebrow">
                <span class="subj-badge" style="background:{color}">{subj}</span>
                <span class="type-chip">{ftype}</span>
            </div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
            <div class="card-meta">
                <span>{ts}</span>
                {size_html}
            </div>
            <div class="card-actions">
                <a href="{url}" target="_blank" class="btn-view">View</a>
                <a href="{url}" download class="btn-dl">Download</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# BROWSE PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_browse(client):
    st.markdown(
        """
        <div class="page-header">
            <h1>Browse Notes</h1>
            <p>Discover and download community-uploaded academic notes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Search ──
    query = st.text_input(
        "search",
        value=st.session_state["search_query"],
        placeholder="Search by title, subject, or keywords...",
        label_visibility="collapsed",
    )
    if query != st.session_state["search_query"]:
        st.session_state["search_query"] = query

    # ── Load & filter ──
    notes = load_notes(client)
    filtered = filter_by_subject(notes, st.session_state["subject_filter"])
    if query.strip():
        filtered = search_notes(filtered, query)

    # ── Result summary ──
    active_sub = st.session_state["subject_filter"]
    col_l, col_r = st.columns([6, 1])
    col_l.markdown(
        f"<div style='color:#71717a;font-size:0.85rem;padding-top:0.4rem'>"
        f"Showing <b style='color:#18181b'>{len(filtered)}</b> note(s)"
        + (f" in <b style='color:#18181b'>{active_sub}</b>" if active_sub != "All" else "")
        + (f" matching <b style='color:#18181b'>\"{query.strip()}\"</b>" if query.strip() else "")
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Empty state ──
    if not filtered:
        st.markdown(
            "<div class='empty-state'>"
            "<h4>No notes found</h4>"
            "<p>Try different search terms or upload the first note for this subject.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Grid ──
    COLS = 3
    for i in range(0, len(filtered), COLS):
        row_notes = filtered[i : i + COLS]
        cols = st.columns(COLS, gap="medium")
        for col, note in zip(cols, row_notes):
            with col:
                note_card(note)
        st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_upload(client):
    st.markdown(
        """
        <div class="page-header">
            <h1>Upload a Note</h1>
            <p>Share your academic notes with the community. PDF and PPT/PPTX only.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Flash message ──
    if st.session_state.get("flash"):
        kind, msg = st.session_state["flash"]
        cls = {"success": "box-success", "error": "box-error", "info": "box-info"}[kind]
        prefix = {"success": "Success:", "error": "Error:", "info": "Info:"}[kind]
        st.markdown(f"<div class='{cls}'>{prefix} {msg}</div>", unsafe_allow_html=True)
        st.session_state["flash"] = None
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Form ──
    with st.form("upload_form", clear_on_submit=True):
        st.markdown("<div class='upload-panel'>", unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 1])
        with col_a:
            title = st.text_input(
                "Title *",
                placeholder="e.g. Binary Trees — Complete Notes with Examples",
            )
        with col_b:
            subject = st.selectbox("Subject *", SUBJECTS)

        description = st.text_area(
            "Description (optional)",
            placeholder="What does this cover? Which exam or chapter is it relevant to?",
            height=90,
        )

        uploaded_file = st.file_uploader(
            "Attach File * (PDF or PPT/PPTX)",
            type=["pdf", "ppt", "pptx"],
            help="Max recommended: 50 MB",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Upload Note", use_container_width=True
        )

    if submitted:
        # ── Validation ──
        errors = []
        if not title.strip():
            errors.append("Note title is required.")
        if not uploaded_file:
            errors.append("Please attach a file.")
        else:
            ok, err = validate_file(uploaded_file)
            if not ok:
                errors.append(err)

        if errors:
            for e in errors:
                st.markdown(f"<div class='box-error'>Error: {e}</div>", unsafe_allow_html=True)
            return

        # ── Upload to Storage ──
        with st.spinner("Uploading file to Supabase Storage..."):
            try:
                file_info = upload_file(client, uploaded_file, subject)
            except Exception as exc:
                st.session_state["flash"] = ("error", f"Storage error: {exc}")
                st.rerun()
                return

        # ── Save metadata ──
        with st.spinner("Saving metadata to database..."):
            try:
                insert_note(
                    client,
                    {
                        "title":        title.strip(),
                        "subject":      subject,
                        "description":  description.strip(),
                        "file_url":     file_info["public_url"],
                        "storage_path": file_info["storage_path"],
                        "file_type":    file_info["file_type"],
                        "file_size_kb": file_info["file_size_kb"],
                    },
                )
            except Exception as exc:
                st.session_state["flash"] = ("error", f"Database error: {exc}")
                st.rerun()
                return

        load_notes(client, force=True)
        st.session_state["flash"] = (
            "success",
            f'"{title.strip()}" uploaded successfully under {subject}!',
        )
        st.session_state["page"] = "Upload"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_analytics(client):
    st.markdown(
        """
        <div class="page-header">
            <h1>Analytics</h1>
            <p>Distribution of notes across subjects and recent upload activity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    notes = load_notes(client)
    if not notes:
        st.markdown(
            "<div class='box-info'>No data yet — upload your first note to see analytics.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Top-level stats ──
    total = len(notes)
    subjects_present = len({n.get("subject") for n in notes})
    pdfs = sum(1 for n in notes if n.get("file_type") == "PDF")
    ppts = total - pdfs

    cols = st.columns(4)
    for col, num, label in [
        (cols[0], total,            "Total Notes"),
        (cols[1], subjects_present, "Active Subjects"),
        (cols[2], pdfs,             "PDF Files"),
        (cols[3], ppts,             "PPT Files"),
    ]:
        col.markdown(
            f"<div style='background:#fff;border:1.5px solid #e4e4e7;border-radius:10px;"
            f"padding:1rem 1.2rem;text-align:center'>"
            f"<div style='font-size:2rem;font-weight:700;"
            f"color:#2563eb;line-height:1'>{num}</div>"
            f"<div style='font-size:0.76rem;color:#71717a;margin-top:0.3rem;"
            f"text-transform:uppercase;letter-spacing:0.07em'>{label}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Per-subject breakdown ──
    from collections import Counter
    counts = Counter(n.get("subject", "Other") for n in notes)
    sorted_subs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    max_count = sorted_subs[0][1] if sorted_subs else 1

    st.markdown(
        "<div class='sec-div'><span>Notes per Subject</span><div class='sec-line'></div></div>",
        unsafe_allow_html=True,
    )

    for subj, count in sorted_subs:
        color = subject_color(subj)
        pct   = count / max_count * 100

        l_col, b_col, n_col = st.columns([2, 7, 1])
        l_col.markdown(
            f"<div style='padding-top:4px;font-size:0.85rem;font-weight:500'>{subj}</div>",
            unsafe_allow_html=True,
        )
        b_col.markdown(
            f"""
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        n_col.markdown(
            f"<div style='padding-top:4px;text-align:right;font-weight:700;"
            f"color:#18181b;font-size:0.88rem'>{count}</div>",
            unsafe_allow_html=True,
        )

    # ── Recent uploads ──
    st.markdown(
        "<div class='sec-div' style='margin-top:2rem'><span>Recent Uploads</span>"
        "<div class='sec-line'></div></div>",
        unsafe_allow_html=True,
    )

    for note in notes[:6]:
        color = subject_color(note.get("subject", "Other"))
        title = note.get("title", "Untitled")
        subj  = note.get("subject", "Other")
        ts    = format_timestamp(note.get("created_at"))
        fsize = format_size(note.get("file_size_kb", 0))

        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:1rem;padding:0.75rem 1rem;
                        background:#fff;border:1.5px solid #e4e4e7;border-radius:10px;
                        margin-bottom:0.5rem;border-left:4px solid {color}">
                <div style="flex:1;min-width:0">
                    <div style="font-weight:600;white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;font-size:0.9rem">{title}</div>
                    <div style="font-size:0.76rem;color:#71717a">{subj} · {fsize}</div>
                </div>
                <div style="font-size:0.76rem;color:#71717a;white-space:nowrap">{ts}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    inject_css()
    init_session()

    client = get_supabase_client()

    # Pre-warm cache on first load
    if st.session_state["notes_cache"] is None:
        load_notes(client)

    render_sidebar(client)

    page = st.session_state["page"]
    if page == "Browse":
        render_browse(client)
    elif page == "Upload":
        render_upload(client)
    elif page == "Analytics":
        render_analytics(client)


if __name__ == "__main__":
    main()
