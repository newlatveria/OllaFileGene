import os
import streamlit as st
from config import LOG_DIR

def render_logs():
    if not os.path.exists(LOG_DIR):
        st.info("No logs yet.")
        return

    logs = os.listdir(LOG_DIR)
    if logs:
        selected = st.selectbox("Log file", logs)
        with open(os.path.join(LOG_DIR, selected)) as f:
            st.code(f.read())
