"""
storage.py
----------
All Supabase Storage operations for the Student Notes Hub.

Bucket : notes-files  (must be public in Supabase dashboard)
Path   : notes-files/<subject>/<uuid>_<filename>
"""

import uuid
import os
from supabase import Client

BUCKET = "notes-files"

# ── Allowed types ──────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}


def validate_file(uploaded_file) -> tuple[bool, str]:
    """
    Validate that the file is PDF or PPT/PPTX.
    Returns (is_valid, error_message).
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"❌ File type '{ext}' is not allowed. Please upload PDF or PPT/PPTX."
    return True, ""


def upload_file(client: Client, uploaded_file, subject: str) -> dict:
    """
    Upload a file to Supabase Storage and return metadata.
    """

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    unique_id = uuid.uuid4().hex[:10]
    safe_name = uploaded_file.name.replace(" ", "_")
    storage_path = f"{subject}/{unique_id}_{safe_name}"

    # Read file bytes
    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()

    # Content type
    content_type_map = {
        ".pdf":  "application/pdf",
        ".ppt":  "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    # Upload
    client.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "false"},
    )

    # Public URL
    public_url = client.storage.from_(BUCKET).get_public_url(storage_path)

    # ✅ FIXED: integer file size (no float error)
    file_size_kb = len(file_bytes) // 1024

    file_type = "PDF" if ext == ".pdf" else "PPT"

    return {
        "storage_path": storage_path,
        "public_url": public_url,
        "file_size_kb": file_size_kb,
        "file_type": file_type,
        "original_name": uploaded_file.name,
    }


def delete_file(client: Client, storage_path: str) -> bool:
    """Delete a file from the bucket."""
    try:
        client.storage.from_(BUCKET).remove([storage_path])
        return True
    except Exception:
        return False
