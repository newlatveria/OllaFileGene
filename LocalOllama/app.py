import streamlit as st
import requests
import json
import subprocess
import os

# --- Constants & Safety Configurations ---
WORKSPACE = "workspace"
LOG_DIR = os.path.join(WORKSPACE, "logs")
DANGEROUS_TOKENS = ["rm -rf /", "sudo ", "chmod 777", "mkfs", "dd ", ":(){", "shutdown", "reboot"]

# Ensure filesystem structure
for p in [WORKSPACE, LOG_DIR]:
    if not os.path.exists(p): os.makedirs(p)

st.set_page_config(page_title="Ollama Secure OS Master", layout="wide")

# --- Sidebar: Global Model Controls ---
st.sidebar.title("🎮 Model Control Center")
model_name = st.sidebar.text_input("MODEL_NAME", value="security-bot")
api_url = st.sidebar.text_input("OLLAMA_API_URL", value="http://localhost:11434/api/generate")
temp = st.sidebar.slider("Temperature (Creativity)", 0.0, 1.0, 0.2)
num_ctx = st.sidebar.select_slider("Context Window", options=[2048, 4096, 8192, 16384], value=8192)

# --- Shared Logic ---
def run_shell(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=15)
        return res.stdout + res.stderr
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- UI Tabs ---
t_lab, t_docs, t_sec, t_auto, t_logs = st.tabs([
    "💻 Coding Lab", "📖 Documentation", "🛡️ Security & Git", "🕒 Automation", "📜 System Logs"
])

# --- TAB 1: CODING LAB (Create, Read, Write, Execute) ---
with t_lab:
    col_in, col_out = st.columns(2)
    with col_in:
        st.subheader("Input & Context")
        up_files = st.file_uploader("Upload Files for AI Analysis", accept_multiple_files=True)
        prompt_input = st.text_area("What should the AI build or fix?", height=200)
        
        if st.button("🚀 Generate Code"):
            # Inject file contents into context
            context = "".join([f"\nFILE: {f.name}\n{f.read().decode()}" for f in up_files]) if up_files else ""
            payload = {
                "model": model_name,
                "prompt": context + prompt_input,
                "stream": False,
                "options": {"temperature": temp, "num_ctx": num_ctx}
            }
            try:
                resp = requests.post(api_url, json=payload).json().get("response", "")
                st.session_state['code'] = resp
            except Exception as e:
                st.error(f"API Connection Failed: {e}")

    with col_out:
        st.subheader("Action Center")
        if 'code' in st.session_state:
            st.code(st.session_state['code'], language="python")
            fname = st.text_input("Save as (filename):", value="agent_script.py")
            
            c1, c2 = st.columns(2)
            if c1.button("💾 Save to Workspace"):
                with open(os.path.join(WORKSPACE, fname), "w") as f:
                    f.write(st.session_state['code'])
                st.success(f"File '{fname}' written to disk.")
            
            if c2.button("▶️ Execute Code"):
                # Security Filter Check
                if any(t in st.session_state['code'] for t in DANGEROUS_TOKENS):
                    st.error("SECURITY BLOCK: Dangerous tokens detected in code.")
                else:
                    st.info("Running script...")
                    output = run_shell(["python3", os.path.join(WORKSPACE, fname)])
                    st.text_area("Terminal Output:", value=output, height=200)

# --- TAB 2: DOCUMENTATION ---
with t_docs:
    st.subheader("Project README Generator")
    if st.button("📝 Auto-Generate Project Docs"):
        ws_files = [f for f in os.listdir(WORKSPACE) if os.path.isfile(os.path.join(WORKSPACE, f))]
        doc_prompt = f"Analyze these files and create a professional README.md: {', '.join(ws_files)}"
        res = requests.post(api_url, json={"model": model_name, "prompt": doc_prompt}).json().get("response", "")
        st.markdown(res)
        if st.button("💾 Save README"):
            with open(os.path.join(WORKSPACE, "README.md"), "w") as f: f.write(res)

# --- TAB 3: SECURITY & GIT ---
with t_sec:
    col_sec, col_git = st.columns(2)
    with col_sec:
        st.subheader("Bandit Vulnerability Scan")
        target = st.selectbox("Select file to scan:", os.listdir(WORKSPACE) if os.path.exists(WORKSPACE) else ["None"])
        if st.button("🔍 Run Security Audit"):
            report = run_shell(["venv/bin/bandit", "-r", os.path.join(WORKSPACE, target)])
            st.code(report, language="text")
    
    with col_git:
        st.subheader("Git Integration")
        commit_msg = st.text_input("Git Commit Message:", value="AI contribution")
        if st.button("🌿 Commit Workspace to AI-Branch"):
            run_shell(["git", "checkout", "-b", "ai-collaboration"])
            run_shell(["git", "add", "."])
            st.info(run_shell(["git", "commit", "-m", commit_msg]))

# --- TAB 4: AUTOMATION (Cron) ---
with t_auto:
    st.subheader("System Automation (Cron)")
    cron_req = st.text_input("Describe a recurring task:", placeholder="Run script.py every day at 4am")
    if st.button("📅 Draft Cron Job"):
        log_path = os.path.abspath(os.path.join(LOG_DIR, "automation.log"))
        c_prompt = f"Convert to crontab line: '{cron_req}'. Log output to >> {log_path} 2>&1"
        res = requests.post(api_url, json={"model": model_name, "prompt": c_prompt}).json().get("response", "")
        st.session_state['cron_draft'] = res.strip()
        st.code(res.strip(), language="bash")
    
    if st.button("✅ Install Schedule"):
        if 'cron_draft' in st.session_state:
            existing = run_shell(["crontab", "-l"])
            with open("cron.tmp", "w") as f: f.write(f"{existing}\n{st.session_state['cron_draft']}\n")
            subprocess.run(["crontab", "cron.tmp"])
            st.success("Crontab updated and active.")

# --- TAB 5: LOG MONITOR ---
with t_logs:
    st.subheader("Live System Logs")
    logs = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if logs:
        selected_log = st.selectbox("Select Log File:", logs)
        with open(os.path.join(LOG_DIR, selected_log), "r") as f:
            st.text_area("Log Content (Last 50 Lines)", value="".join(f.readlines()[-50:]), height=400)
        if st.button("🗑️ Wipe Selected Log"):
            open(os.path.join(LOG_DIR, selected_log), 'w').close()
            st.rerun()
    else:
        st.info("No logs detected. Ensure your Cron jobs are running and redirecting output.")