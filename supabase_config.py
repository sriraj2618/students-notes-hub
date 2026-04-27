"""
supabase_config.py
------------------
Supabase client initialization.
Credentials are read from Streamlit secrets or environment variables.
Replace SUPABASE_URL and SUPABASE_KEY with your actual values.
"""

import os
import streamlit as st
from supabase import create_client, Client

# ── Credential resolution order ───────────────────────────────────────────────
# 1. Streamlit secrets  (recommended for Cloud deployment)
# 2. Environment variables (local dev)
# 3. Placeholder strings  (will raise a clear error)

SUPABASE_URL: str = ""
SUPABASE_KEY: str = ""

def get_supabase_client() -> Client:
    """
    Return an authenticated Supabase client.
    Initialised once and cached in st.session_state to avoid repeated handshakes.
    """
    if "supabase_client" in st.session_state:
        return st.session_state["supabase_client"]

    url = _resolve("SUPABASE_URL", "supabase.url")
    key = _resolve("SUPABASE_KEY", "supabase.key")

    if not url or not key or url == "SUPABASE_URL":
        st.error(
            "⚠️ Supabase credentials missing. "
            "Set them in `.streamlit/secrets.toml` or as environment variables "
            "`SUPABASE_URL` and `SUPABASE_KEY`."
        )
        st.stop()

    client: Client = create_client(url, key)
    st.session_state["supabase_client"] = client
    return client


def _resolve(env_key: str, secret_path: str) -> str:
    """Try Streamlit secrets first, then environment variables."""
    try:
        # secret_path like "supabase.url" → st.secrets["supabase"]["url"]
        section, key = secret_path.split(".")
        return st.secrets[section][key]
    except (KeyError, AttributeError, Exception):
        pass
    return os.environ.get(env_key, "")
