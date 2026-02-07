import streamlit as st
import requests
import json
import subprocess
import os
import sys
import time
from datetime import datetime

# --- 1. STARTUP & SELF-HEALING (INTEL ARC SUPPORT) ---
def startup_check():
    """Ensures dependencies are installed in the active VENV."""
    required = ["psutil", "py-cpuinfo", "black", "pylint", "bandit"]
    for lib in required:
        try:
            __import__(lib if lib != "py-cpuinfo" else "cpuinfo")
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

startup_check()
import psutil
import cpuinfo

# --- 2. INTEL ARC GPU MONITORING LOGIC ---
def get_gpu_stats():
    """Reads Intel Arc A770 metrics from Linux sysfs."""
    gpu = {"name": "Intel Arc A770", "vram_used": 0, "vram_total": 0, "detected": False}
    try:
        # Check if Intel DRM drivers are active
        if os.path.exists("/sys/class/drm/card0/device/mem_info_vram_total"):
            with open("/sys/class/drm/card0/device/mem_info_vram_total", "r") as f:
                gpu["vram_total"] = int(f.read()) // (1024**2)
            with open("/sys/class/drm/card0/device/mem_info_vram_used", "r") as f:
                gpu["vram_used"] = int(f.read()) // (1024**2)
            gpu["detected"] = True
        else:
            # Fallback check via lspci
            lspci = subprocess.check_output("lspci | grep -i 'VGA |Display'", shell=True).decode()
            if "Intel" in lspci:
                gpu["detected"] = True
    except:
        pass
    return gpu

# --- 3. CORE SETUP & PERSISTENCE ---
WORKSPACE = "workspace"
LOG_DIR = os.path.join(WORKSPACE, "logs")
ARCHIVE_DIR = os.path.join(WORKSPACE, ".archive")
SESSION_FILE = "session_metadata.json"
DANGEROUS_TOKENS = ["rm -rf /", "sudo ", "chmod 777", "mkfs", "dd ", ":(){", "shutdown", "> /etc/"]

for path in [WORKSPACE, LOG_DIR, ARCHIVE_DIR]:
    if not os.path.exists(path): os.makedirs(path)

st.set_page_config(page_title="Ollama MasterStation Pro", layout="wide", page_icon="🚀")

def save_session():
    data = {
        "messages": st.session_state.get("messages", []),
        "latest_code": st.session_state.get("latest_code", ""),
        "terminal_output": st.session_state.get("terminal_output", ""),
        "settings": {
            "temp": st.session_state.get("temp", 0.2),
            "num_ctx": st.session_state.get("num_ctx", 8192)
        }
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

# --- 4. STATE INITIALIZATION ---
if "init" not in st.session_state:
    saved = load_session()
    st.session_state["messages"] = saved.get("messages", [])
    st.session_state["latest_code"] = saved.get("latest_code", "")
    st.session_state["terminal_output"] = saved.get("terminal_output", "System Ready.")
    st.session_state["temp"] = saved.get("settings", {}).get("temp", 0.2)
    st.session_state["num_ctx"] = saved.get("settings", {}).get("num_ctx", 8192)
    st.session_state["editor_key"] = 0
    st.session_state["last_autosave"] = time.time()
    st.session_state["init"] = True

def run_shell(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        out = f"--- Result: {' '.join(cmd_list)} ---\n{res.stdout}{res.stderr}"
        st.session_state["terminal_output"] = out
        return out
    except Exception as e: return str(e)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Station Control")
    
    with st.expander("📊 Live Hardware (Intel Arc)", expanded=True):
        cpu_p = psutil.cpu_percent()
        ram_p = psutil.virtual_memory().percent
        st.write(f"**CPU:** {cpu_p}% | **RAM:** {ram_p}%")
        st.progress(cpu_p / 100)
        
        gpu = get_gpu_stats()
        if gpu["detected"]:
            st.divider()
            st.write(f"**GPU:** {gpu['name']}")
            if gpu["vram_total"] > 0:
                v_use = min(gpu["vram_used"] / gpu["vram_total"], 1.0)
                st.write(f"VRAM: {gpu['vram_used']}MB / {gpu['vram_total']}MB")
                st.progress(v_use)
        else:
            st.warning("Intel Arc A770 monitoring restricted.")

    st.divider()
    api_url = st.text_input("Ollama URL", value="http://localhost:11434")
    try:
        r = requests.get(f"{api_url}/api/tags", timeout=2)
        models = [m["name"] for m in r.json().get("models", [])]
        model_name = st.selectbox("Active Brain", models)
    except:
        model_name = st.text_input("Manual Model", "llama3")

    st.session_state["temp"] = st.slider("Temperature", 0.0, 1.0, st.session_state["temp"])
    st.session_state["num_ctx"] = st.select_slider("Context", [2048, 4096, 8192, 16384, 32768], st.session_state["num_ctx"])

# --- 6. TABS DEFINITION ---
t_chat, t_ide, t_history, t_sess, t_factory, t_auto, t_sec, t_logs = st.tabs([
    "💬 Chat", "🛠️ IDE", "📜 Versions", "💾 Session", "🏭 Factory", "🕒 Auto", "🛡️ Sec", "📑 Logs"
])

# --- TAB 1: CHAT ---
with t_chat:
    chat_up = st.file_uploader("📎 Context", accept_multiple_files=True)
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask for code..."):
        f_ctx = ""
        if chat_up:
            for f in chat_up: f_ctx += f"\nFILE: {f.name}\n{f.getvalue().decode('utf-8')}\n"
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            resp = st.empty(); full = ""
            payload = {"model": model_name, "messages": st.session_state["messages"][:-1] + [{"role": "user", "content": f"{f_ctx}\n{prompt}"}], "options": {"temperature": st.session_state["temp"], "num_ctx": st.session_state["num_ctx"]}, "stream": True}
            r = requests.post(f"{api_url}/api/chat", json=payload, stream=True)
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    content = chunk.get("message", {}).get("content", "")
                    full += content
                    resp.markdown(full + "▌")
            resp.markdown(full)
            st.session_state["messages"].append({"role": "assistant", "content": full})
            if "```" in full:
                st.session_state["latest_code"] = full.split("```")[1].split("\n", 1)[-1].split("```")[0]
                st.session_state["editor_key"] += 1
            save_session()

# --- TAB 2: IDE ---
with t_ide:
    files = sorted([f for f in os.listdir(WORKSPACE) if os.path.isfile(os.path.join(WORKSPACE, f))])
    sel_file = st.selectbox("📁 Project Files", ["(New)"] + files)
    
    if st.button("📖 Load"):
        with open(os.path.join(WORKSPACE, sel_file), "r") as f:
            st.session_state["latest_code"] = f.read()
            st.session_state["editor_key"] += 1; st.rerun()
            
    code = st.text_area("Source", value=st.session_state["latest_code"], height=300, key=f"ed_{st.session_state['editor_key']}")
    st.session_state["latest_code"] = code
    fname = st.text_input("Filename", value=sel_file if sel_file != "(New)" else "script.py")
    
    a1, a2, a3 = st.columns(3)
    if a1.button("💾 Save"):
        with open(os.path.join(WORKSPACE, fname), "w") as f: f.write(code)
        save_session(); st.toast("Saved!")
    if a2.button("✨ Format"):
        run_shell(["black", os.path.join(WORKSPACE, fname)]); st.rerun()
    if a3.button("▶️ Run"):
        if not any(t in code for t in DANGEROUS_TOKENS):
            run_shell(["python3", os.path.join(WORKSPACE, fname)]); st.rerun()

    st.code(st.session_state["terminal_output"])

# --- TAB 3: VERSIONS ---
with t_history:
    archived = sorted(os.listdir(ARCHIVE_DIR), reverse=True)
    if archived:
        v = st.selectbox("Backups", archived)
        with open(os.path.join(ARCHIVE_DIR, v)) as f: st.code(f.read())

# --- TAB 4: SESSION & SYSTEM MANAGER ---
with t_sess:
    st.header("💾 Session Command Center")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        if st.button("💾 Manual Save"): save_session(); st.success("Synced!")
        if st.button("🔥 Factory Reset", type="primary"):
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            st.session_state.clear(); st.rerun()
    with c_s2:
        if st.button("🛰️ Git Sync"): run_shell(["make", "git-sync"]); st.success("Pushed!")
        if st.button("♻️ Repair Intel Monitor"):
            subprocess.run(["sudo", "apt", "install", "-y", "intel-gpu-tools"])
            st.rerun()
    
    st.divider()
    st.subheader("📊 Telemetry")
    st.metric("Active Model", model_name)
    st.metric("GPU Detected", "Intel Arc A770" if gpu["detected"] else "No")

# --- TAB 5: FACTORY ---
with t_factory:
    st.subheader("🏭 Model Management")
    new_m = st.text_input("Pull Model (e.g., deepseek-coder)")
    if st.button("🚀 Download"):
        with st.status("Downloading..."): run_shell(["ollama", "pull", new_m])

# --- TAB 6: AUTOMATION ---
with t_auto:
    st.subheader("🕒 Cron Generator")
    c_p = st.text_input("Schedule Task Description")
    if st.button("🪄 Generate"):
        res = requests.post(f"{api_url}/api/generate", json={"model": model_name, "prompt": f"Crontab line for: {c_p}", "stream": False}).json()
        st.code(res.get("response", ""))

# --- TAB 7: SECURITY ---
with t_sec:
    if st.button("🔍 Scan for Vulnerabilities"):
        st.code(run_shell(["bandit", "-r", WORKSPACE]))

# --- TAB 8: LOGS ---
with t_logs:
    if st.button("🛠️ Diagnostic Check"):
        st.write(f"VENV Path: {sys.executable}")
        st.write(f"GPU Support: {gpu}")
    logs = os.listdir(LOG_DIR)
    if logs:
        s = st.selectbox("Logs", logs)
        with open(os.path.join(LOG_DIR, s)) as f: st.code(f.read())