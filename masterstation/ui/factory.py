import streamlit as st
from core.shell import run_shell

def render_factory():
    model = st.text_input("Model to pull")
    if st.button("Download"):
        st.code(run_shell(["ollama", "pull", model]))
