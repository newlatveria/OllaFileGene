import json
import os
import time
import streamlit as st
from config import SESSION_FILE

def init_session():
    if "initialized" in st.session_state:
        return

    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            saved = json.load(f)
    else:
        saved = {}

    st.session_state.update({
        "messages": saved.get("messages", []),
        "latest_code": saved.get("latest_code", ""),
        "terminal_output": "System Ready.",
        "autosave_enabled": False,
        "last_autosave": time.time(),
        "initialized": True
    })

def save_session():
    data = {
        "messages": st.session_state.get("messages", []),
        "latest_code": st.session_state.get("latest_code", ""),
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)
