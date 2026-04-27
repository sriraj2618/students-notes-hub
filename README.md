# 📖 Student Notes Hub — Supabase Edition

A production-quality academic notes platform built with **Streamlit** + **Supabase** (PostgreSQL + Storage).

---

## ✨ Features

| Feature | Details |
|---|---|
| **Upload** | PDF & PPT/PPTX with title, subject, description |
| **Browse** | Responsive 3-column card grid, newest-first |
| **Search** | Real-time client-side + server-side ilike search |
| **Filter** | Sidebar subject dropdown |
| **Analytics** | Per-subject bar chart, recent uploads |
| **Backend** | Supabase PostgreSQL + Storage (public bucket) |
| **Design** | Cream/ink editorial theme, Fraunces serif headings |

---

## 🗂 Project Structure

```
student_notes_hub_sb/
│
├── app.py               # Main Streamlit app — all pages, CSS, sidebar
├── supabase_config.py   # Supabase client initialisation
├── storage.py           # File upload + public URL generation
├── database.py          # PostgreSQL CRUD via PostgREST
├── utils.py             # Helpers: search, formatting, subjects
│
├── supabase_setup.sql   # Run once in Supabase SQL Editor
├── requirements.txt
└── .streamlit/
    └── secrets.toml.template
```

---

## 🚀 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Supabase Project Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste and run `supabase_setup.sql`
3. Go to **Storage** → create bucket **`notes-files`** (set as **Public**)
4. Copy your **Project URL** and **anon/public API key** from  
   **Settings → API**

### 3. Credentials

```bash
# Option A: Streamlit secrets (recommended)
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Fill in url and key

# Option B: Environment variables
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### 4. Run

```bash
streamlit run app.py
```

---

## 🌍 Deploy to Streamlit Cloud

1. Push to GitHub (exclude `secrets.toml`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. In **Advanced → Secrets**, paste:
   ```toml
   [supabase]
   url = "https://YOUR_PROJECT.supabase.co"
   key = "YOUR_ANON_KEY"
   ```
4. Deploy ✅

---

## 🔐 Supabase Storage Policies

In your Supabase dashboard → Storage → notes-files → Policies:

**Allow public read:**
```sql
true
```

**Allow public upload (INSERT):**
```sql
true
```

---

## 🎨 Design

| Token | Value |
|---|---|
| Font (headings) | Fraunces (serif) |
| Font (body) | DM Sans |
| Background | `#faf7f2` cream |
| Sidebar | `#1a1510` ink |
| Accent | `#c8401a` terracotta |
| Success | `#166534` forest |

---

## 📦 Subjects

PSE · DSA · OS · DBMS · CN · OOP · TOC · AI/ML · Web Dev · Mathematics · Physics · Chemistry · Other
