"""
app.py
Student Notes Hub — Clean Version (No Emojis + All Subjects)
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Student Notes Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from supabase_config import get_supabase_client
from storage import upload_file, validate_file
from database import (
    insert_note,
    get_all_notes,
)

# ── ALL SUBJECTS ─────────────────────────
SUBJECTS = [
    "Mathematics","Physics","Chemistry",
    "Programming in C","Python Programming","Java Programming",
    "Object Oriented Programming","Data Structures",
    "Design and Analysis of Algorithms",
    "Database Management Systems","Operating Systems",
    "Computer Networks","Software Engineering",
    "Compiler Design","Theory of Computation",
    "Artificial Intelligence","Machine Learning","Deep Learning",
    "Data Science","Cloud Computing","Cyber Security",
    "Distributed Systems","Web Development","Mobile App Development","DevOps",
    "Digital Logic Design","Microprocessors","Microcontrollers",
    "Basic Electrical Engineering","Basic Electronics",
    "Engineering Mechanics","Thermodynamics","Fluid Mechanics",
    "Strength of Materials","Linear Algebra","Probability and Statistics"
]

# ── SESSION ─────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Browse"

# ── SIDEBAR ─────────────────────────────
st.sidebar.title("Notes Hub")

if st.sidebar.button("Browse Notes"):
    st.session_state.page = "Browse"

if st.sidebar.button("Upload Note"):
    st.session_state.page = "Upload"

st.sidebar.markdown("---")

subject_filter = st.sidebar.selectbox(
    "Filter by Subject",
    ["All"] + SUBJECTS
)

# ── INIT ────────────────────────────────
client = get_supabase_client()

# ── UPLOAD PAGE ─────────────────────────
if st.session_state.page == "Upload":

    st.title("Upload Note")

    title = st.text_input("Title")
    subject = st.selectbox("Subject", SUBJECTS)
    description = st.text_area("Description")

    file = st.file_uploader("Upload PDF or PPT", type=["pdf", "ppt", "pptx"])

    if st.button("Upload"):
        if not title or not file:
            st.error("Title and file are required")
        else:
            valid, msg = validate_file(file)
            if not valid:
                st.error(msg)
            else:
                try:
                    file_info = upload_file(client, file, subject)

                    insert_note(client, {
                        "title": title,
                        "subject": subject,
                        "description": description,
                        "file_url": file_info["public_url"],
                        "file_size_kb": file_info["file_size_kb"],
                        "file_type": file_info["file_type"],
                        "storage_path": file_info["storage_path"]
                    })

                    st.success("Upload successful")

                except Exception as e:
                    st.error(f"Error: {e}")

# ── BROWSE PAGE ─────────────────────────
elif st.session_state.page == "Browse":

    st.title("Browse Notes")

    search = st.text_input("Search")

    notes = get_all_notes(client)

    if subject_filter != "All":
        notes = [n for n in notes if n["subject"] == subject_filter]

    if search:
        notes = [
            n for n in notes
            if search.lower() in n["title"].lower()
        ]

    if not notes:
        st.info("No notes available")
    else:
        cols = st.columns(3)

        for i, note in enumerate(notes):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border:1px solid #ddd;padding:15px;border-radius:8px;margin-bottom:15px;">
                    <div style="font-weight:600">{note['title']}</div>
                    <div>Subject: {note['subject']}</div>
                    <div>{note.get('description','')}</div>
                    <div>Size: {note.get('file_size_kb',0)} KB</div>
                    <br>
                    <a href="{note['file_url']}" target="_blank">View</a>
                </div>
                """, unsafe_allow_html=True)
