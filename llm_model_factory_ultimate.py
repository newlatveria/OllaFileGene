"""
Secure LLM Model Factory - Ultimate Edition
Features: Chat, Model Management, RAG, Document Processing, Full Controls
Version: 3.0.0
"""

import streamlit as st
import requests
import json
import subprocess
import os
import hashlib
import time
import re
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import secrets
import logging
from dataclasses import dataclass
from enum import Enum
import io

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class SecurityLevel(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

@dataclass
class SecurityConfig:
    """Centralized security configuration"""
    MAX_FILE_SIZE_MB: int = 10
    MAX_EXECUTION_TIME: int = 30
    ALLOWED_FILE_EXTENSIONS: List[str] = None
    BLOCKED_PATTERNS: List[str] = None
    MAX_DAILY_EXECUTIONS: int = 100
    REQUIRE_CONFIRMATION: bool = True
    ENABLE_AUDIT_LOG: bool = True
    SANDBOX_ENABLED: bool = True
    
    def __post_init__(self):
        if self.ALLOWED_FILE_EXTENSIONS is None:
            self.ALLOWED_FILE_EXTENSIONS = ['.py', '.txt', '.json', '.yaml', '.yml', '.md', '.pdf', '.docx']
        if self.BLOCKED_PATTERNS is None:
            self.BLOCKED_PATTERNS = [
                r'rm\s+-rf', r'sudo\s+', r'chmod\s+777', r'mkfs', r'dd\s+',
                r':(\(\)){', r'shutdown', r'reboot', r'eval\(', r'exec\(',
                r'__import__', r'subprocess\.(?!run\()', r'os\.system',
                r'shutil\.rmtree', r'/etc/', r'/sys/', r'/proc/', r'\.\./',
            ]

SECURITY_CONFIG = SecurityConfig()

# Paths
BASE_DIR = Path(__file__).parent
WORKSPACE = BASE_DIR / "workspace"
SANDBOX_DIR = BASE_DIR / "sandbox"
LOG_DIR = BASE_DIR / "logs"
AUDIT_LOG = LOG_DIR / "audit.log"
CONFIG_DIR = BASE_DIR / "config"
USERS_DB = CONFIG_DIR / "users.json"
CHAT_HISTORY_DIR = CONFIG_DIR / "chat_history"
RAG_DOCS_DIR = CONFIG_DIR / "rag_documents"
EMBEDDINGS_DIR = CONFIG_DIR / "embeddings"

# Create directory structure
for directory in [WORKSPACE, SANDBOX_DIR, LOG_DIR, CONFIG_DIR, CHAT_HISTORY_DIR, RAG_DOCS_DIR, EMBEDDINGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def audit_log(user: str, action: str, details: str, success: bool = True):
    """Write to audit log"""
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILURE"
    log_entry = f"{timestamp} | {user} | {action} | {status} | {details}\n"
    
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

class AuthManager:
    """Secure authentication and session management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        salt = "llm_factory_salt_2024"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    @staticmethod
    def load_users() -> Dict:
        if not USERS_DB.exists():
            default_users = {
                "admin": {
                    "password": AuthManager.hash_password("admin123"),
                    "role": SecurityLevel.ADMIN.value,
                    "created": datetime.now().isoformat()
                }
            }
            with open(USERS_DB, "w") as f:
                json.dump(default_users, f, indent=2)
            return default_users
        
        with open(USERS_DB, "r") as f:
            return json.load(f)
    
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[str]]:
        users = AuthManager.load_users()
        
        if username not in users:
            audit_log("SYSTEM", "LOGIN_FAILED", f"Unknown user: {username}", False)
            return False, None
        
        hashed = AuthManager.hash_password(password)
        if users[username]["password"] == hashed:
            role = users[username]["role"]
            audit_log(username, "LOGIN_SUCCESS", f"Role: {role}", True)
            return True, role
        
        audit_log(username, "LOGIN_FAILED", "Invalid password", False)
        return False, None

# ============================================================================
# OLLAMA MODEL MANAGEMENT
# ============================================================================

class OllamaManager:
    """Complete Ollama model management"""
    
    @staticmethod
    def get_available_models() -> List[Dict]:
        """Get detailed list of installed Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            models.append({
                                "name": parts[0],
                                "id": parts[1] if len(parts) > 1 else "",
                                "size": parts[2] if len(parts) > 2 else "",
                                "modified": " ".join(parts[3:]) if len(parts) > 3 else ""
                            })
                return models
            return []
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
            return []
    
    @staticmethod
    def get_model_info(model_name: str) -> Dict:
        """Get detailed information about a specific model"""
        try:
            result = subprocess.run(
                ["ollama", "show", model_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "name": model_name,
                    "info": result.stdout,
                    "available": True
                }
            return {"name": model_name, "available": False}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"name": model_name, "available": False, "error": str(e)}
    
    @staticmethod
    def pull_model(model_name: str) -> Tuple[bool, str]:
        """Download a model from Ollama library"""
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=600)  # 10 min timeout
            
            if process.returncode == 0:
                return True, "Model downloaded successfully"
            else:
                return False, stderr or "Download failed"
        except subprocess.TimeoutExpired:
            return False, "Download timeout (10 minutes exceeded)"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def delete_model(model_name: str) -> Tuple[bool, str]:
        """Delete a model"""
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, f"Model {model_name} deleted"
            else:
                return False, result.stderr or "Deletion failed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_ollama_running() -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def generate_response(model: str, prompt: str, system: str = None, 
                         temperature: float = 0.7, stream: bool = False) -> Dict:
        """Generate response from Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system:
                payload["system"] = system
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def chat_with_history(model: str, messages: List[Dict], 
                         temperature: float = 0.7) -> Dict:
        """Chat with conversation history"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def generate_embeddings(model: str, text: str) -> Optional[List[float]]:
        """Generate embeddings for RAG"""
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json().get("embedding")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None

# ============================================================================
# RAG DOCUMENT MANAGER
# ============================================================================

class RAGManager:
    """Manage documents for Retrieval Augmented Generation"""
    
    @staticmethod
    def process_document(file_path: Path, file_name: str) -> Tuple[bool, str]:
        """Process uploaded document for RAG"""
        try:
            # Read file content
            if file_path.suffix == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_path.suffix == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_path.suffix == '.pdf':
                try:
                    # Try to extract text from PDF
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page in pdf_reader.pages:
                            content += page.extract_text()
                except:
                    content = "PDF content extraction requires PyPDF2 package"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Save processed content
            doc_path = RAG_DOCS_DIR / f"{file_name}.txt"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Store metadata
            metadata = {
                "filename": file_name,
                "uploaded": datetime.now().isoformat(),
                "size": len(content),
                "path": str(doc_path)
            }
            
            meta_path = RAG_DOCS_DIR / f"{file_name}.meta.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True, f"Document processed: {len(content)} characters"
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return False, str(e)
    
    @staticmethod
    def get_documents() -> List[Dict]:
        """Get list of processed documents"""
        try:
            documents = []
            for meta_file in RAG_DOCS_DIR.glob("*.meta.json"):
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                    documents.append(metadata)
            return sorted(documents, key=lambda x: x.get('uploaded', ''), reverse=True)
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    @staticmethod
    def delete_document(filename: str) -> bool:
        """Delete a document and its metadata"""
        try:
            doc_path = RAG_DOCS_DIR / f"{filename}.txt"
            meta_path = RAG_DOCS_DIR / f"{filename}.meta.json"
            
            if doc_path.exists():
                doc_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    @staticmethod
    def search_documents(query: str, max_results: int = 3) -> List[Dict]:
        """Simple keyword search in documents"""
        try:
            results = []
            query_lower = query.lower()
            
            for doc_file in RAG_DOCS_DIR.glob("*.txt"):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple relevance scoring
                content_lower = content.lower()
                score = content_lower.count(query_lower)
                
                if score > 0:
                    # Get context around matches
                    context = RAGManager._extract_context(content, query, max_chars=500)
                    results.append({
                        "filename": doc_file.stem,
                        "score": score,
                        "context": context,
                        "full_content": content
                    })
            
            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    @staticmethod
    def _extract_context(text: str, query: str, max_chars: int = 500) -> str:
        """Extract relevant context around query matches"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        idx = text_lower.find(query_lower)
        if idx == -1:
            return text[:max_chars]
        
        start = max(0, idx - max_chars // 2)
        end = min(len(text), idx + max_chars // 2)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context

# ============================================================================
# CHAT HISTORY MANAGEMENT
# ============================================================================

class ChatHistoryManager:
    """Manage chat conversation history"""
    
    @staticmethod
    def save_conversation(username: str, conversation_name: str, messages: List[Dict]):
        try:
            user_dir = CHAT_HISTORY_DIR / username
            user_dir.mkdir(exist_ok=True)
            
            filename = f"{conversation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = user_dir / filename
            
            with open(filepath, "w") as f:
                json.dump(messages, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    @staticmethod
    def load_conversations(username: str) -> List[str]:
        try:
            user_dir = CHAT_HISTORY_DIR / username
            if not user_dir.exists():
                return []
            
            conversations = [f.stem for f in user_dir.glob("*.json")]
            return sorted(conversations, reverse=True)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            return []
    
    @staticmethod
    def load_conversation(username: str, conversation_name: str) -> List[Dict]:
        try:
            user_dir = CHAT_HISTORY_DIR / username
            conversations = list(user_dir.glob(f"{conversation_name}*.json"))
            
            if conversations:
                with open(conversations[0], "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return []

# ============================================================================
# SECURITY VALIDATION
# ============================================================================

class SecurityValidator:
    """Comprehensive security validation"""
    
    @staticmethod
    def validate_code(code: str) -> Tuple[bool, List[str]]:
        issues = []
        
        for pattern in SECURITY_CONFIG.BLOCKED_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Blocked pattern detected: {pattern}")
        
        dangerous_imports = ['os', 'subprocess', 'shutil', 'sys', 'ctypes', 'pickle']
        for imp in dangerous_imports:
            if re.search(rf'\bimport\s+{imp}\b|\bfrom\s+{imp}\s+import', code):
                issues.append(f"Dangerous import: {imp}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        text = text[:max_length]
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        return text

# ============================================================================
# STREAMLIT UI CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🔐 Secure LLM Factory - Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .chat-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .model-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_auth():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        return False
    return True

def show_login():
    st.title("🔐 Secure LLM Model Factory - Ultimate Edition")
    st.subheader("Authentication Required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("**Default Credentials**\nUsername: `admin`\nPassword: `admin123`")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("🔓 Login")
            
            if submit:
                success, role = AuthManager.authenticate(username, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.login_time = datetime.now()
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
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = "You are a helpful AI assistant."
    if 'rag_enabled' not in st.session_state:
        st.session_state.rag_enabled = False
    
    # Sidebar
    with st.sidebar:
        st.title("🔐 LLM Factory Ultimate")
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role.upper()}")
        
        if st.button("🚪 Logout"):
            audit_log(st.session_state.username, "LOGOUT", "User logged out", True)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 Active Model")
        
        ollama_running = OllamaManager.check_ollama_running()
        
        if ollama_running:
            st.success("✅ Ollama Running")
            
            available_models = OllamaManager.get_available_models()
            
            if available_models:
                model_names = [m["name"] for m in available_models]
                selected_model = st.selectbox(
                    "Select Model",
                    model_names,
                    key="model_selector"
                )
                st.session_state.selected_model = selected_model
                
                # Quick model info
                selected_info = next((m for m in available_models if m["name"] == selected_model), None)
                if selected_info:
                    st.caption(f"Size: {selected_info.get('size', 'Unknown')}")
            else:
                st.warning("No models installed")
                manual_model = st.text_input("Model name:", "llama3")
                if st.button("Use This Model"):
                    st.session_state.selected_model = manual_model
        else:
            st.error("❌ Ollama Not Running")
            st.code("ollama serve")
            manual_model = st.text_input("Model name:", "llama3")
            if st.button("Use Anyway"):
                st.session_state.selected_model = manual_model
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        # RAG Toggle
        st.session_state.rag_enabled = st.checkbox(
            "🔍 Enable RAG",
            value=st.session_state.rag_enabled,
            help="Use uploaded documents for context"
        )
        
        if st.session_state.rag_enabled:
            num_docs = len(RAGManager.get_documents())
            st.caption(f"📚 {num_docs} documents available")
        
        with st.expander("System Prompt"):
            system_prompt = st.text_area(
                "Define behavior:",
                value=st.session_state.system_prompt,
                height=100
            )
            if st.button("Update"):
                st.session_state.system_prompt = system_prompt
                st.success("Updated!")
        
        st.divider()
        
        # Chat Management
        st.subheader("💾 Conversations")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("💾 Save", use_container_width=True):
                if st.session_state.chat_history:
                    conv_name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    ChatHistoryManager.save_conversation(
                        st.session_state.username,
                        conv_name,
                        st.session_state.chat_history
                    )
                    st.success("Saved!")
    
    # Main Tabs
    tabs = st.tabs([
        "💬 Chat",
        "🤖 Model Manager",
        "📚 RAG Documents",
        "💻 Code Gen",
        "📊 Monitor",
        "🛡️ Security",
        "📜 Logs"
    ])
    
    with tabs[0]:
        chat_interface_tab(temperature)
    
    with tabs[1]:
        model_management_tab()
    
    with tabs[2]:
        rag_documents_tab()
    
    with tabs[3]:
        code_generation_tab(temperature)
    
    with tabs[4]:
        execution_monitor_tab()
    
    with tabs[5]:
        security_tab()
    
    with tabs[6]:
        audit_logs_tab()

# ============================================================================
# TAB: CHAT INTERFACE
# ============================================================================

def chat_interface_tab(temperature):
    st.header("💬 Chat Interface")
    
    if not st.session_state.selected_model:
        st.warning("⚠️ Please select a model from sidebar")
        return
    
    # Status bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Model:** {st.session_state.selected_model}")
    with col2:
        st.info(f"**Temp:** {temperature}")
    with col3:
        st.info(f"**Messages:** {len(st.session_state.chat_history)}")
    with col4:
        rag_status = "🔍 RAG ON" if st.session_state.rag_enabled else "RAG OFF"
        st.info(f"**{rag_status}**")
    
    # Chat display
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <h3>👋 Start a conversation!</h3>
                <p>Ask anything - I'm powered by {}</p>
            </div>
            """.format(st.session_state.selected_model), unsafe_allow_html=True)
        else:
            for message in st.session_state.chat_history:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="chat-header">👤 You</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show RAG context if present
                    rag_context = message.get("rag_context", "")
                    context_display = ""
                    if rag_context:
                        context_display = f"<small><em>📚 Used {len(rag_context)} document(s)</em></small><br>"
                    
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="chat-header">🤖 {st.session_state.selected_model}</div>
                        {context_display}
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Input
    st.divider()
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Type here...",
            key="chat_input"
        )
    
    with col2:
        st.write("")
        st.write("")
        send_button = st.button("📤 Send", type="primary")
        
        if st.button("🔄 Regen"):
            if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                st.session_state.chat_history.pop()
                if st.session_state.chat_history:
                    last_user_msg = st.session_state.chat_history[-1]["content"]
                    st.session_state.chat_history.pop()
                    
                    with st.spinner("🤔 Thinking..."):
                        # RAG search if enabled
                        rag_context = ""
                        if st.session_state.rag_enabled:
                            docs = RAGManager.search_documents(last_user_msg)
                            if docs:
                                rag_context = "\n\n".join([d["context"] for d in docs])
                                last_user_msg = f"Context from documents:\n{rag_context}\n\nQuestion: {last_user_msg}"
                        
                        response = OllamaManager.chat_with_history(
                            st.session_state.selected_model,
                            st.session_state.chat_history + [{"role": "user", "content": last_user_msg}],
                            temperature
                        )
                    
                    if "error" not in response:
                        st.session_state.chat_history.append({"role": "user", "content": last_user_msg})
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.get("message", {}).get("content", ""),
                            "rag_context": rag_context
                        })
                        st.rerun()
    
    if send_button and user_input.strip():
        sanitized_input = SecurityValidator.sanitize_input(user_input)
        
        # RAG enhancement
        rag_context = ""
        enhanced_input = sanitized_input
        
        if st.session_state.rag_enabled:
            docs = RAGManager.search_documents(sanitized_input)
            if docs:
                rag_context = "\n\n".join([f"Document: {d['filename']}\n{d['context']}" for d in docs])
                enhanced_input = f"Context from uploaded documents:\n{rag_context}\n\nUser question: {sanitized_input}"
                st.info(f"📚 Found {len(docs)} relevant document(s)")
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": sanitized_input
        })
        
        with st.spinner("🤔 Thinking..."):
            messages = []
            if st.session_state.system_prompt:
                messages.append({
                    "role": "system",
                    "content": st.session_state.system_prompt
                })
            
            # Add chat history with RAG-enhanced last message
            for msg in st.session_state.chat_history[:-1]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": enhanced_input})
            
            response = OllamaManager.chat_with_history(
                st.session_state.selected_model,
                messages,
                temperature
            )
        
        if "error" in response:
            st.error(f"❌ Error: {response['error']}")
        else:
            assistant_message = response.get("message", {}).get("content", "")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_message,
                "rag_context": rag_context
            })
            
            audit_log(
                st.session_state.username,
                "CHAT_MESSAGE",
                f"Model: {st.session_state.selected_model}, RAG: {st.session_state.rag_enabled}",
                True
            )
        
        st.rerun()
    
    # Export
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as Markdown"):
            if st.session_state.chat_history:
                markdown = f"# Chat with {st.session_state.selected_model}\n\n"
                for msg in st.session_state.chat_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    markdown += f"## {role}\n\n{msg['content']}\n\n"
                
                st.download_button(
                    "Download",
                    markdown,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
    
    with col2:
        if st.button("📊 Statistics"):
            if st.session_state.chat_history:
                user_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "user")
                assistant_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "assistant")
                total_chars = sum(len(m["content"]) for m in st.session_state.chat_history)
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("User", user_msgs)
                col_b.metric("Assistant", assistant_msgs)
                col_c.metric("Chars", f"{total_chars:,}")

# ============================================================================
# TAB: MODEL MANAGEMENT
# ============================================================================

def model_management_tab():
    st.header("🤖 Model Management & Controls")
    
    # Ollama status
    ollama_running = OllamaManager.check_ollama_running()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if ollama_running:
            st.success("✅ Ollama Service: Running")
        else:
            st.error("❌ Ollama Service: Not Running")
            st.code("Start with: ollama serve")
    
    with col2:
        if st.button("🔄 Refresh Models"):
            st.rerun()
    
    st.divider()
    
    # Tabs for different model operations
    model_tabs = st.tabs(["📋 Installed Models", "📥 Download Models", "⚙️ Model Info"])
    
    # INSTALLED MODELS
    with model_tabs[0]:
        st.subheader("📋 Installed Models")
        
        if not ollama_running:
            st.warning("Ollama service not running")
            return
        
        models = OllamaManager.get_available_models()
        
        if not models:
            st.info("No models installed. Download models from the 'Download Models' tab.")
        else:
            st.success(f"Found {len(models)} installed model(s)")
            
            for model in models:
                with st.expander(f"🤖 {model['name']}", expanded=False):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.markdown(f"**Name:** {model['name']}")
                        st.markdown(f"**Size:** {model.get('size', 'Unknown')}")
                        st.markdown(f"**Modified:** {model.get('modified', 'Unknown')}")
                    
                    with col_b:
                        if st.button("ℹ️ Details", key=f"info_{model['name']}"):
                            info = OllamaManager.get_model_info(model['name'])
                            st.text_area("Model Info", info.get('info', 'N/A'), height=200)
                    
                    with col_c:
                        if st.button("🗑️ Delete", key=f"del_{model['name']}"):
                            if st.session_state.get(f"confirm_delete_{model['name']}", False):
                                success, msg = OllamaManager.delete_model(model['name'])
                                if success:
                                    st.success(msg)
                                    audit_log(
                                        st.session_state.username,
                                        "MODEL_DELETED",
                                        model['name'],
                                        True
                                    )
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.session_state[f"confirm_delete_{model['name']}"] = True
                                st.warning("Click again to confirm deletion")
    
    # DOWNLOAD MODELS
    with model_tabs[1]:
        st.subheader("📥 Download New Models")
        
        st.info("Popular models from Ollama library")
        
        # Predefined models
        popular_models = {
            "llama3": {"size": "4.7GB", "desc": "Meta's Llama 3 - Great all-rounder"},
            "llama3:70b": {"size": "40GB", "desc": "Llama 3 70B - Most capable"},
            "mistral": {"size": "4.1GB", "desc": "Mistral 7B - Fast and efficient"},
            "codellama": {"size": "3.8GB", "desc": "Code-specialized Llama"},
            "phi3": {"size": "2.2GB", "desc": "Microsoft Phi-3 - Lightweight"},
            "gemma2": {"size": "5.4GB", "desc": "Google Gemma 2"},
            "qwen2": {"size": "4.4GB", "desc": "Alibaba Qwen 2"},
        }
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            model_choice = st.selectbox(
                "Select model to download:",
                list(popular_models.keys())
            )
            
            if model_choice:
                info = popular_models[model_choice]
                st.caption(f"**Size:** {info['size']} | **Description:** {info['desc']}")
        
        with col2:
            st.write("")
            st.write("")
            if st.button("📥 Download Selected Model", type="primary"):
                st.session_state.downloading_model = model_choice
                st.session_state.download_started = True
        
        # Custom model
        st.divider()
        custom_model = st.text_input("Or enter custom model name:")
        if st.button("📥 Download Custom Model"):
            if custom_model:
                st.session_state.downloading_model = custom_model
                st.session_state.download_started = True
        
        # Download progress
        if st.session_state.get("download_started", False):
            model_to_download = st.session_state.get("downloading_model", "")
            
            if model_to_download:
                with st.spinner(f"Downloading {model_to_download}... This may take several minutes."):
                    success, message = OllamaManager.pull_model(model_to_download)
                
                if success:
                    st.success(f"✅ {message}")
                    audit_log(
                        st.session_state.username,
                        "MODEL_DOWNLOADED",
                        model_to_download,
                        True
                    )
                else:
                    st.error(f"❌ {message}")
                
                st.session_state.download_started = False
                st.session_state.downloading_model = None
    
    # MODEL INFO
    with model_tabs[2]:
        st.subheader("⚙️ Detailed Model Information")
        
        models = OllamaManager.get_available_models()
        
        if models:
            model_names = [m["name"] for m in models]
            selected_info_model = st.selectbox("Select model:", model_names, key="info_select")
            
            if st.button("Get Detailed Info"):
                with st.spinner("Fetching model information..."):
                    info = OllamaManager.get_model_info(selected_info_model)
                
                if info.get("available"):
                    st.text_area("Model Information", info.get("info", ""), height=400)
                else:
                    st.error("Could not retrieve model information")
        else:
            st.info("No models available for inspection")

# ============================================================================
# TAB: RAG DOCUMENTS
# ============================================================================

def rag_documents_tab():
    st.header("📚 RAG Document Management")
    
    st.info("Upload documents to enhance chat responses with your own knowledge base")
    
    doc_tabs = st.tabs(["📤 Upload", "📋 Manage Documents", "🔍 Search Test"])
    
    # UPLOAD
    with doc_tabs[0]:
        st.subheader("📤 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Upload documents for RAG",
            accept_multiple_files=True,
            type=['txt', 'md', 'pdf', 'doc', 'docx', 'json']
        )
        
        if uploaded_files:
            if st.button("Process Uploaded Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Save temporarily
                    temp_path = WORKSPACE / uploaded_file.name
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process
                    success, message = RAGManager.process_document(temp_path, uploaded_file.name)
                    
                    if success:
                        st.success(f"✅ {uploaded_file.name}: {message}")
                        audit_log(
                            st.session_state.username,
                            "RAG_DOC_UPLOADED",
                            uploaded_file.name,
                            True
                        )
                    else:
                        st.error(f"❌ {uploaded_file.name}: {message}")
                    
                    # Cleanup temp file
                    if temp_path.exists():
                        temp_path.unlink()
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("All files processed!")
                st.balloons()
    
    # MANAGE
    with doc_tabs[1]:
        st.subheader("📋 Manage Documents")
        
        documents = RAGManager.get_documents()
        
        if not documents:
            st.info("No documents uploaded yet")
        else:
            st.success(f"Found {len(documents)} document(s)")
            
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Uploaded:** {doc.get('uploaded', 'Unknown')}")
                        st.markdown(f"**Size:** {doc.get('size', 0):,} characters")
                    
                    with col2:
                        if st.button("👁️ View", key=f"view_{doc['filename']}"):
                            try:
                                with open(doc['path'], 'r') as f:
                                    content = f.read()
                                st.text_area("Content", content[:1000] + "..." if len(content) > 1000 else content, height=300)
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_doc_{doc['filename']}"):
                            if RAGManager.delete_document(doc['filename']):
                                st.success(f"Deleted {doc['filename']}")
                                audit_log(
                                    st.session_state.username,
                                    "RAG_DOC_DELETED",
                                    doc['filename'],
                                    True
                                )
                                st.rerun()
                            else:
                                st.error("Failed to delete")
    
    # SEARCH TEST
    with doc_tabs[2]:
        st.subheader("🔍 Test Document Search")
        
        test_query = st.text_input("Enter a test query:")
        
        if st.button("Search Documents"):
            if test_query:
                with st.spinner("Searching..."):
                    results = RAGManager.search_documents(test_query, max_results=5)
                
                if results:
                    st.success(f"Found {len(results)} relevant document(s)")
                    
                    for i, result in enumerate(results, 1):
                        st.markdown(f"### Result {i}: {result['filename']}")
                        st.markdown(f"**Relevance Score:** {result['score']}")
                        st.markdown(f"**Context:**")
                        st.info(result['context'])
                        st.divider()
                else:
                    st.warning("No relevant documents found")

# ============================================================================
# TAB: CODE GENERATION
# ============================================================================

def code_generation_tab(temperature):
    st.header("💻 Code Generation")
    
    if not st.session_state.selected_model:
        st.warning("⚠️ Please select a model")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input")
        
        code_prompt = st.text_area(
            "What code do you need?",
            height=200,
            placeholder="Example: Create a Python function to sort a list using quicksort"
        )
        
        language = st.selectbox(
            "Language",
            ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript", "PHP"]
        )
        
        if st.button("🚀 Generate", type="primary"):
            if code_prompt:
                full_prompt = f"Generate {language} code for: {code_prompt}\n\nProvide only clean, well-commented code."
                
                with st.spinner("Generating..."):
                    response = OllamaManager.generate_response(
                        st.session_state.selected_model,
                        full_prompt,
                        temperature=temperature
                    )
                
                if "error" not in response:
                    st.session_state.generated_code = response.get("response", "")
                    st.rerun()
    
    with col2:
        st.subheader("📤 Output")
        
        if 'generated_code' in st.session_state and st.session_state.generated_code:
            code = st.session_state.generated_code
            
            st.code(code, language=language.lower())
            
            is_safe, issues = SecurityValidator.validate_code(code)
            
            if not is_safe:
                st.error("🚨 Security Issues:")
                for issue in issues:
                    st.warning(f"• {issue}")
            else:
                st.success("✅ Security: Pass")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                filename = st.text_input("Filename:", f"code.{language.lower()[:2]}")
                if st.button("💾 Save"):
                    try:
                        with open(WORKSPACE / filename, "w") as f:
                            f.write(code)
                        st.success(f"Saved to {filename}")
                    except Exception as e:
                        st.error(str(e))
            
            with col_b:
                st.download_button("📥 Download", code, file_name=filename)
            
            with col_c:
                if st.button("📋 Copy"):
                    st.code(code)

# ============================================================================
# TAB: EXECUTION MONITOR
# ============================================================================

def execution_monitor_tab():
    st.header("📊 Execution Monitor")
    
    files = list(WORKSPACE.glob("*"))
    
    if files:
        st.success(f"📁 {len([f for f in files if f.is_file()])} file(s) in workspace")
        
        for file in files:
            if file.is_file():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.text(f"📄 {file.name}")
                
                with col2:
                    st.text(f"{file.stat().st_size / 1024:.1f} KB")
                
                with col3:
                    if st.button("👁️", key=f"view_{file.name}"):
                        try:
                            with open(file, "r") as f:
                                st.code(f.read())
                        except:
                            st.error("Cannot read file")
                
                with col4:
                    if st.button("🗑️", key=f"del_{file.name}"):
                        file.unlink()
                        st.success("Deleted")
                        st.rerun()
    else:
        st.info("No files in workspace")

# ============================================================================
# TAB: SECURITY
# ============================================================================

def security_tab():
    st.header("🛡️ Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Code Scanner")
        
        scan_input = st.text_area("Paste code:", height=200)
        
        if st.button("🔍 Scan"):
            if scan_input:
                is_safe, issues = SecurityValidator.validate_code(scan_input)
                
                if is_safe:
                    st.success("✅ No issues")
                else:
                    st.error(f"🚨 {len(issues)} issues:")
                    for issue in issues:
                        st.warning(issue)
    
    with col2:
        st.subheader("📊 Stats")
        
        if AUDIT_LOG.exists():
            with open(AUDIT_LOG) as f:
                lines = f.readlines()
            
            total = len(lines)
            failures = sum(1 for line in lines if "FAILURE" in line)
            
            st.metric("Total Actions", total)
            st.metric("Failures", failures)
            if total > 0:
                st.metric("Success Rate", f"{((total-failures)/total*100):.1f}%")

# ============================================================================
# TAB: AUDIT LOGS
# ============================================================================

def audit_logs_tab():
    st.header("📜 Audit Logs")
    
    if AUDIT_LOG.exists():
        max_lines = st.slider("Lines", 10, 200, 50)
        
        with open(AUDIT_LOG) as f:
            lines = f.readlines()
        
        st.text_area("Logs", "".join(reversed(lines[-max_lines:])), height=400)
    else:
        st.info("No logs")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
