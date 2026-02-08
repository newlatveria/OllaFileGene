import logging
import streamlit as st
import psutil
import cpuinfo

from config import OLLAMA_DEFAULT_URL, DEFAULT_MODEL
from core.session import init_session
from core.gpu import get_gpu_stats
from ui.chat import render_chat
from ui.ide import render_ide
from ui.factory import render_factory
from ui.automation import render_automation
from ui.security_tab import render_security
from ui.logs import render_logs

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Ollama MasterStation", layout="wide")

init_session()

with st.sidebar:
    st.title("Station Control")
    gpu = get_gpu_stats()
    st.write(f"CPU: {psutil.cpu_percent()}%")
    st.write(cpuinfo.get_cpu_info()['brand_raw'])
    if gpu["detected"]:
        st.write("GPU detected")

api_url = OLLAMA_DEFAULT_URL
model_name = DEFAULT_MODEL

options = {
    "temperature": 0.7,
    "num_ctx": 8192,
}

tabs = st.tabs(["Chat", "IDE", "Factory", "Automation", "Security", "Logs"])

with tabs[0]:
    render_chat(api_url, model_name, options)

with tabs[1]:
    render_ide()

with tabs[2]:
    render_factory()

with tabs[3]:
    render_automation(api_url, model_name)

with tabs[4]:
    render_security()

with tabs[5]:
    render_logs()
