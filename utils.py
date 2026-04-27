"""
utils.py
--------
Shared constants and helper functions for Student Notes Hub (Supabase edition).
"""

from datetime import datetime, timezone


# ── Subject catalogue ──────────────────────────────────────────────────────────

SUBJECTS = [
    "PSE",
    "DSA",
    "OS",
    "DBMS",
    "CN",
    "OOP",
    "TOC",
    "AI/ML",
    "Web Dev",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Other",
]

# Warm, editorial palette — distinct from the Firebase version's dark theme
SUBJECT_COLORS = {
    "PSE":         "#e85d26",   # burnt orange
    "DSA":         "#2563eb",   # royal blue
    "OS":          "#059669",   # emerald
    "DBMS":        "#7c3aed",   # violet
    "CN":          "#db2777",   # rose
    "OOP":         "#d97706",   # amber
    "TOC":         "#dc2626",   # red
    "AI/ML":       "#0891b2",   # cyan
    "Web Dev":     "#65a30d",   # lime
    "Mathematics": "#4f46e5",   # indigo
    "Physics":     "#c2410c",   # orange-red
    "Chemistry":   "#7e22ce",   # purple
    "Other":       "#6b7280",   # gray
}

SUBJECT_ICONS = {
    "PSE":         "💡",
    "DSA":         "🌳",
    "OS":          "🖥️",
    "DBMS":        "🗄️",
    "CN":          "🌐",
    "OOP":         "🧩",
    "TOC":         "⚙️",
    "AI/ML":       "🤖",
    "Web Dev":     "🕸️",
    "Mathematics": "📐",
    "Physics":     "⚡",
    "Chemistry":   "🧪",
    "Other":       "📚",
}


def subject_color(subject: str) -> str:
    return SUBJECT_COLORS.get(subject, "#6b7280")


def subject_icon(subject: str) -> str:
    return SUBJECT_ICONS.get(subject, "📄")


# ── Client-side search (used when DB search isn't available) ───────────────────

def search_notes(notes: list[dict], query: str) -> list[dict]:
    """Case-insensitive substring search across title, subject, description."""
    if not query or not query.strip():
        return notes
    q = query.strip().lower()
    return [
        n for n in notes
        if q in n.get("title", "").lower()
        or q in n.get("subject", "").lower()
        or q in n.get("description", "").lower()
    ]


def filter_by_subject(notes: list[dict], subject: str) -> list[dict]:
    if subject == "All":
        return notes
    return [n for n in notes if n.get("subject") == subject]


# ── Formatting ─────────────────────────────────────────────────────────────────

def format_timestamp(raw) -> str:
    """Convert Supabase ISO timestamp string to human-friendly relative time."""
    if raw is None:
        return "Unknown"
    try:
        if isinstance(raw, str):
            # Supabase returns strings like "2024-03-10T14:22:01.123456+00:00"
            raw = raw.rstrip("Z")
            if "+" in raw:
                raw = raw.split("+")[0]
            dt = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
        else:
            dt = raw
        now = datetime.now(timezone.utc)
        delta = now - dt
        s = int(delta.total_seconds())
        if s < 60:    return "just now"
        if s < 3600:  return f"{s // 60}m ago"
        if s < 86400: return f"{s // 3600}h ago"
        if s < 604800: return f"{s // 86400}d ago"
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(raw)[:10]


def format_size(size_kb: float) -> str:
    if not size_kb:
        return ""
    if size_kb >= 1024:
        return f"{size_kb / 1024:.1f} MB"
    return f"{size_kb:.0f} KB"


def file_badge(file_type: str) -> str:
    return "📄" if file_type == "PDF" else "📊"
