import streamlit as st
import requests
import json
import subprocess
import os
import re

# --- 1. CORE SYSTEM & SECURITY INITIALIZATION ---
WORKSPACE = "workspace"
LOG_DIR = os.path.join(WORKSPACE, "logs")
DANGEROUS_TOKENS = ["rm -rf /", "sudo ", "chmod 777", "mkfs", "dd ", ":(){", "shutdown", "reboot", "> /etc/"]
# Patterns to clean up "Token Soup" and training leaks
FORBIDDEN_PATTERNS = [r"<\|.*?\|>", r"fim_suffix", r"fim_middle", r"NSCoder", r"onBindViewHolder"]

for path in [WORKSPACE, LOG_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)

st.set_page_config(page_title="Ollama Master Workstation", layout="wide")

# --- 2. SESSION PERSISTENCE ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "latest_code" not in st.session_state:
    st.session_state["latest_code"] = ""
if "cron_draft" not in st.session_state:
    st.session_state["cron_draft"] = ""

# --- 3. HELPER LOGIC ---
def sanitize_output(text):
    for pattern in FORBIDDEN_PATTERNS:
        text = re.sub(pattern, "[CLEANED]", text)
    return text

def get_installed_models(base_url):
    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=2)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])], True
    except:
        return [], False
    return [], False

def run_shell(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=20)
        return res.stdout + res.stderr
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- 4. SIDEBAR: GLOBAL CONTROLS & MODEL SELECTION ---
with st.sidebar:
    st.title("🎮 System Controls")
    api_url = st.text_input("Ollama API URL", value="http://localhost:11434")
    
    models, is_online = get_installed_models(api_url)
    if is_online:
        st.success("🟢 Ollama Online")
        model_name = st.selectbox("Select Model", models)
    else:
        st.error("🔴 Ollama Offline")
        model_name = st.text_input("Model Name (Manual)", value="llama3")

    st.divider()
    st.subheader("⚙️ Hyperparameters")
    temp = st.slider("Temperature", 0.0, 1.0, 0.2)
    num_ctx = st.select_slider("Context Window", options=[2048, 4096, 8192, 16384, 32768], value=8192)
    
    st.divider()
    if st.button("🔥 HARD RESET SESSION", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# --- 5. TABBED INTERFACE ---
t_chat, t_factory, t_auto, t_sec_git, t_logs, t_help = st.tabs([
    "💬 Chat & Code", "🏭 Model Factory", "🕒 Automation", "🌿 Security & Git", "📜 Logs", "❓ Help Center"
])

# --- TAB 1: CHAT & CODE LAB (WITH PERSISTENT MEMORY) ---
with t_chat:
    col_chat, col_exec = st.columns([1, 1])
    
    with col_chat:
        st.subheader("Interactive Session (Context Aware)")
        
        # Display the chat history stored in session_state
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("Ask a follow-up question or start a new task..."):
            # 1. Store user message in memory
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                full_resp = ""
                
                # 2. Update to the CHAT endpoint for conversation memory
                chat_url = f"{api_url.rstrip('/')}/api/chat"
                
                # 3. Pass the ENTIRE messages list to Ollama
                payload = {
                    "model": model_name,
                    "messages": st.session_state["messages"],
                    "stream": True,
                    "options": {"temperature": temp, "num_ctx": num_ctx}
                }
                
                try:
                    r = requests.post(chat_url, json=payload, stream=True)
                    for line in r.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8'))
                            # Note: The 'chat' endpoint returns 'message' -> 'content'
                            chunk_content = chunk.get("message", {}).get("content", "")
                            content = sanitize_output(chunk_content)
                            full_resp += content
                            msg_placeholder.markdown(full_resp + "▌")
                    
                    msg_placeholder.markdown(full_resp)
                    
                    # 4. Store assistant response in memory
                    st.session_state["messages"].append({"role": "assistant", "content": full_resp})
                    
                    # 5. Extract Code to Workbench
                    if "```" in full_resp:
                        blocks = full_resp.split("```")
                        if len(blocks) > 1:
                            raw_code = blocks[1]
                            if raw_code.startswith("python"): raw_code = raw_code[6:]
                            elif raw_code.startswith("bash"): raw_code = raw_code[4:]
                            st.session_state["latest_code"] = raw_code.strip()
                            # Force a rerun to update the Code Editor in the right column
                            st.rerun()

                except Exception as e:
                    st.error(f"Memory Connection Error: {e}")

    with col_exec:
        st.subheader("⚡ Workbench")
        up_files = st.file_uploader("Context Files", accept_multiple_files=True)
        
        # This text area now updates automatically when the AI responds
        code_editor = st.text_area("Code Editor", value=st.session_state["latest_code"], height=350)
        st.session_state["latest_code"] = code_editor
        
        save_name = st.text_input("Save as:", value="generated_script.py")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("💾 Save"):
            with open(os.path.join(WORKSPACE, save_name), "w") as f: f.write(code_editor)
            st.success("Saved.")
        if c2.button("🔍 Scan"):
            st.text_area("Audit Report", value=run_shell(["venv/bin/bandit", "-r", os.path.join(WORKSPACE, save_name)]))
        if c3.button("▶️ Run"):
            if any(t in code_editor for t in DANGEROUS_TOKENS): st.error("Dangerous code blocked.")
            else: st.code(run_shell(["python3", os.path.join(WORKSPACE, save_name)]))
# --- TAB 2: MODEL FACTORY & EXPORTER ---
with t_factory:
    st.header("🏭 Personality Factory")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("Build Personality")
        m_b_name = st.text_input("Model Name (e.g., bash-expert)")
        m_base = st.selectbox("Base Model", models if is_online else ["llama3"])
        m_sys = st.text_area("System Prompt", "You are a Linux guru.")
        if st.button("🔨 Build"):
            with open("Modelfile", "w") as f: f.write(f"FROM {m_base}\nSYSTEM \"{m_sys}\"")
            st.info(run_shell(["ollama", "create", m_b_name, "-f", "Modelfile"]))
    with col_f2:
        st.subheader("Export Script")
        ex_name = st.selectbox("Model to Export", models if is_online else [])
        if st.button("📦 Create Installer"):
            sh_c = f"#!/bin/bash\nollama pull {m_base}\necho \"FROM {m_base}\nSYSTEM \\\"{m_sys}\\\"\" > Modelfile\nollama create {ex_name} -f Modelfile\nrm Modelfile"
            st.download_button("Download .sh", sh_c, file_name=f"install_{ex_name}.sh")

# --- TAB 3: AUTOMATION ---
with t_auto:
    st.header("🕒 Task Scheduler")
    cron_req = st.text_input("Cron Task Description")
    if st.button("Draft Cron"):
        log_p = os.path.abspath(os.path.join(LOG_DIR, "cron.log"))
        p = f"Convert to crontab: '{cron_req}'. Log to >> {log_p} 2>&1"
        res = requests.post(f"{api_url}/api/generate", json={"model": model_name, "prompt": p, "stream": False}).json()
        st.session_state['cron_draft'] = res.get("response", "").strip()
    if 'cron_draft' in st.session_state:
        st.code(st.session_state['cron_draft'])
        if st.button("✅ Activate"):
            exist = run_shell(["crontab", "-l"])
            with open("c.tmp", "w") as f: f.write(exist + "\n" + st.session_state['cron_draft'])
            subprocess.run(["crontab", "c.tmp"])
            st.success("Active.")

# --- TAB 4: SECURITY & GIT ---
with t_sec_git:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Git Control")
        branch = st.text_input("Branch", "ai-update")
        msg = st.text_input("Message", "Code update")
        if st.button("Push"):
            run_shell(["git", "checkout", "-b", branch])
            run_shell(["git", "add", "."])
            st.info(run_shell(["git", "commit", "-m", msg]))
    with col_g2:
        st.subheader("Full Scan")
        if st.button("Scan Workspace"): st.code(run_shell(["venv/bin/bandit", "-r", WORKSPACE]))

# --- TAB 5: LOGS ---
with t_logs:
    logs = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if logs:
        sel = st.selectbox("View Log", logs)
        with open(os.path.join(LOG_DIR, sel)) as f: st.code("".join(f.readlines()[-100:]))
    else: st.info("No logs.")

# --- TAB 6: HELP ---
with t_help:
    st.markdown("### Guide\n1. Use **Chat** to build code.\n2. **Save & Run** in Workbench.\n3. **Factory** for new models.\n4. **Reset** sidebar if soup occurs.")