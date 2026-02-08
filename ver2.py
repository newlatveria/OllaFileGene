import os
from pathlib import Path
from textwrap import dedent

BASE_DIR = Path("masterstation")

STRUCTURE = {
    "config.py": None,
    "app.py": None,
    "core/shell.py": None,
    "core/gpu.py": None,
    "core/session.py": None,
    "core/security.py": None,
    "ui/chat.py": None,
    "ui/ide.py": None,
    "ui/factory.py": None,
    "ui/automation.py": None,
    "ui/security_tab.py": None,
    "ui/logs.py": None,
}

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def create_structure():
    for file in STRUCTURE:
        write_file(BASE_DIR / file, FILE_CONTENT[file])


FILE_CONTENT = {}

# ---------------- CONFIG ----------------

FILE_CONTENT["config.py"] = """
import os

WORKSPACE = "workspace"
ARCHIVE_DIR = os.path.join(WORKSPACE, ".archive")
LOG_DIR = os.path.join(WORKSPACE, "logs")
SESSION_FILE = "session_metadata.json"

REQUIRED_LIBS = ["psutil", "cpuinfo", "black", "pylint", "bandit"]

DANGEROUS_TOKENS = [
    "os.system",
    "subprocess",
    "rm -rf",
    "shutil.rmtree",
]

OLLAMA_DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
"""

# ---------------- SHELL ----------------

FILE_CONTENT["core/shell.py"] = """
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_shell(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        logger.info("Command executed: %s", cmd)
        return output
    except Exception as e:
        logger.exception("Shell execution failed")
        return str(e)
"""

# ---------------- GPU ----------------

FILE_CONTENT["core/gpu.py"] = """
import os

def get_gpu_stats():
    gpu = {"name": "Intel Arc A770", "vram_used": 0,
           "vram_total": 0, "detected": False, "error": ""}

    for card in ["card0", "card1", "card2"]:
        base = f"/sys/class/drm/{card}/device"
        try:
            if os.path.exists(f"{base}/mem_info_vram_total"):
                with open(f"{base}/mem_info_vram_total") as f:
                    gpu["vram_total"] = int(f.read().strip()) // (1024**2)
                with open(f"{base}/mem_info_vram_used") as f:
                    gpu["vram_used"] = int(f.read().strip()) // (1024**2)
                gpu["detected"] = True
                break
        except PermissionError:
            gpu["error"] = "Permission denied for GPU metrics."
    return gpu
"""

# ---------------- SECURITY ----------------

FILE_CONTENT["core/security.py"] = """
from config import DANGEROUS_TOKENS

def is_safe(code: str) -> bool:
    return not any(token in code for token in DANGEROUS_TOKENS)
"""

# ---------------- SESSION ----------------

FILE_CONTENT["core/session.py"] = """
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
"""

# ---------------- CHAT UI ----------------

FILE_CONTENT["ui/chat.py"] = """
import streamlit as st
import requests
from core.session import save_session

def render_chat(api_url, model_name, options):
    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Message AI..."):
        st.session_state["messages"].append(
            {"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": st.session_state["messages"],
            "options": options,
            "stream": False,
        }

        try:
            r = requests.post(f"{api_url}/api/chat", json=payload)
            r.raise_for_status()
            ans = r.json()["message"]["content"]
        except Exception as e:
            ans = f"Error: {e}"

        st.session_state["messages"].append(
            {"role": "assistant", "content": ans})
        save_session()
        st.rerun()
"""

# ---------------- IDE ----------------

FILE_CONTENT["ui/ide.py"] = """
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
"""

# ---------------- FACTORY ----------------

FILE_CONTENT["ui/factory.py"] = """
import streamlit as st
from core.shell import run_shell

def render_factory():
    model = st.text_input("Model to pull")
    if st.button("Download"):
        st.code(run_shell(["ollama", "pull", model]))
"""

# ---------------- AUTOMATION ----------------

FILE_CONTENT["ui/automation.py"] = """
import streamlit as st
import requests

def render_automation(api_url, model_name):
    task = st.text_input("Describe scheduled task")
    if st.button("Generate Cron"):
        r = requests.post(f"{api_url}/api/generate",
                          json={"model": model_name,
                                "prompt": f"Crontab line for: {task}",
                                "stream": False})
        st.code(r.json().get("response", ""))
"""

# ---------------- SECURITY TAB ----------------

FILE_CONTENT["ui/security_tab.py"] = """
import streamlit as st
from core.shell import run_shell
from config import WORKSPACE

def render_security():
    if st.button("Run Bandit"):
        st.code(run_shell(["bandit", "-r", WORKSPACE]))
"""

# ---------------- LOGS ----------------

FILE_CONTENT["ui/logs.py"] = """
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
"""

# ---------------- APP ----------------

FILE_CONTENT["app.py"] = """
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
"""

# ---------------- RUN ----------------

if __name__ == "__main__":
    create_structure()
    print("MasterStation project created successfully.")
