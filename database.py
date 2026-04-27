"""
database.py
-----------
All Supabase PostgreSQL (via PostgREST) operations for the notes table.

Table schema (run in Supabase SQL editor):

    create table public.notes (
        id          uuid primary key default gen_random_uuid(),
        title       text not null,
        subject     text not null,
        description text default '',
        file_url    text not null,
        storage_path text default '',
        file_type   text default 'PDF',
        file_size_kb numeric default 0,
        created_at  timestamptz default now()
    );

    -- Enable Row Level Security (RLS) and add a public-read policy:
    alter table public.notes enable row level security;
    create policy "Public read" on public.notes for select using (true);
    create policy "Public insert" on public.notes for insert with check (true);
"""

from supabase import Client

TABLE = "notes"


# ── Write ──────────────────────────────────────────────────────────────────────

def insert_note(client: Client, metadata: dict) -> dict:
    """
    Insert a note record into Supabase.
    Returns the inserted row as a dict.
    """
    response = (
        client.table(TABLE)
        .insert(metadata)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_note(client: Client, note_id: str) -> bool:
    """Delete a note by its UUID. Returns True on success."""
    try:
        client.table(TABLE).delete().eq("id", note_id).execute()
        return True
    except Exception:
        return False


# ── Read ───────────────────────────────────────────────────────────────────────

def get_all_notes(client: Client) -> list[dict]:
    """Fetch all notes ordered newest-first."""
    response = (
        client.table(TABLE)
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def get_notes_by_subject(client: Client, subject: str) -> list[dict]:
    """Fetch notes for a specific subject, newest-first."""
    response = (
        client.table(TABLE)
        .select("*")
        .eq("subject", subject)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def search_notes_db(client: Client, query: str) -> list[dict]:
    """
    Server-side case-insensitive search using PostgREST ilike.
    Searches title, subject, and description columns.
    Falls back to client-side filtering if the OR filter fails.
    """
    q = f"%{query}%"
    try:
        response = (
            client.table(TABLE)
            .select("*")
            .or_(f"title.ilike.{q},subject.ilike.{q},description.ilike.{q}")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception:
        # Fallback: fetch all and filter client-side
        all_notes = get_all_notes(client)
        ql = query.lower()
        return [
            n for n in all_notes
            if ql in n.get("title", "").lower()
            or ql in n.get("subject", "").lower()
            or ql in n.get("description", "").lower()
        ]


def get_subject_counts(client: Client) -> dict[str, int]:
    """Return a dict mapping subject → note count (computed client-side)."""
    notes = get_all_notes(client)
    counts: dict[str, int] = {}
    for note in notes:
        s = note.get("subject", "Other")
        counts[s] = counts.get(s, 0) + 1
    return counts
