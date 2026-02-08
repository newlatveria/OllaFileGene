import os
import streamlit as st
from config import WORKSPACE, ARCHIVE_DIR
from core.shell import run_shell
from core.security import is_safe

def render_ide():
    os.makedirs(WORKSPACE, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    files = sorted(os.listdir(WORKSPACE))
    selected = st.selectbox("File", ["(New)"] + files)

    code = st.text_area("Code",
                        value=st.session_state.get("latest_code", ""),
                        height=400)

    fname = st.text_input("Filename",
                          value=selected if selected != "(New)" else "script.py")

    if st.button("Save"):
        with open(os.path.join(WORKSPACE, fname), "w") as f:
            f.write(code)
        st.success("Saved")

    if st.button("Run"):
        if is_safe(code):
            output = run_shell(["python3",
                                os.path.join(WORKSPACE, fname)])
            st.code(output)
        else:
            st.error("Unsafe code detected.")
