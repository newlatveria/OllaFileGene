import streamlit as st
from core.shell import run_shell
from config import WORKSPACE

def render_security():
    if st.button("Run Bandit"):
        st.code(run_shell(["bandit", "-r", WORKSPACE]))
