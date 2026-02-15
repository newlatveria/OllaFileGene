"""
Secure LLM Model Factory - Enhanced Version with Chat Interface
Includes: Chat interface, model selection, conversation history, and all security features
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
            self.ALLOWED_FILE_EXTENSIONS = ['.py', '.txt', '.json', '.yaml', '.yml', '.md']
        if self.BLOCKED_PATTERNS is None:
            self.BLOCKED_PATTERNS = [
                r'rm\s+-rf', r'sudo\s+', r'chmod\s+777', r'mkfs', r'dd\s+',
                r':(\(\)){', r'shutdown', r'reboot', r'eval\(', r'exec\(',
                r'__import__', r'subprocess\.(?!run\()', r'os\.system',
                r'shutil\.rmtree', r'open\([^)]*[\'"]w[\'"]', r'/etc/',
                r'/sys/', r'/proc/', r'\.\./',
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

# Create directory structure
for directory in [WORKSPACE, SANDBOX_DIR, LOG_DIR, CONFIG_DIR, CHAT_HISTORY_DIR]:
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
        """Hash password with salt"""
        salt = "llm_factory_salt_2024"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    @staticmethod
    def load_users() -> Dict:
        """Load user database"""
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
        """Authenticate user and return role"""
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
    """Manage Ollama models and interactions"""
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of installed Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            return []
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
            return []
    
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

# ============================================================================
# CHAT HISTORY MANAGEMENT
# ============================================================================

class ChatHistoryManager:
    """Manage chat conversation history"""
    
    @staticmethod
    def save_conversation(username: str, conversation_name: str, messages: List[Dict]):
        """Save conversation to file"""
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
        """Load list of saved conversations for user"""
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
        """Load specific conversation"""
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
        """Validate code for security issues"""
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
        """Sanitize user input"""
        text = text[:max_length]
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        return text

# ============================================================================
# STREAMLIT UI
# ============================================================================

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        return False
    return True

def show_login():
    """Display login page"""
    st.title("🔐 Secure LLM Model Factory")
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
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🔐 Secure LLM Model Factory",
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
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # Check authentication
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
    
    # Sidebar
    with st.sidebar:
        st.title("🔐 LLM Factory")
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role.upper()}")
        
        if st.button("🚪 Logout"):
            audit_log(st.session_state.username, "LOGOUT", "User logged out", True)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 Model Selection")
        
        # Check Ollama status
        ollama_running = OllamaManager.check_ollama_running()
        
        if ollama_running:
            st.success("✅ Ollama Running")
            
            # Get available models
            available_models = OllamaManager.get_available_models()
            
            if available_models:
                selected_model = st.selectbox(
                    "Select Model",
                    available_models,
                    key="model_selector"
                )
                st.session_state.selected_model = selected_model
                
                # Model info
                st.info(f"**Active:** {selected_model}")
            else:
                st.warning("No models installed")
                st.markdown("Install a model:")
                st.code("ollama pull llama3")
                
                # Manual model entry
                manual_model = st.text_input("Or enter model name:", "llama3")
                if st.button("Use This Model"):
                    st.session_state.selected_model = manual_model
        else:
            st.error("❌ Ollama Not Running")
            st.markdown("Start Ollama:")
            st.code("ollama serve")
            
            # Fallback
            manual_model = st.text_input("Model name:", "llama3")
            if st.button("Use Anyway"):
                st.session_state.selected_model = manual_model
        
        st.divider()
        
        # Model Settings
        st.subheader("⚙️ Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        with st.expander("System Prompt"):
            system_prompt = st.text_area(
                "Define assistant behavior:",
                value=st.session_state.system_prompt,
                height=100
            )
            if st.button("Update System Prompt"):
                st.session_state.system_prompt = system_prompt
                st.success("Updated!")
        
        st.divider()
        
        # Chat Management
        st.subheader("💾 Conversations")
        
        if st.button("🗑️ Clear Current Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("💾 Save Conversation"):
            if st.session_state.chat_history:
                conv_name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if ChatHistoryManager.save_conversation(
                    st.session_state.username,
                    conv_name,
                    st.session_state.chat_history
                ):
                    st.success("Saved!")
                    audit_log(st.session_state.username, "CHAT_SAVED", conv_name, True)
            else:
                st.warning("No messages to save")
        
        # Load conversations
        saved_conversations = ChatHistoryManager.load_conversations(st.session_state.username)
        if saved_conversations:
            with st.expander(f"📂 Saved ({len(saved_conversations)})"):
                for conv in saved_conversations[:5]:
                    if st.button(conv, key=f"load_{conv}"):
                        loaded = ChatHistoryManager.load_conversation(
                            st.session_state.username,
                            conv
                        )
                        if loaded:
                            st.session_state.chat_history = loaded
                            st.rerun()
    
    # Main content
    tabs = st.tabs([
        "💬 Chat Interface",
        "💻 Code Generation",
        "📊 Execution Monitor",
        "🛡️ Security",
        "📜 Audit Logs"
    ])
    
    # TAB 1: CHAT INTERFACE
    with tabs[0]:
        chat_interface_tab(temperature)
    
    # TAB 2: CODE GENERATION
    with tabs[1]:
        code_generation_tab(temperature)
    
    # TAB 3: EXECUTION MONITOR
    with tabs[2]:
        execution_monitor_tab()
    
    # TAB 4: SECURITY
    with tabs[3]:
        security_tab()
    
    # TAB 5: AUDIT LOGS
    with tabs[4]:
        audit_logs_tab()

# ============================================================================
# TAB IMPLEMENTATIONS
# ============================================================================

def chat_interface_tab(temperature):
    """Dedicated chat interface"""
    st.header("💬 Chat Interface")
    
    # Check if model is selected
    if not st.session_state.selected_model:
        st.warning("⚠️ Please select a model from the sidebar first")
        return
    
    # Display model info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info(f"**Model:** {st.session_state.selected_model}")
    with col2:
        st.info(f"**Temp:** {temperature}")
    with col3:
        st.info(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <h3>👋 Start a conversation!</h3>
                <p>Ask me anything - I'm here to help with coding, questions, or creative tasks.</p>
            </div>
            """, unsafe_allow_html=True)
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
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="chat-header">🤖 Assistant ({st.session_state.selected_model})</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Input area
    st.divider()
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Type your message here...",
            key="chat_input"
        )
    
    with col2:
        st.write("")
        st.write("")
        send_button = st.button("📤 Send", type="primary")
        
        if st.button("🔄 Regenerate"):
            if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                # Remove last assistant message and regenerate
                st.session_state.chat_history.pop()
                if st.session_state.chat_history:
                    last_user_msg = st.session_state.chat_history[-1]["content"]
                    st.session_state.chat_history.pop()
                    
                    # Regenerate
                    with st.spinner("🤔 Thinking..."):
                        response = OllamaManager.chat_with_history(
                            st.session_state.selected_model,
                            st.session_state.chat_history + [{"role": "user", "content": last_user_msg}],
                            temperature
                        )
                    
                    if "error" not in response:
                        st.session_state.chat_history.append({"role": "user", "content": last_user_msg})
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.get("message", {}).get("content", "No response")
                        })
                        st.rerun()
    
    # Send message
    if send_button and user_input.strip():
        # Sanitize input
        sanitized_input = SecurityValidator.sanitize_input(user_input)
        
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": sanitized_input
        })
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            # Prepare messages with system prompt
            messages = []
            if st.session_state.system_prompt:
                messages.append({
                    "role": "system",
                    "content": st.session_state.system_prompt
                })
            messages.extend(st.session_state.chat_history)
            
            response = OllamaManager.chat_with_history(
                st.session_state.selected_model,
                messages,
                temperature
            )
        
        if "error" in response:
            st.error(f"❌ Error: {response['error']}")
            audit_log(
                st.session_state.username,
                "CHAT_ERROR",
                f"Model: {st.session_state.selected_model}",
                False
            )
        else:
            # Add assistant response
            assistant_message = response.get("message", {}).get("content", "No response")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            audit_log(
                st.session_state.username,
                "CHAT_MESSAGE",
                f"Model: {st.session_state.selected_model}",
                True
            )
        
        st.rerun()
    
    # Export options
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy Last Response"):
            if st.session_state.chat_history:
                last_msg = st.session_state.chat_history[-1]
                if last_msg["role"] == "assistant":
                    st.code(last_msg["content"])
    
    with col2:
        if st.button("📄 Export Chat as Markdown"):
            if st.session_state.chat_history:
                markdown = "# Chat Conversation\n\n"
                for msg in st.session_state.chat_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    markdown += f"## {role}\n\n{msg['content']}\n\n"
                
                st.download_button(
                    "Download Markdown",
                    markdown,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
    
    with col3:
        if st.button("📊 Chat Statistics"):
            if st.session_state.chat_history:
                user_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "user")
                assistant_msgs = sum(1 for m in st.session_state.chat_history if m["role"] == "assistant")
                total_chars = sum(len(m["content"]) for m in st.session_state.chat_history)
                
                st.metric("User Messages", user_msgs)
                st.metric("Assistant Messages", assistant_msgs)
                st.metric("Total Characters", f"{total_chars:,}")

def code_generation_tab(temperature):
    """Code generation with security"""
    st.header("💻 Code Generation")
    
    if not st.session_state.selected_model:
        st.warning("⚠️ Please select a model from the sidebar")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input")
        
        code_prompt = st.text_area(
            "What code do you need?",
            height=200,
            placeholder="Example: Create a Python function to calculate fibonacci numbers"
        )
        
        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "Other"]
        )
        
        if st.button("🚀 Generate Code", type="primary"):
            if code_prompt:
                full_prompt = f"Generate {language} code for: {code_prompt}\n\nProvide only the code with comments."
                
                with st.spinner("Generating code..."):
                    response = OllamaManager.generate_response(
                        st.session_state.selected_model,
                        full_prompt,
                        temperature=temperature
                    )
                
                if "error" not in response:
                    generated_code = response.get("response", "")
                    st.session_state.generated_code = generated_code
                    st.rerun()
                else:
                    st.error(f"Error: {response['error']}")
    
    with col2:
        st.subheader("📤 Output")
        
        if 'generated_code' in st.session_state and st.session_state.generated_code:
            code = st.session_state.generated_code
            
            st.code(code, language=language.lower())
            
            # Security validation
            is_safe, issues = SecurityValidator.validate_code(code)
            
            if not is_safe:
                st.error("🚨 Security Issues Detected:")
                for issue in issues:
                    st.warning(f"• {issue}")
            else:
                st.success("✅ Code passed security validation")
            
            # Actions
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                filename = st.text_input("Filename:", value="generated_code.py")
                if st.button("💾 Save"):
                    try:
                        filepath = WORKSPACE / filename
                        with open(filepath, "w") as f:
                            f.write(code)
                        st.success(f"Saved to {filepath}")
                        audit_log(
                            st.session_state.username,
                            "CODE_SAVED",
                            f"File: {filename}",
                            True
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col_b:
                st.download_button(
                    "📥 Download",
                    code,
                    file_name=filename,
                    mime="text/plain"
                )
            
            with col_c:
                if st.button("📋 Copy"):
                    st.code(code)
                    st.info("Code displayed above - copy manually")

def execution_monitor_tab():
    """Monitor execution history"""
    st.header("📊 Execution Monitor")
    
    st.info("View workspace files and execution history")
    
    if WORKSPACE.exists():
        files = list(WORKSPACE.glob("*"))
        
        if files:
            st.subheader(f"📁 Workspace Files ({len(files)})")
            for file in files:
                if file.is_file():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.text(f"📄 {file.name}")
                    
                    with col2:
                        size_kb = file.stat().st_size / 1024
                        st.text(f"{size_kb:.1f} KB")
                    
                    with col3:
                        if st.button("👁️", key=f"view_{file.name}"):
                            try:
                                with open(file, "r") as f:
                                    content = f.read()
                                st.code(content)
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_{file.name}"):
                            try:
                                file.unlink()
                                st.success(f"Deleted {file.name}")
                                audit_log(
                                    st.session_state.username,
                                    "FILE_DELETED",
                                    f"File: {file.name}",
                                    True
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        else:
            st.info("No files in workspace")

def security_tab():
    """Security tools and validation"""
    st.header("🛡️ Security Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Code Security Scanner")
        
        scan_input = st.text_area(
            "Paste code to scan:",
            height=200
        )
        
        if st.button("🔍 Scan Code"):
            if scan_input:
                is_safe, issues = SecurityValidator.validate_code(scan_input)
                
                if is_safe:
                    st.success("✅ No security issues detected")
                else:
                    st.error(f"🚨 Found {len(issues)} security issues:")
                    for i, issue in enumerate(issues, 1):
                        st.warning(f"{i}. {issue}")
    
    with col2:
        st.subheader("📊 Security Statistics")
        
        if AUDIT_LOG.exists():
            with open(AUDIT_LOG, "r") as f:
                lines = f.readlines()
            
            total = len(lines)
            failures = sum(1 for line in lines if "FAILURE" in line)
            blocks = sum(1 for line in lines if "CODE_BLOCKED" in line)
            
            st.metric("Total Actions", total)
            st.metric("Failed Actions", failures)
            st.metric("Blocked Codes", blocks)
            
            if total > 0:
                success_rate = ((total - failures) / total) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")

def audit_logs_tab():
    """View audit logs"""
    st.header("📜 Audit Logs")
    
    if not AUDIT_LOG.exists():
        st.info("No audit logs available")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        filter_user = st.selectbox(
            "Filter by User",
            ["All"] + [st.session_state.username]
        )
    
    with col2:
        max_lines = st.slider("Lines to show", 10, 200, 50)
    
    # Read logs
    with open(AUDIT_LOG, "r") as f:
        lines = f.readlines()
    
    if filter_user != "All":
        lines = [line for line in lines if filter_user in line]
    
    # Display
    st.subheader(f"Showing last {min(len(lines), max_lines)} entries")
    
    log_text = "".join(reversed(lines[-max_lines:]))
    st.text_area("📋 Logs", value=log_text, height=400)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
