import streamlit as st
import requests
import json
import subprocess
import os
import re

# --- 1. CORE SYSTEM & SECURITY INITIALIZATION ---
WORKSPACE = "workspace"
LOG_DIR = os.path.join(WORKSPACE, "logs")
# Security firewall for shell execution
DANGEROUS_TOKENS = ["rm -rf /", "sudo ", "chmod 777", "mkfs", "dd ", ":(){", "shutdown", "reboot", "> /etc/"]
# Regex to catch "Token Soup" leaks from LLM training data
FORBIDDEN_PATTERNS = [r"<\|.*?\|>", r"fim_suffix", r"fim_middle", r"NSCoder", r"onBindViewHolder"]

for path in [WORKSPACE, LOG_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)

st.set_page_config(page_title="Ollama Master Workstation", layout="wide")

# --- 2. SESSION PERSISTENCE (Memory) ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "latest_code" not in st.session_state:
    st.session_state["latest_code"] = ""
if "cron_draft" not in st.session_state:
    st.session_state["cron_draft"] = ""

# --- 3. HELPER FUNCTIONS ---
def sanitize_output(text):
    """Filters out LLM internal tokens to prevent UI corruption."""
    for pattern in FORBIDDEN_PATTERNS:
        text = re.sub(pattern, "[CLEANED]", text)
    return text

def get_installed_models(base_url):
    """Queries local Ollama API for available models."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=2)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])], True
    except:
        return [], False
    return [], False

def run_shell(cmd_list):
    """Executes local system commands and returns output."""
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        return res.stdout + res.stderr
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- 4. SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.title("🎮 System Controls")
    api_url = st.text_input("Ollama API URL", value="http://localhost:11434")
    
    models, is_online = get_installed_models(api_url)
    if is_online:
        st.success("🟢 Ollama Online")
        model_name = st.selectbox("Active Model", models)
    else:
        st.error("🔴 Ollama Offline")
        model_name = st.text_input("Model (Manual Entry)", value="llama3")

    st.divider()
    st.subheader("⚙️ Model Tuning")
    temp = st.slider("Temperature", 0.0, 1.0, 0.2)
    num_ctx = st.select_slider("Context Window", options=[2048, 4096, 8192, 16384, 32768], value=8192)
    
    st.divider()
    if st.button("🔥 HARD RESET SESSION", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# --- 5. THE TABBED WORKSPACE ---
t_chat, t_factory, t_auto, t_sec_git, t_logs, t_help = st.tabs([
    "💬 Chat & IDE", "🏭 Model Factory", "🕒 Automation", "🌿 Security & Git", "📜 Logs", "❓ Help"
])

# --- TAB 1: CHAT & IDE (CRUD ENABLED) ---
with t_chat:
    # GLOBAL FILE PICKER (Fixes NameError by defining at top level of Tab)
    up_files = st.file_uploader("📂 Select Files to Import (Opens OS File Picker)", accept_multiple_files=True)
    
    if up_files:
        for f in up_files:
            import_path = os.path.join(WORKSPACE, f.name)
            with open(import_path, "wb") as save_f:
                save_f.write(f.getbuffer())
        st.toast(f"Imported {len(up_files)} files to {WORKSPACE}", icon="📥")

    st.divider()
    
    col_chat, col_exec = st.columns([1, 1])
    
    # Left: The AI Conversation with Memory
    with col_chat:
        st.subheader("AI Assistant")
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask about code or files..."):
            # Context Injection from Files
            file_context = ""
            if up_files:
                for f in up_files:
                    file_context += f"\nFILE_NAME: {f.name}\nCONTENT:\n{f.getvalue().decode('utf-8')}\n"
            
            combined_prompt = f"{file_context}\nUSER REQUEST: {prompt}" if file_context else prompt
            st.session_state["messages"].append({"role": "user", "content": prompt})
            
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                full_resp = ""
                try:
                    chat_url = f"{api_url.rstrip('/')}/api/chat"
                    payload = {
                        "model": model_name,
                        "messages": st.session_state["messages"][:-1] + [{"role": "user", "content": combined_prompt}],
                        "stream": True,
                        "options": {"temperature": temp, "num_ctx": num_ctx}
                    }
                    r = requests.post(chat_url, json=payload, stream=True)
                    for line in r.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8'))
                            content = sanitize_output(chunk.get("message", {}).get("content", ""))
                            full_resp += content
                            msg_placeholder.markdown(full_resp + "▌")
                    msg_placeholder.markdown(full_resp)
                    st.session_state["messages"].append({"role": "assistant", "content": full_resp})
                    
                    # Code extraction to IDE
                    if "```" in full_resp:
                        st.session_state["latest_code"] = full_resp.split("```")[1].split("\n", 1)[-1]
                        st.rerun()
                except Exception as e:
                    st.error(f"API Error: {e}")

# Right Column: The IDE (Full CRUD)
    with col_exec:
        st.subheader("🛠️ IDE Workbench")
        
        # 1. DYNAMIC FILE SCANNER
        # We perform the scan right here to ensure 'files' is always fresh
        if not os.path.exists(WORKSPACE):
            os.makedirs(WORKSPACE)
            
        files = [f for f in os.listdir(WORKSPACE) if os.path.isfile(os.path.join(WORKSPACE, f))]
        
        c_nav, c_refresh = st.columns([3, 1])
        with c_nav:
            # We use an index-based selection to prevent the box from resetting unexpectedly
            selected_file = st.selectbox(
                "📁 Workspace Files", 
                ["New File"] + sorted(files),
                help="Select a file from the ./workspace folder to edit or delete."
            )
        with c_refresh:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        # 2. FILE LOADING LOGIC
        if selected_file != "New File":
            abs_p = os.path.abspath(os.path.join(WORKSPACE, selected_file))
            st.caption(f"📍 Path: `{abs_p}`")
            
            # CRUD: Read - Only load if the button is pressed to prevent overwriting unsaved work
            if st.button("📖 Load Content into Editor", use_container_width=True):
                try:
                    with open(os.path.join(WORKSPACE, selected_file), "r") as f:
                        st.session_state["latest_code"] = f.read()
                        st.toast(f"Loaded {selected_file}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error reading file: {e}")

        st.divider()

        # 3. THE EDITOR (CRUD: Update)
        # The key="main_editor" is crucial for Streamlit to track changes
        code_editor = st.text_area(
            "Source Code", 
            value=st.session_state["latest_code"], 
            height=400, 
            key="main_editor"
        )
        st.session_state["latest_code"] = code_editor
        
        # Smart filename suggestion
        default_name = selected_file if selected_file != "New File" else "script.py"
        save_name = st.text_input("📝 Target Filename:", value=default_name)
        
        # 4. CRUD & EXECUTION ACTION BAR
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("💾 Save", use_container_width=True):
            clean_name = os.path.basename(save_name)
            target_path = os.path.join(WORKSPACE, clean_name)
            with open(target_path, "w") as f:
                f.write(code_editor)
            st.toast(f"Saved {clean_name} to workspace!")
            # We do NOT rerun here so the user sees the toast, 
            # the next interaction will refresh the list.
            
        if b2.button("🔍 Audit", use_container_width=True):
            path = os.path.join(WORKSPACE, save_name)
            if os.path.exists(path):
                st.info(f"Auditing {save_name}...")
                st.code(run_shell(["venv/bin/bandit", "-r", path]))
            else:
                st.warning("Save file first.")

        if b3.button("▶️ Run", use_container_width=True):
            path = os.path.join(WORKSPACE, save_name)
            # Auto-save before running to ensure we execute the latest version
            with open(path, "w") as f: f.write(code_editor)
            
            if any(t in code_editor for t in DANGEROUS_TOKENS):
                st.error("Blocked: Dangerous system command detected.")
            else:
                st.code(run_shell(["python3", path]))

        if b4.button("🗑️ Delete", type="secondary", use_container_width=True):
            if selected_file != "New File":
                os.remove(os.path.join(WORKSPACE, selected_file))
                st.session_state["latest_code"] = "" # Clear editor
                st.warning(f"Deleted {selected_file}")
                st.rerun()

# --- TAB 2: MODEL FACTORY (BUILD & EXPORT) ---
with t_factory:
    st.header("🏭 Personality Factory")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("Build Personality")
        m_b_name = st.text_input("Custom Model Name")
        m_sys = st.text_area("System Instructions (Personality)")
        if st.button("🔨 Create Model"):
            with open("Modelfile", "w") as f: f.write(f"FROM {model_name}\nSYSTEM \"{m_sys}\"")
            st.info(run_shell(["ollama", "create", m_b_name, "-f", "Modelfile"]))
    with col_f2:
        st.subheader("Export Installer")
        ex_name = st.selectbox("Export Targets", models if is_online else [])
        if st.button("📦 Generate .sh Installer"):
            sh_content = f"#!/bin/bash\nollama pull {model_name}\necho \"FROM {model_name}\nSYSTEM \\\"{m_sys}\\\"\" > Modelfile\nollama create {ex_name} -f Modelfile"
            st.download_button("Download Installer", sh_content, file_name=f"install_{ex_name}.sh")

# --- TAB 3: AUTOMATION (CRON) ---
with t_auto:
    st.header("🕒 Task Scheduler")
    cron_req = st.text_input("Schedule (e.g., Run script.py every hour)")
    if st.button("📝 Draft Cron"):
        log_p = os.path.abspath(os.path.join(LOG_DIR, "automation.log"))
        p = f"Convert to crontab: '{cron_req}'. Log output to >> {log_p} 2>&1"
        res = requests.post(f"{api_url}/api/generate", json={"model": model_name, "prompt": p, "stream": False}).json()
        st.session_state['cron_draft'] = res.get("response", "").strip()
    
    if st.session_state['cron_draft']:
        st.code(st.session_state['cron_draft'], language="bash")
        if st.button("✅ Install to Crontab"):
            current = run_shell(["crontab", "-l"])
            with open("temp_cron", "w") as f: f.write(f"{current}\n{st.session_state['cron_draft']}\n")
            run_shell(["crontab", "temp_cron"])
            st.success("Crontab Updated.")

# --- TAB 4: SECURITY & GIT ---
with t_sec_git:
    st.header("🌿 Project Control")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Git Branching")
        g_branch = st.text_input("Branch Name", value="dev-ai")
        g_msg = st.text_input("Commit Message", value="AI generated update")
        if st.button("🚀 Push to Local Git"):
            run_shell(["git", "checkout", "-b", g_branch])
            run_shell(["git", "add", "."])
            st.info(run_shell(["git", "commit", "-m", g_msg]))
    with col_g2:
        st.subheader("Full Audit")
        if st.button("🔍 Scan All Workspace Files"):
            st.code(run_shell(["venv/bin/bandit", "-r", WORKSPACE]))

# --- TAB 5: LOGS ---
with t_logs:
    st.header("📜 System Logs")
    logs = [f for f in os.listdir(LOG_DIR)]
    if logs:
        s_log = st.selectbox("Select Log", logs)
        with open(os.path.join(LOG_DIR, s_log)) as f:
            st.code(f.read())
    else: st.info("No logs found.")

# --- TAB 6: HELP ---
with t_help:
    st.title("📖 Documentation")
    st.markdown("""
    * **Chat:** Conversational memory enabled. Attach files to give the AI context.
    * **IDE:** Full CRUD on `./workspace`. Absolute paths shown on load.
    * **Security:** Bandit scans Python code; the Firewall blocks destructive shell commands.
    * **Automation:** Natural language crontab generation.
    """)