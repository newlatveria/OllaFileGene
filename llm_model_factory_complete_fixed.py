"""
Secure LLM Model Factory - Complete Edition (Fixed)
Version: 3.6.0
All issues resolved: Input clearing, Intel GPU, compact metrics, common file types, persona
"""

import streamlit as st
import requests
import json
import subprocess
import os
import hashlib
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

class SecurityLevel(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

# Predefined personas
PERSONAS = {
    "Default Assistant": "You are a helpful AI assistant.",
    "Expert Programmer": "You are an expert programmer. Provide clean, well-documented code with best practices. Always include error handling and explanations.",
    "Research Assistant": "You are a research assistant. Provide detailed, well-structured responses with clear reasoning. When using documents, cite sources.",
    "Creative Writer": "You are a creative writer. Use vivid language, engaging narratives, and imaginative descriptions. Be expressive and original.",
    "Technical Educator": "You are a technical educator. Explain complex concepts clearly with examples and analogies. Break down information step-by-step.",
    "Business Consultant": "You are a business consultant. Provide strategic insights, data-driven recommendations, and practical solutions.",
    "Debugging Expert": "You are a debugging expert. Analyze code systematically, identify issues, and suggest fixes with clear explanations.",
    "Custom": ""
}

@dataclass
class SecurityConfig:
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = None
    
    def __post_init__(self):
        if self.ALLOWED_FILE_EXTENSIONS is None:
            self.ALLOWED_FILE_EXTENSIONS = [
                '.py', '.txt', '.md', '.json', '.yaml', '.yml',
                '.pdf', '.docx', '.doc', '.csv', '.tsv', '.xml'
            ]

SECURITY_CONFIG = SecurityConfig()

# Paths
BASE_DIR = Path(__file__).parent
WORKSPACE = BASE_DIR / "workspace"
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
CHAT_HISTORY_DIR = CONFIG_DIR / "chat_history"
RAG_DOCS_DIR = CONFIG_DIR / "rag_documents"

for directory in [WORKSPACE, LOG_DIR, CONFIG_DIR, CHAT_HISTORY_DIR, RAG_DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

AUDIT_LOG = LOG_DIR / "audit.log"
USERS_DB = CONFIG_DIR / "users.json"

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def audit_log(user: str, action: str, details: str, success: bool = True):
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILURE"
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{timestamp} | {user} | {action} | {status} | {details}\n")

# ============================================================================
# HARDWARE MONITORING
# ============================================================================

class HardwareMonitor:
    @staticmethod
    def get_cpu_usage() -> Dict:
        if not PSUTIL_AVAILABLE:
            return {"available": False}
        return {
            "available": True,
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count()
        }
    
    @staticmethod
    def get_memory_usage() -> Dict:
        if not PSUTIL_AVAILABLE:
            return {"available": False}
        mem = psutil.virtual_memory()
        return {
            "available": True,
            "percent": mem.percent,
            "used_gb": mem.used / (1024**3),
            "total_gb": mem.total / (1024**3)
        }
    
    @staticmethod
    def get_disk_usage() -> Dict:
        if not PSUTIL_AVAILABLE:
            return {"available": False}
        disk = psutil.disk_usage('/')
        return {
            "available": True,
            "percent": disk.percent,
            "free_gb": disk.free / (1024**3),
            "total_gb": disk.total / (1024**3)
        }
    
    @staticmethod
    def get_gpu_info() -> Dict:
        """Get GPU info for both NVIDIA and Intel"""
        gpus = []
        
        # Try NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        gpus.append({
                            "name": parts[0],
                            "type": "NVIDIA",
                            "vram_total": int(parts[1]),
                            "vram_used": int(parts[2]),
                            "temp": int(parts[3]),
                            "usage": int(parts[4])
                        })
        except:
            pass
        
        # Try Intel (Linux)
        try:
            if os.path.exists("/sys/class/drm/card0/device/"):
                # Check for Intel GPU
                vendor_path = "/sys/class/drm/card0/device/vendor"
                if os.path.exists(vendor_path):
                    with open(vendor_path, 'r') as f:
                        vendor = f.read().strip()
                    if vendor == "0x8086":  # Intel vendor ID
                        # Try to get GPU name
                        gpu_name = "Intel GPU"
                        try:
                            result = subprocess.run(
                                ["lspci"], capture_output=True, text=True, timeout=2
                            )
                            for line in result.stdout.split('\n'):
                                if 'VGA' in line and 'Intel' in line:
                                    gpu_name = line.split(':')[-1].strip()
                                    break
                        except:
                            pass
                        
                        gpus.append({
                            "name": gpu_name,
                            "type": "Intel",
                            "vram_total": "Shared",
                            "vram_used": "N/A",
                            "temp": "N/A",
                            "usage": "N/A"
                        })
        except:
            pass
        
        # Try Intel GPU Top (if installed)
        try:
            result = subprocess.run(
                ["intel_gpu_top", "-l"], capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0 and not gpus:
                gpus.append({
                    "name": "Intel Integrated Graphics",
                    "type": "Intel",
                    "vram_total": "Shared",
                    "vram_used": "N/A",
                    "temp": "N/A",
                    "usage": "Detected"
                })
        except:
            pass
        
        return {"available": len(gpus) > 0, "gpus": gpus}

# ============================================================================
# AUTHENTICATION
# ============================================================================

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(f"{password}llm_salt".encode()).hexdigest()
    
    @staticmethod
    def load_users() -> Dict:
        if not USERS_DB.exists():
            default = {
                "admin": {
                    "password": AuthManager.hash_password("admin123"),
                    "role": "admin",
                    "created": datetime.now().isoformat()
                }
            }
            with open(USERS_DB, "w") as f:
                json.dump(default, f, indent=2)
            return default
        with open(USERS_DB, "r") as f:
            return json.load(f)
    
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[str]]:
        users = AuthManager.load_users()
        if username not in users:
            return False, None
        if users[username]["password"] == AuthManager.hash_password(password):
            audit_log(username, "LOGIN", f"Role: {users[username]['role']}", True)
            return True, users[username]["role"]
        return False, None

# ============================================================================
# OLLAMA MANAGER
# ============================================================================

class OllamaManager:
    @staticmethod
    def get_available_models() -> List[Dict]:
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:
                    if line.strip():
                        parts = line.split()
                        models.append({
                            "name": parts[0],
                            "size": parts[2] if len(parts) > 2 else "?"
                        })
                return models
        except:
            pass
        return []
    
    @staticmethod
    def check_ollama_running() -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def chat_with_history(model: str, messages: List[Dict], temperature: float = 0.7) -> Dict:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature}
            }
            response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# CHAT HISTORY MANAGER
# ============================================================================

class ChatHistoryManager:
    @staticmethod
    def save_conversation(username: str, title: str, messages: List[Dict]) -> bool:
        try:
            user_dir = CHAT_HISTORY_DIR / username
            user_dir.mkdir(exist_ok=True)
            filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(user_dir / filename, "w") as f:
                json.dump({"title": title, "messages": messages, "saved": datetime.now().isoformat()}, f, indent=2)
            return True
        except:
            return False
    
    @staticmethod
    def load_conversations(username: str) -> List[Dict]:
        try:
            user_dir = CHAT_HISTORY_DIR / username
            if not user_dir.exists():
                return []
            convos = []
            for file in user_dir.glob("*.json"):
                with open(file, "r") as f:
                    data = json.load(f)
                    convos.append({"filename": file.stem, "title": data.get("title", file.stem), "saved": data.get("saved", "")})
            return sorted(convos, key=lambda x: x["saved"], reverse=True)
        except:
            return []
    
    @staticmethod
    def load_conversation(username: str, filename: str) -> Optional[Dict]:
        try:
            user_dir = CHAT_HISTORY_DIR / username
            with open(user_dir / f"{filename}.json", "r") as f:
                return json.load(f)
        except:
            return None
    
    @staticmethod
    def delete_conversation(username: str, filename: str) -> bool:
        try:
            (CHAT_HISTORY_DIR / username / f"{filename}.json").unlink()
            return True
        except:
            return False

# ============================================================================
# RAG MANAGER (Enhanced for common file types)
# ============================================================================

class RAGManager:
    @staticmethod
    def process_document(file_path: Path, filename: str) -> Tuple[bool, str]:
        try:
            content = ""
            ext = file_path.suffix.lower()
            
            # Text files
            if ext in ['.txt', '.md', '.csv', '.tsv', '.json', '.yaml', '.yml', '.xml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # PDF (basic text extraction)
            elif ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        for page in pdf.pages:
                            content += page.extract_text() + "\n"
                except ImportError:
                    return False, "PyPDF2 not installed. Run: pip install PyPDF2"
                except Exception as e:
                    return False, f"PDF error: {str(e)}"
            
            # DOCX
            elif ext in ['.docx', '.doc']:
                try:
                    import docx
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        content += para.text + "\n"
                except ImportError:
                    return False, "python-docx not installed. Run: pip install python-docx"
                except Exception as e:
                    return False, f"DOCX error: {str(e)}"
            
            else:
                return False, f"Unsupported file type: {ext}"
            
            if not content.strip():
                return False, "No text content extracted"
            
            # Save processed document
            doc_path = RAG_DOCS_DIR / f"{filename}.txt"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"Processed {len(content):,} chars"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def search_documents(query: str, max_results: int = 3) -> List[Dict]:
        try:
            results = []
            query_lower = query.lower()
            for doc_file in RAG_DOCS_DIR.glob("*.txt"):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                score = content.lower().count(query_lower)
                if score > 0:
                    idx = content.lower().find(query_lower)
                    context = content[max(0, idx-200):min(len(content), idx+200)]
                    results.append({"filename": doc_file.stem, "score": score, "context": context})
            return sorted(results, key=lambda x: x['score'], reverse=True)[:max_results]
        except:
            return []
    
    @staticmethod
    def get_documents() -> List[str]:
        return [f.stem for f in RAG_DOCS_DIR.glob("*.txt")]

# ============================================================================
# UI CONFIGURATION
# ============================================================================

st.set_page_config(page_title="🔐 Complete LLM Factory", layout="wide")

st.markdown("""
<style>
.chat-message {padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;}
.user-message {background-color: #e3f2fd; border-left: 4px solid #2196f3;}
.assistant-message {background-color: #f5f5f5; border-left: 4px solid #4caf50;}
.chat-header {font-weight: bold; margin-bottom: 0.5rem; font-size: 0.9em;}
.metric-compact {text-align: center; padding: 0.5rem;}
</style>
""", unsafe_allow_html=True)

def check_auth():
    return st.session_state.get('authenticated', False)

def show_login():
    st.title("🔐 Complete LLM Factory")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("**Default:** admin / admin123")
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("🔓 Login"):
                success, role = AuthManager.authenticate(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    if not check_auth():
        show_login()
        return
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    if 'chat_title' not in st.session_state:
        st.session_state.chat_title = "New Chat"
    if 'token_count' not in st.session_state:
        st.session_state.token_count = 0
    if 'rag_enabled' not in st.session_state:
        st.session_state.rag_enabled = False
    if 'persona' not in st.session_state:
        st.session_state.persona = "Default Assistant"
    if 'custom_persona' not in st.session_state:
        st.session_state.custom_persona = ""
    
    # Sidebar
    with st.sidebar:
        st.title("🔐 Complete LLM Factory")
        st.markdown(f"**User:** {st.session_state.username}")
        
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 Model")
        if OllamaManager.check_ollama_running():
            st.success("✅ Ollama")
            models = OllamaManager.get_available_models()
            if models:
                model_names = [m["name"] for m in models]
                st.session_state.selected_model = st.selectbox("Select:", model_names)
            else:
                st.warning("No models")
                st.session_state.selected_model = st.text_input("Model:", "llama3")
        else:
            st.error("❌ Start Ollama")
            st.code("ollama serve")
            st.session_state.selected_model = st.text_input("Model:", "llama3")
        
        st.divider()
        
        # Persona Selection
        st.subheader("🎭 Persona")
        st.session_state.persona = st.selectbox(
            "Select persona:",
            list(PERSONAS.keys()),
            index=list(PERSONAS.keys()).index(st.session_state.persona) if st.session_state.persona in PERSONAS else 0
        )
        
        if st.session_state.persona == "Custom":
            st.session_state.custom_persona = st.text_area(
                "Custom prompt:",
                value=st.session_state.custom_persona,
                height=100,
                placeholder="Define custom system prompt..."
            )
        else:
            with st.expander("View prompt"):
                st.caption(PERSONAS[st.session_state.persona])
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        st.session_state.rag_enabled = st.checkbox("🔍 RAG", st.session_state.rag_enabled)
        
        if st.session_state.rag_enabled:
            doc_count = len(RAGManager.get_documents())
            st.caption(f"📚 {doc_count} docs")
        
        st.divider()
        
        # Chat Management
        st.subheader("💾 Conversations")
        st.session_state.chat_title = st.text_input("Title:", st.session_state.chat_title)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New"):
                st.session_state.chat_history = []
                st.session_state.chat_title = "New Chat"
                st.session_state.token_count = 0
                st.rerun()
        with col2:
            if st.button("💾 Save"):
                if st.session_state.chat_history:
                    ChatHistoryManager.save_conversation(
                        st.session_state.username,
                        st.session_state.chat_title.replace(" ", "_"),
                        st.session_state.chat_history
                    )
                    st.success("Saved!")
        
        # Load conversations
        convos = ChatHistoryManager.load_conversations(st.session_state.username)
        if convos:
            with st.expander(f"📂 Saved ({len(convos)})"):
                for convo in convos[:5]:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        if st.button(f"📄 {convo['title'][:20]}", key=f"load_{convo['filename']}", use_container_width=True):
                            data = ChatHistoryManager.load_conversation(st.session_state.username, convo['filename'])
                            if data:
                                st.session_state.chat_history = data['messages']
                                st.session_state.chat_title = data['title']
                                st.rerun()
                    with col_b:
                        if st.button("🗑️", key=f"del_{convo['filename']}"):
                            ChatHistoryManager.delete_conversation(st.session_state.username, convo['filename'])
                            st.rerun()
        
        st.divider()
        st.caption(f"📊 ~{st.session_state.token_count} tokens")
    
    # Main Tabs
    tabs = st.tabs(["💬 Chat", "📚 RAG", "⚡ Hardware", "🛡️ Security"])
    
    with tabs[0]:
        chat_tab(temperature)
    with tabs[1]:
        rag_tab()
    with tabs[2]:
        hardware_tab()
    with tabs[3]:
        security_tab()

# ============================================================================
# CHAT TAB (FIXED: Input clearing issue)
# ============================================================================

def chat_tab(temperature):
    st.header(f"💬 {st.session_state.chat_title}")
    
    if not st.session_state.selected_model:
        st.warning("⚠️ Select a model")
        return
    
    # Status bar (compact)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Model", st.session_state.selected_model, label_visibility="collapsed")
        st.caption("Model")
    with col2:
        st.metric("Temp", f"{temperature:.1f}", label_visibility="collapsed")
        st.caption("Temperature")
    with col3:
        st.metric("Msgs", len(st.session_state.chat_history), label_visibility="collapsed")
        st.caption("Messages")
    with col4:
        rag_status = "🔍 ON" if st.session_state.rag_enabled else "OFF"
        st.metric("RAG", rag_status, label_visibility="collapsed")
        st.caption("RAG Status")
    
    st.divider()
    
    # Chat display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <h3>👋 Ready to chat!</h3>
                <p><strong>Persona:</strong> {st.session_state.persona}</p>
                <p>Ask me anything...</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, msg in enumerate(st.session_state.chat_history):
                role = msg["role"]
                content = msg["content"]
                timestamp = msg.get("timestamp", "")
                
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="chat-header">👤 You {timestamp}</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="chat-header">🤖 {st.session_state.selected_model} {timestamp}</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Message actions (compact)
                    col_a, col_b = st.columns([1, 5])
                    with col_a:
                        if st.button("📋", key=f"copy_{idx}", help="Copy"):
                            st.code(content)
                    with col_b:
                        if st.button("🔄", key=f"regen_{idx}", help="Regenerate"):
                            if idx > 0:
                                st.session_state.chat_history = st.session_state.chat_history[:idx-1]
                                if st.session_state.chat_history:
                                    last_user = st.session_state.chat_history[-1]
                                    if last_user["role"] == "user":
                                        process_message(last_user["content"], temperature)
                                st.rerun()
    
    st.divider()
    
    # FIXED: Input with proper clearing using form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Type your message here...",
            key="user_input_field"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            send = st.form_submit_button("📤 Send", type="primary", use_container_width=True)
        with col2:
            export = st.form_submit_button("📄 Export", use_container_width=True)
        with col3:
            stats = st.form_submit_button("📊 Stats", use_container_width=True)
    
    # Process actions
    if send and user_input.strip():
        process_message(user_input, temperature)
        st.rerun()
    
    if export:
        if st.session_state.chat_history:
            md = f"# {st.session_state.chat_title}\n\n"
            md += f"**Persona:** {st.session_state.persona}\n\n"
            for m in st.session_state.chat_history:
                role = "User" if m["role"] == "user" else "Assistant"
                md += f"## {role}\n\n{m['content']}\n\n"
            st.download_button("Download MD", md, f"{st.session_state.chat_title}.md", use_container_width=True)
    
    if stats:
        if st.session_state.chat_history:
            user_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "user")
            asst_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "assistant")
            total_chars = sum(len(m["content"]) for m in st.session_state.chat_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("User", user_msgs)
            with col2:
                st.metric("Assistant", asst_msgs)
            with col3:
                st.metric("Chars", f"{total_chars:,}")
    
    # Regenerate last button (outside form)
    if st.button("🔄 Regenerate Last", use_container_width=True):
        if st.session_state.chat_history:
            if st.session_state.chat_history[-1]["role"] == "assistant":
                st.session_state.chat_history.pop()
            if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
                last_msg = st.session_state.chat_history[-1]["content"]
                st.session_state.chat_history.pop()
                process_message(last_msg, temperature)
                st.rerun()

def process_message(user_input: str, temperature: float):
    """Process chat message with persona support"""
    # Token estimate
    tokens = len(user_input) // 4
    st.session_state.token_count += tokens
    
    # RAG enhancement
    enhanced_input = user_input
    if st.session_state.rag_enabled:
        docs = RAGManager.search_documents(user_input)
        if docs:
            context = "\n".join([f"{d['filename']}: {d['context']}" for d in docs])
            enhanced_input = f"Context from documents:\n{context}\n\nQuestion: {user_input}"
    
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Build messages with persona
    messages = []
    
    # Add system prompt (persona)
    if st.session_state.persona == "Custom" and st.session_state.custom_persona:
        messages.append({"role": "system", "content": st.session_state.custom_persona})
    elif st.session_state.persona in PERSONAS:
        messages.append({"role": "system", "content": PERSONAS[st.session_state.persona]})
    
    # Add chat history
    for msg in st.session_state.chat_history:
        if msg["role"] in ["user", "assistant"]:
            content = msg["content"]
            # Use enhanced input for last user message if RAG enabled
            if msg == st.session_state.chat_history[-1] and st.session_state.rag_enabled:
                content = enhanced_input
            messages.append({"role": msg["role"], "content": content})
    
    # Generate response
    response = OllamaManager.chat_with_history(
        st.session_state.selected_model,
        messages,
        temperature
    )
    
    if "error" not in response:
        content = response.get("message", {}).get("content", "No response")
        tokens = len(content) // 4
        st.session_state.token_count += tokens
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        audit_log(st.session_state.username, "CHAT", f"Tokens: ~{tokens}", True)
    else:
        st.error(f"Error: {response['error']}")

# ============================================================================
# RAG TAB (Enhanced for common file types)
# ============================================================================

def rag_tab():
    st.header("📚 RAG Documents")
    
    tab1, tab2 = st.tabs(["📤 Upload", "📋 Manage"])
    
    with tab1:
        st.info("**Supported formats:** TXT, MD, PDF, DOCX, CSV, JSON, YAML, XML")
        st.caption("For PDF/DOCX: Install dependencies if needed")
        st.code("pip install PyPDF2 python-docx")
        
        uploaded = st.file_uploader(
            "Upload documents:",
            type=['txt', 'md', 'pdf', 'docx', 'doc', 'csv', 'json', 'yaml', 'yml', 'xml', 'tsv'],
            accept_multiple_files=True
        )
        
        if uploaded and st.button("📥 Process Files", type="primary"):
            progress = st.progress(0)
            for idx, file in enumerate(uploaded):
                st.write(f"Processing: {file.name}")
                temp = WORKSPACE / file.name
                with open(temp, "wb") as f:
                    f.write(file.getbuffer())
                success, msg = RAGManager.process_document(temp, file.name)
                if success:
                    st.success(f"✅ {file.name}: {msg}")
                else:
                    st.error(f"❌ {file.name}: {msg}")
                temp.unlink()
                progress.progress((idx + 1) / len(uploaded))
            st.balloons()
    
    with tab2:
        docs = RAGManager.get_documents()
        if docs:
            st.success(f"📚 {len(docs)} document(s)")
            for doc in docs:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"📄 **{doc}**")
                with col2:
                    if st.button("🗑️", key=f"del_doc_{doc}"):
                        (RAG_DOCS_DIR / f"{doc}.txt").unlink(missing_ok=True)
                        st.rerun()
        else:
            st.info("No documents uploaded yet")

# ============================================================================
# HARDWARE TAB (Compact metrics, Intel GPU support)
# ============================================================================

def hardware_tab():
    st.header("⚡ Hardware Monitor")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # CPU (compact)
    st.subheader("🖥️ CPU")
    cpu = HardwareMonitor.get_cpu_usage()
    if cpu.get("available"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Usage", f"{cpu['percent']:.0f}%")
        with col2:
            st.metric("Cores", cpu['count'])
        with col3:
            status = "🟢 OK" if cpu['percent'] < 80 else "🔴 High"
            st.metric("Status", status)
    else:
        st.warning("Install: pip install psutil")
    
    st.divider()
    
    # Memory (compact)
    st.subheader("💾 Memory")
    mem = HardwareMonitor.get_memory_usage()
    if mem.get("available"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Usage", f"{mem['percent']:.0f}%")
        with col2:
            st.metric("Used / Total", f"{mem['used_gb']:.1f} / {mem['total_gb']:.1f} GB")
        st.progress(mem['percent'] / 100)
        if mem['percent'] > 85:
            st.error("⚠️ High memory usage!")
    
    st.divider()
    
    # Disk (compact)
    st.subheader("💿 Disk")
    disk = HardwareMonitor.get_disk_usage()
    if disk.get("available"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Usage", f"{disk['percent']:.0f}%")
        with col2:
            st.metric("Free / Total", f"{disk['free_gb']:.1f} / {disk['total_gb']:.1f} GB")
        st.progress(disk['percent'] / 100)
        if disk['percent'] > 90:
            st.error("⚠️ Low disk space!")
    
    st.divider()
    
    # GPU (Intel + NVIDIA support)
    st.subheader("🎮 GPU")
    gpu = HardwareMonitor.get_gpu_info()
    if gpu.get("available"):
        for idx, g in enumerate(gpu['gpus']):
            st.markdown(f"**{g['name']}** ({g['type']})")
            
            if g['type'] == "NVIDIA":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("VRAM", f"{g['vram_used']} / {g['vram_total']} MB")
                with col2:
                    st.metric("Temp", f"{g['temp']}°C")
                with col3:
                    st.metric("Usage", f"{g['usage']}%")
            elif g['type'] == "Intel":
                st.info("Intel GPU detected (integrated graphics, shared memory)")
            
            st.divider()
    else:
        st.info("No GPU detected")

# ============================================================================
# SECURITY TAB
# ============================================================================

def security_tab():
    st.header("🛡️ Security")
    
    st.subheader("📜 Audit Log")
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG) as f:
            lines = f.readlines()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Actions", len(lines))
        with col2:
            failures = sum(1 for line in lines if "FAILURE" in line)
            st.metric("Failures", failures)
        
        max_lines = st.slider("Show lines:", 10, 100, 20)
        st.text_area("Recent activity:", "".join(lines[-max_lines:]), height=300)
    else:
        st.info("No audit logs yet")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
