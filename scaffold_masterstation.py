import os
from pathlib import Path

BASE_DIR = Path("masterstation")

FILES = {
    "config.py": """
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
""",

    "core/shell.py": """
import subprocess

def run_shell(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)
""",

    "core/gpu.py": """
import os

def get_gpu_stats():
    gpu = {"name": "Intel Arc A770", "vram_used": 0, "vram_total": 0, "detected": False, "error": ""}
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
            gpu["error"] = "Access Denied. Add user to render group."
    return gpu
""",

    "core/security.py": """
from config import DANGEROUS_TOKENS

def is_safe(code: str) -> bool:
    return not any(token in code for token in DANGEROUS_TOKENS)
""",

    "core/session.py": """
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
""",

    "ui/chat.py": """
import streamlit as st
import requests
from core.session import save_session

def render_chat(api_url, model_name, options):
    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Message AI..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})

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

        st.session_state["messages"].append({"role": "assistant", "content": ans})
        save_session()
        st.rerun()
""",

    "app.py": """
import streamlit as st
import psutil
import cpuinfo

from config import WORKSPACE, ARCHIVE_DIR, LOG_DIR
from core.session import init_session
from core.gpu import get_gpu_stats
from ui.chat import render_chat

st.set_page_config(page_title="Ollama MasterStation", layout="wide")

init_session()

with st.sidebar:
    st.title("Station Control")
    gpu = get_gpu_stats()
    st.write(f"CPU: {psutil.cpu_percent()}%")
    st.write(cpuinfo.get_cpu_info()["brand_raw"])
    st.write(gpu)

api_url = "http://localhost:11434"
model_name = "llama3"

options = {
    "temperature": 0.7,
    "num_ctx": 8192,
}

t_chat, = st.tabs(["Chat"])

with t_chat:
    render_chat(api_url, model_name, options)
"""
}

def create_structure():
    print("Creating project structure...")

    for path, content in FILES.items():
        full_path = BASE_DIR / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content.strip() + "\n")
        print(f"Created {full_path}")

    print("\nMasterStation scaffold complete.")

if __name__ == "__main__":
    create_structure()
