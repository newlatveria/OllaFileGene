import streamlit as st
import requests
import json
import subprocess
import os
import re
from datetime import datetime
import time

# --- 1. CORE SETUP & PERSISTENCE ---
WORKSPACE = "workspace"
LOG_DIR = os.path.join(WORKSPACE, "logs")
ARCHIVE_DIR = os.path.join(WORKSPACE, ".archive")
SESSION_FILE = "session_metadata.json"
DANGEROUS_TOKENS = ["rm -rf /", "sudo ", "chmod 777", "mkfs", "dd ", ":(){", "shutdown", "reboot", "> /etc/"]

for path in [WORKSPACE, LOG_DIR, ARCHIVE_DIR]:
    if not os.path.exists(path): os.makedirs(path)

st.set_page_config(page_title="Ollama MasterStation Pro", layout="wide", page_icon="🚀")

# --- 2. PERSISTENCE ENGINE ---
def save_session():
    data = {
        "messages": st.session_state.get("messages", []),
        "latest_code": st.session_state.get("latest_code", ""),
        "terminal_output": st.session_state.get("terminal_output", ""),
        "cron_draft": st.session_state.get("cron_draft", "")
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

# --- 3. STATE INITIALIZATION ---
saved_data = load_session()
if "messages" not in st.session_state: st.session_state["messages"] = saved_data.get("messages", [])
if "latest_code" not in st.session_state: st.session_state["latest_code"] = saved_data.get("latest_code", "")
if "terminal_output" not in st.session_state: st.session_state["terminal_output"] = saved_data.get("terminal_output", "System Ready.")
if "cron_draft" not in st.session_state: st.session_state["cron_draft"] = saved_data.get("cron_draft", "")
if "editor_key" not in st.session_state: st.session_state["editor_key"] = 0
if "last_autosave" not in st.session_state: st.session_state["last_autosave"] = time.time()

# --- 4. UTILITIES ---
def run_shell(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        out = res.stdout + res.stderr
        st.session_state["terminal_output"] = out
        save_session()
        return out
    except Exception as e: return str(e)

def create_version(filename, content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    v_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{filename}")
    with open(v_path, "w") as f: f.write(content)

# --- 5. SIDEBAR (NEW CONTROLS ADDED) ---
with st.sidebar:
    st.title("🛡️ Station Control")
    api_url = st.text_input("Ollama API URL", value="http://localhost:11434")
    
    try:
        r = requests.get(f"{api_url.rstrip('/')}/api/tags", timeout=2)
        models = [m["name"] for m in r.json().get("models", [])]
        model_name = st.selectbox("Active Model", models)
        st.success("🟢 Online")
    except:
        model_name = st.text_input("Model (Manual)", value="llama3")
        st.error("🔴 Offline")

    st.divider()
    st.subheader("🧠 LLM Hyperparameters")
    temp = st.slider("Temperature", 0.0, 1.0, 0.2, help="Higher = more creative, lower = more factual.")
    num_ctx = st.select_slider("Context Length (Tokens)", options=[2048, 4096, 8192, 16384, 32768], value=8192)
    
    with st.expander("Advanced Tuning"):
        top_p = st.slider("Top P", 0.0, 1.0, 0.9)
        top_k = st.slider("Top K", 0, 100, 40)
        repeat_penalty = st.slider("Repeat Penalty", 1.0, 2.0, 1.1)

    st.divider()
    autosave_enabled = st.toggle("Enable Auto-Save (30s)", value=True)
    
    if st.button("🔥 PURGE SESSION", type="primary", use_container_width=True):
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        st.session_state.clear()
        st.rerun()

# --- 6. TABS ---
t_chat, t_ide, t_history, t_factory, t_auto, t_sec, t_logs = st.tabs([
    "💬 Chat", "🛠️ IDE", "📜 Versions", "🏭 Factory", "🕒 Automation", "🌿 Security", "📑 Logs"
])

# --- TAB 1: SMART CHAT ---
with t_chat:
    if st.button("🗑️ Clear Chat History"):
        st.session_state["messages"] = []
        save_session()
        st.rerun()

    chat_up = st.file_uploader("📎 Upload Context", accept_multiple_files=True)
    
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Prompt the workstation..."):
        file_ctx = ""
        if chat_up:
            for f in chat_up: file_ctx += f"\nFILE: {f.name}\n{f.getvalue().decode('utf-8')}\n"
        
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            resp_box = st.empty(); full_r = ""
            payload = {
                "model": model_name,
                "messages": st.session_state["messages"][:-1] + [{"role": "user", "content": f"{file_ctx}\n{prompt}"}],
                "options": {
                    "temperature": temp,
                    "num_ctx": num_ctx,
                    "top_p": top_p,
                    "top_k": top_k,
                    "repeat_penalty": repeat_penalty
                },
                "stream": True
            }
            r = requests.post(f"{api_url}/api/chat", json=payload, stream=True)
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    content = chunk.get("message", {}).get("content", "")
                    full_r += content
                    resp_box.markdown(full_r + "▌")
            resp_box.markdown(full_r)
            st.session_state["messages"].append({"role": "assistant", "content": full_r})
            if "```" in full_r:
                st.session_state["latest_code"] = full_r.split("```")[1].split("\n", 1)[-1].split("```")[0]
                st.session_state["editor_key"] += 1
            save_session()

# --- TAB 2: IDE ---
with t_ide:
    files = sorted([f for f in os.listdir(WORKSPACE) if os.path.isfile(os.path.join(WORKSPACE, f))])
    c1, c2, c3 = st.columns([2,1,1])
    with c1: sel_file = st.selectbox("📁 Project Files", ["(New File)"] + files)
    with c2: 
        if st.button("📖 Load") and sel_file != "(New File)":
            with open(os.path.join(WORKSPACE, sel_file), "r") as f:
                st.session_state["latest_code"] = f.read()
                st.session_state["editor_key"] += 1
                st.rerun()
    with c3:
        if st.button("🗑️ Delete", type="secondary") and sel_file != "(New File)":
            os.remove(os.path.join(WORKSPACE, sel_file)); st.rerun()
    
    code = st.text_area("Editor", value=st.session_state["latest_code"], height=400, key=f"ed_{st.session_state['editor_key']}")
    st.session_state["latest_code"] = code
    fname = st.text_input("Filename", value=sel_file if sel_file != "(New File)" else "script.py")

    if autosave_enabled and (time.time() - st.session_state["last_autosave"] > 30):
        with open(os.path.join(WORKSPACE, fname), "w") as f: f.write(code)
        st.session_state["last_autosave"] = time.time()
        st.toast("Auto-saved")

    b1, b2, b3 = st.columns(3)
    if b1.button("💾 Save & Version"):
        create_version(fname, code)
        with open(os.path.join(WORKSPACE, fname), "w") as f: f.write(code)
        save_session(); st.toast("Saved & Backed up!")
    if b2.button("🔍 Security Audit"):
        run_shell(["venv/bin/bandit", "-r", os.path.join(WORKSPACE, fname)]); st.rerun()
    if b3.button("▶️ Run Python"):
        if not any(t in code for t in DANGEROUS_TOKENS):
            with open(os.path.join(WORKSPACE, fname), "w") as f: f.write(code)
            run_shell(["python3", os.path.join(WORKSPACE, fname)])
            st.rerun()
        else: st.error("Destructive Command Blocked")

    st.caption("📟 Console Output")
    st.code(st.session_state["terminal_output"])

# --- TAB 3: VERSIONS ---
with t_history:
    st.subheader("Version Restore")
    archived = sorted(os.listdir(ARCHIVE_DIR), reverse=True)
    if archived:
        v_sel = st.selectbox("Backups", archived)
        with open(os.path.join(ARCHIVE_DIR, v_sel), "r") as f: v_content = f.read()
        st.code(v_content)
        if st.button("♻️ Restore"):
            st.session_state["latest_code"] = v_content
            st.session_state["editor_key"] += 1
            st.rerun()

# --- TAB 4: FACTORY ---
with t_factory:
    st.header("🏭 Personality Factory")
    m_name = st.text_input("Model Name")
    m_sys = st.text_area("System Instructions")
    if st.button("🔨 Build"):
        with open("Modelfile", "w") as f: f.write(f"FROM {model_name}\nSYSTEM \"{m_sys}\"")
        st.info(run_shell(["ollama", "create", m_name, "-f", "Modelfile"]))

# --- TAB 5: AUTOMATION ---
with t_auto:
    st.header("🕒 Cron Generator")
    c_p = st.text_input("Schedule Request", value=st.session_state["cron_draft"])
    if st.button("Generate"):
        res = requests.post(f"{api_url}/api/generate", json={"model": model_name, "prompt": f"Crontab for: {c_p}", "stream": False}).json()
        st.session_state["cron_draft"] = res.get("response", "")
        save_session(); st.rerun()
    st.code(st.session_state["cron_draft"])

# --- TAB 6: SECURITY ---
with t_sec:
    if st.button("Scan Project"): st.code(run_shell(["venv/bin/bandit", "-r", WORKSPACE]))

# --- TAB 7: LOGS ---
with t_logs:
    logs = os.listdir(LOG_DIR)
    if logs:
        s_log = st.selectbox("Log File", logs)
        with open(os.path.join(LOG_DIR, s_log)) as f: st.code(f.read())