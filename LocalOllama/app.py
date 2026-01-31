import streamlit as st
import requests
import json
import subprocess
import os
import shlex

# --- Configuration & Safety Settings ---
WORKSPACE = "workspace"
DANGEROUS_TOKENS = ["rm ", "sudo ", "chmod ", "mv /", "> /etc", "mkfs", ":(){", "dd ", "wget ", "curl "]

if not os.path.exists(WORKSPACE):
    os.makedirs(WORKSPACE)

st.set_page_config(page_title="Secure Ollama AI", layout="wide")

# --- Sidebar: Logic & Settings ---
st.sidebar.title("🛠️ Settings")
model_name = st.sidebar.text_input("Model", value="localmodel")
api_url = st.sidebar.text_input("Ollama API URL", value="http://localhost:11434/api/generate")
temp = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)

# --- Helper Functions ---

def is_safe(content):
    """Scan code for dangerous Linux commands."""
    for token in DANGEROUS_TOKENS:
        if token in content.lower():
            return False, token
    return True, None

def run_vulnerability_scan(filepath):
    """Uses 'bandit' to scan Python code for security flaws."""
    result = subprocess.run(["venv/bin/bandit", "-r", filepath], capture_output=True, text=True)
    return result.stdout

def git_manager(filename, msg):
    """Commits files to a dedicated AI branch."""
    try:
        subprocess.run(["git", "checkout", "-b", "ai-collaboration"], capture_output=True)
        subprocess.run(["git", "add", filename], capture_output=True)
        res = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
        return res.stdout if res.returncode == 0 else "No changes to commit or Git error."
    except Exception as e:
        return str(e)

# --- Main UI ---
st.title("🛡️ Secure Local AI Workstation")

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("Input & Context")
    uploaded_files = st.file_uploader("Attach Project Files", accept_multiple_files=True)
    user_query = st.text_area("What should the AI do?", height=200)
    
    if st.button("🚀 Generate Code"):
        context = ""
        if uploaded_files:
            for f in uploaded_files:
                context += f"\nFILE: {f.name}\n{f.read().decode('utf-8')}\n"
        
        payload = {
            "model": model_name,
            "prompt": f"{context}\n\nUser Request: {user_query}\n\nIMPORTANT: Provide ONLY the code code block.",
            "stream": True,
            "options": {"temperature": temp}
        }

        with st.spinner("AI is thinking..."):
            response_area = st.empty()
            full_text = ""
            resp = requests.post(api_url, json=payload, stream=True)
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    full_text += chunk.get("response", "")
                    response_area.markdown(f"```python\n{full_text}\n```")
            st.session_state['latest_code'] = full_text

# --- Output & Action Section ---
with col_out:
    st.subheader("Execution & Security")
    if 'latest_code' in st.session_state:
        code = st.session_state['latest_code']
        filename = st.text_input("Save as:", value="generated_script.py")
        
        # Action Buttons
        c1, c2, c3 = st.columns(3)
        
        if c1.button("💾 Save"):
            with open(os.path.join(WORKSPACE, filename), "w") as f:
                f.write(code)
            st.success(f"Saved to {WORKSPACE}/{filename}")

        if c2.button("🔍 Scan"):
            path = os.path.join(WORKSPACE, filename)
            if os.path.exists(path):
                report = run_vulnerability_scan(path)
                st.code(report, language="text")
            else:
                st.error("Save file first!")

        if c3.button("▶️ Run"):
            path = os.path.join(WORKSPACE, filename)
            safe, token = is_safe(code)
            if not safe:
                st.error(f"BLOCKED: Dangerous token '{token}' found!")
            else:
                res = subprocess.run(["python3", path], capture_output=True, text=True)
                st.text_area("Terminal Output:", value=res.stdout + res.stderr)

# --- Git Integration (Sidebar) ---
st.sidebar.divider()
st.sidebar.subheader("Version Control")
commit_msg = st.sidebar.text_input("Commit Msg", value="AI Update")
if st.sidebar.button("🌿 Commit to AI-Branch"):
    if 'latest_code' in st.session_state:
        path = os.path.join(WORKSPACE, filename)
        report = git_manager(path, commit_msg)
        st.sidebar.code(report)
