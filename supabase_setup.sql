-- ═══════════════════════════════════════════════════════════════════════════
-- Student Notes Hub — Supabase Setup Script
-- Run these statements in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Create the notes table
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.notes (
    id           uuid primary key default gen_random_uuid(),
    title        text not null,
    subject      text not null,
    description  text default '',
    file_url     text not null,
    storage_path text default '',
    file_type    text default 'PDF',
    file_size_kb numeric default 0,
    created_at   timestamptz default now()
);

-- 2. Enable Row Level Security
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.notes enable row level security;

-- 3. Public read policy (anyone can read notes)
-- ─────────────────────────────────────────────────────────────────────────────
create policy "Public read notes"
    on public.notes
    for select
    using (true);

-- 4. Public insert policy (anyone can upload a note)
-- ─────────────────────────────────────────────────────────────────────────────
create policy "Public insert notes"
    on public.notes
    for insert
    with check (true);

-- 5. Index for faster subject filtering
-- ─────────────────────────────────────────────────────────────────────────────
create index if not exists idx_notes_subject
    on public.notes (subject);

create index if not exists idx_notes_created_at
    on public.notes (created_at desc);

-- ─────────────────────────────────────────────────────────────────────────────
-- Storage Setup (do this in Supabase Dashboard → Storage)
-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Go to Storage in your Supabase dashboard
-- 2. Click "New Bucket"
-- 3. Name it exactly:  notes-files
-- 4. Check "Public bucket" → Save
--
-- Then add these storage policies (Storage → notes-files → Policies):
--
--   Policy 1 — Public read:
--     Operation : SELECT
--     Target    : authenticated, anon
--     Expression: true
--
--   Policy 2 — Public upload:
--     Operation : INSERT
--     Target    : authenticated, anon
--     Expression: (storage.foldername(name))[1] IN (
--                   'PSE','DSA','OS','DBMS','CN','OOP','TOC',
--                   'AI/ML','Web Dev','Mathematics','Physics','Chemistry','Other'
--                 )
--              AND octet_length(storage.foldername(name)) < 52428800  -- 50 MB
-- ─────────────────────────────────────────────────────────────────────────────

-- Verify setup
select count(*) as notes_count from public.notes;
