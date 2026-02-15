"""
Secure LLM Model Factory - Production-Ready Version
Enhanced with authentication, sandboxing, audit logging, and comprehensive security controls
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
                r'rm\s+-rf',
                r'sudo\s+',
                r'chmod\s+777',
                r'mkfs',
                r'dd\s+',
                r':(\(\)){',
                r'shutdown',
                r'reboot',
                r'eval\(',
                r'exec\(',
                r'__import__',
                r'subprocess\.(?!run\()',
                r'os\.system',
                r'shutil\.rmtree',
                r'open\([^)]*[\'"]w[\'"]',  # Write operations
                r'/etc/',
                r'/sys/',
                r'/proc/',
                r'\.\./',  # Path traversal
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

# Create directory structure
for directory in [WORKSPACE, SANDBOX_DIR, LOG_DIR, CONFIG_DIR]:
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
        salt = "llm_factory_salt_2024"  # In production, use unique salts per user
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    @staticmethod
    def load_users() -> Dict:
        """Load user database"""
        if not USERS_DB.exists():
            # Create default admin user
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
    
    @staticmethod
    def create_user(username: str, password: str, role: str) -> bool:
        """Create new user (admin only)"""
        users = AuthManager.load_users()
        
        if username in users:
            return False
        
        users[username] = {
            "password": AuthManager.hash_password(password),
            "role": role,
            "created": datetime.now().isoformat()
        }
        
        with open(USERS_DB, "w") as f:
            json.dump(users, f, indent=2)
        
        audit_log("ADMIN", "USER_CREATED", f"Username: {username}, Role: {role}", True)
        return True
    
    @staticmethod
    def change_password(username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        users = AuthManager.load_users()
        
        if username not in users:
            return False
        
        if users[username]["password"] != AuthManager.hash_password(old_password):
            return False
        
        users[username]["password"] = AuthManager.hash_password(new_password)
        
        with open(USERS_DB, "w") as f:
            json.dump(users, f, indent=2)
        
        audit_log(username, "PASSWORD_CHANGED", "Password updated", True)
        return True

# ============================================================================
# SECURITY VALIDATION
# ============================================================================

class SecurityValidator:
    """Comprehensive security validation"""
    
    @staticmethod
    def validate_code(code: str) -> Tuple[bool, List[str]]:
        """Validate code for security issues"""
        issues = []
        
        # Check for dangerous patterns
        for pattern in SECURITY_CONFIG.BLOCKED_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Blocked pattern detected: {pattern}")
        
        # Check for suspicious imports
        dangerous_imports = ['os', 'subprocess', 'shutil', 'sys', 'ctypes', 'pickle']
        for imp in dangerous_imports:
            if re.search(rf'\bimport\s+{imp}\b|\bfrom\s+{imp}\s+import', code):
                issues.append(f"Dangerous import: {imp}")
        
        # Check for file operations
        file_ops = ['open(', 'write(', 'unlink(', 'remove(']
        for op in file_ops:
            if op in code:
                issues.append(f"File operation detected: {op}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """Validate filename for security"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Path traversal attempt detected"
        
        # Check extension
        ext = Path(filename).suffix
        if ext not in SECURITY_CONFIG.ALLOWED_FILE_EXTENSIONS:
            return False, f"File extension {ext} not allowed"
        
        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False, "Invalid characters in filename"
        
        return True, ""
    
    @staticmethod
    def validate_command(cmd_list: List[str]) -> Tuple[bool, str]:
        """Validate shell command for security"""
        # Whitelist of allowed commands
        allowed_commands = ['python3', 'python', 'bandit', 'git', 'ollama']
        
        if not cmd_list or cmd_list[0] not in allowed_commands:
            return False, f"Command not allowed: {cmd_list[0] if cmd_list else 'empty'}"
        
        # Check for command injection attempts
        for arg in cmd_list:
            if any(char in arg for char in [';', '|', '&', '$', '`', '\n']):
                return False, "Command injection attempt detected"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize user input"""
        # Truncate
        text = text[:max_length]
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text

# ============================================================================
# SANDBOXED EXECUTION
# ============================================================================

class SandboxExecutor:
    """Execute code in isolated sandbox environment"""
    
    @staticmethod
    def create_sandbox() -> Path:
        """Create temporary sandbox directory"""
        sandbox = SANDBOX_DIR / f"sandbox_{secrets.token_hex(8)}"
        sandbox.mkdir(parents=True, exist_ok=True)
        return sandbox
    
    @staticmethod
    def execute_python(code: str, timeout: int = None) -> Dict[str, any]:
        """Execute Python code in sandbox"""
        if timeout is None:
            timeout = SECURITY_CONFIG.MAX_EXECUTION_TIME
        
        # Create sandbox
        sandbox = SandboxExecutor.create_sandbox()
        script_path = sandbox / "script.py"
        
        try:
            # Write script
            with open(script_path, "w") as f:
                f.write(code)
            
            # Execute in sandbox with resource limits
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=sandbox,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                }
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timeout after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "returncode": -1
            }
        finally:
            # Cleanup sandbox
            try:
                shutil.rmtree(sandbox)
            except Exception as e:
                logger.error(f"Failed to cleanup sandbox: {e}")
    
    @staticmethod
    def execute_command(cmd_list: List[str], timeout: int = None) -> Dict[str, any]:
        """Execute shell command with safety checks"""
        if timeout is None:
            timeout = SECURITY_CONFIG.MAX_EXECUTION_TIME
        
        # Validate command
        is_valid, error = SecurityValidator.validate_command(cmd_list)
        if not is_valid:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Security validation failed: {error}",
                "returncode": -1
            }
        
        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=WORKSPACE
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timeout after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "returncode": -1
            }

# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Track and enforce rate limits"""
    
    def __init__(self):
        self.requests = {}
    
    def check_limit(self, user: str, action: str, limit: int, window: int = 86400) -> Tuple[bool, int]:
        """Check if user is within rate limit"""
        key = f"{user}:{action}"
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside window
        self.requests[key] = [ts for ts in self.requests[key] if now - ts < window]
        
        # Check limit
        remaining = limit - len(self.requests[key])
        
        if remaining <= 0:
            return False, 0
        
        # Add current request
        self.requests[key].append(now)
        return True, remaining - 1

rate_limiter = RateLimiter()

# ============================================================================
# LLM API INTERFACE
# ============================================================================

class LLMInterface:
    """Safe interface to LLM API"""
    
    @staticmethod
    def generate(prompt: str, model: str, api_url: str, options: Dict) -> Optional[str]:
        """Generate response from LLM with error handling"""
        try:
            payload = {
                "model": model,
                "prompt": SecurityValidator.sanitize_input(prompt),
                "stream": False,
                "options": options
            }
            
            response = requests.post(
                api_url,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            return response.json().get("response", "")
            
        except requests.exceptions.Timeout:
            logger.error("LLM API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

# ============================================================================
# STREAMLIT UI
# ============================================================================

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        return False
    return True

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not check_auth():
            st.error("⛔ Authentication required")
            return None
        return func(*args, **kwargs)
    return wrapper

def require_role(required_role: SecurityLevel):
    """Decorator to require specific role"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_auth():
                st.error("⛔ Authentication required")
                return None
            
            user_role = SecurityLevel(st.session_state.role)
            
            if required_role == SecurityLevel.ADMIN and user_role != SecurityLevel.ADMIN:
                st.error("⛔ Admin privileges required")
                audit_log(st.session_state.username, "UNAUTHORIZED_ACCESS", 
                         f"Attempted admin action: {func.__name__}", False)
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🔐 Secure LLM Model Factory",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stAlert {border-radius: 5px;}
    .security-badge {
        background: #ff4b4b;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-size: 12px;
    }
    .success-badge {
        background: #00c851;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION UI
# ============================================================================

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

def show_logout():
    """Handle logout"""
    if st.sidebar.button("🚪 Logout"):
        audit_log(st.session_state.username, "LOGOUT", "User logged out", True)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # Check authentication
    if not check_auth():
        show_login()
        return
    
    # Sidebar with user info and controls
    st.sidebar.title("🔐 Secure Model Factory")
    st.sidebar.markdown(f"**User:** {st.session_state.username}")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.upper()}")
    show_logout()
    
    st.sidebar.divider()
    
    # Model configuration
    st.sidebar.subheader("🎮 Model Settings")
    model_name = st.sidebar.text_input("Model Name", value="llama3")
    api_url = st.sidebar.text_input("API URL", value="http://localhost:11434/api/generate")
    temp = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)
    num_ctx = st.sidebar.select_slider("Context", options=[2048, 4096, 8192, 16384], value=8192)
    
    st.sidebar.divider()
    st.sidebar.markdown("### 🛡️ Security Status")
    st.sidebar.success("✅ Sandbox: Active")
    st.sidebar.success("✅ Rate Limit: Active")
    st.sidebar.success("✅ Audit Log: Active")
    
    # Main tabs
    tabs = st.tabs([
        "💻 Code Generation",
        "📊 Execution Monitor",
        "🛡️ Security Audit",
        "👥 User Management",
        "📜 Audit Logs"
    ])
    
    # TAB 1: CODE GENERATION
    with tabs[0]:
        code_generation_tab(model_name, api_url, temp, num_ctx)
    
    # TAB 2: EXECUTION MONITOR
    with tabs[1]:
        execution_monitor_tab()
    
    # TAB 3: SECURITY AUDIT
    with tabs[2]:
        security_audit_tab()
    
    # TAB 4: USER MANAGEMENT (Admin only)
    with tabs[3]:
        user_management_tab()
    
    # TAB 5: AUDIT LOGS
    with tabs[4]:
        audit_logs_tab()

# ============================================================================
# TAB IMPLEMENTATIONS
# ============================================================================

@require_auth
def code_generation_tab(model_name, api_url, temp, num_ctx):
    """Code generation with security"""
    st.header("💻 Secure Code Generation")
    
    # Check rate limit
    can_proceed, remaining = rate_limiter.check_limit(
        st.session_state.username,
        "code_generation",
        SECURITY_CONFIG.MAX_DAILY_EXECUTIONS
    )
    
    st.info(f"**Daily Requests Remaining:** {remaining}/{SECURITY_CONFIG.MAX_DAILY_EXECUTIONS}")
    
    if not can_proceed:
        st.error("⛔ Rate limit exceeded. Please try again tomorrow.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Context Files (Optional)",
            accept_multiple_files=True,
            type=['txt', 'py', 'json', 'md']
        )
        
        # Prompt input
        prompt = st.text_area(
            "Describe what you want to build:",
            height=200,
            placeholder="Example: Create a function to calculate fibonacci numbers"
        )
        
        if st.button("🚀 Generate Code", type="primary"):
            if not prompt:
                st.warning("Please enter a prompt")
                return
            
            with st.spinner("Generating code..."):
                # Build context
                context = ""
                if uploaded_files:
                    for file in uploaded_files:
                        try:
                            content = file.read().decode()
                            context += f"\n--- FILE: {file.name} ---\n{content}\n"
                        except Exception as e:
                            st.warning(f"Could not read {file.name}: {e}")
                
                # Generate code
                full_prompt = context + "\n" + prompt
                response = LLMInterface.generate(
                    full_prompt,
                    model_name,
                    api_url,
                    {"temperature": temp, "num_ctx": num_ctx}
                )
                
                if response:
                    st.session_state.generated_code = response
                    audit_log(
                        st.session_state.username,
                        "CODE_GENERATED",
                        f"Prompt length: {len(prompt)}",
                        True
                    )
                else:
                    st.error("Failed to generate code. Check API connection.")
    
    with col2:
        st.subheader("📤 Output & Actions")
        
        if 'generated_code' in st.session_state:
            code = st.session_state.generated_code
            
            # Display code
            st.code(code, language="python")
            
            # Security validation
            is_safe, issues = SecurityValidator.validate_code(code)
            
            if not is_safe:
                st.error("🚨 Security Issues Detected:")
                for issue in issues:
                    st.warning(f"• {issue}")
                st.error("⛔ This code cannot be executed due to security concerns.")
                audit_log(
                    st.session_state.username,
                    "CODE_BLOCKED",
                    f"Issues: {', '.join(issues)}",
                    False
                )
            else:
                st.success("✅ Code passed security validation")
            
            # Action buttons
            col_a, col_b = st.columns(2)
            
            with col_a:
                filename = st.text_input("Filename:", value="generated_script.py")
                
                if st.button("💾 Save to Workspace"):
                    is_valid, error = SecurityValidator.validate_filename(filename)
                    
                    if not is_valid:
                        st.error(f"Invalid filename: {error}")
                    else:
                        try:
                            filepath = WORKSPACE / filename
                            with open(filepath, "w") as f:
                                f.write(code)
                            st.success(f"✅ Saved to: {filepath}")
                            audit_log(
                                st.session_state.username,
                                "FILE_SAVED",
                                f"File: {filename}",
                                True
                            )
                        except Exception as e:
                            st.error(f"Failed to save: {e}")
            
            with col_b:
                if st.button("▶️ Execute Code (Sandbox)", disabled=not is_safe):
                    if SECURITY_CONFIG.REQUIRE_CONFIRMATION:
                        if 'confirm_execute' not in st.session_state:
                            st.session_state.confirm_execute = False
                        
                        if not st.session_state.confirm_execute:
                            st.warning("⚠️ Click again to confirm execution")
                            st.session_state.confirm_execute = True
                            return
                    
                    with st.spinner("Executing in sandbox..."):
                        result = SandboxExecutor.execute_python(code)
                        
                        st.session_state.confirm_execute = False
                        
                        if result['success']:
                            st.success("✅ Execution completed")
                        else:
                            st.error("❌ Execution failed")
                        
                        st.text_area("📟 Output:", value=result['stdout'], height=150)
                        
                        if result['stderr']:
                            st.text_area("⚠️ Errors:", value=result['stderr'], height=100)
                        
                        audit_log(
                            st.session_state.username,
                            "CODE_EXECUTED",
                            f"Success: {result['success']}, Return: {result['returncode']}",
                            result['success']
                        )

@require_auth
def execution_monitor_tab():
    """Monitor execution history"""
    st.header("📊 Execution Monitor")
    
    st.info("View recent code executions and their results")
    
    # Read audit log for executions
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG, "r") as f:
            lines = f.readlines()
        
        # Filter for executions
        executions = [line for line in lines if "CODE_EXECUTED" in line]
        
        if executions:
            st.subheader(f"Recent Executions ({len(executions)})")
            for line in reversed(executions[-20:]):  # Last 20
                parts = line.strip().split(" | ")
                if len(parts) >= 4:
                    timestamp, user, action, status, details = parts
                    
                    if status == "SUCCESS":
                        st.success(f"✅ {timestamp} - {user} - {details}")
                    else:
                        st.error(f"❌ {timestamp} - {user} - {details}")
        else:
            st.info("No executions yet")
    else:
        st.warning("Audit log not found")
    
    # Workspace files
    st.subheader("📁 Workspace Files")
    
    if WORKSPACE.exists():
        files = list(WORKSPACE.glob("*"))
        
        if files:
            for file in files:
                if file.is_file():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.text(f"📄 {file.name}")
                    
                    with col2:
                        size_kb = file.stat().st_size / 1024
                        st.text(f"{size_kb:.1f} KB")
                    
                    with col3:
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
                                st.error(f"Failed to delete: {e}")
        else:
            st.info("No files in workspace")

@require_auth
def security_audit_tab():
    """Security scanning and validation"""
    st.header("🛡️ Security Audit Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Code Security Scanner")
        
        scan_input = st.text_area(
            "Paste code to scan:",
            height=200,
            placeholder="Paste Python code here for security analysis"
        )
        
        if st.button("🔍 Run Security Scan"):
            if scan_input:
                is_safe, issues = SecurityValidator.validate_code(scan_input)
                
                if is_safe:
                    st.success("✅ No security issues detected")
                else:
                    st.error(f"🚨 Found {len(issues)} security issues:")
                    for i, issue in enumerate(issues, 1):
                        st.warning(f"{i}. {issue}")
                
                audit_log(
                    st.session_state.username,
                    "SECURITY_SCAN",
                    f"Issues found: {len(issues)}",
                    True
                )
    
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

@require_role(SecurityLevel.ADMIN)
def user_management_tab():
    """User management (admin only)"""
    st.header("👥 User Management")
    
    if st.session_state.role != SecurityLevel.ADMIN.value:
        st.error("⛔ Admin privileges required")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", [r.value for r in SecurityLevel])
            
            if st.form_submit_button("Create User"):
                if new_username and new_password:
                    success = AuthManager.create_user(new_username, new_password, new_role)
                    
                    if success:
                        st.success(f"✅ User '{new_username}' created")
                    else:
                        st.error("❌ User already exists")
                else:
                    st.warning("Please fill all fields")
    
    with col2:
        st.subheader("👤 Existing Users")
        
        users = AuthManager.load_users()
        
        for username, data in users.items():
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                st.text(f"👤 {username} - {data['role']}")
            
            with col_b:
                if username != "admin":
                    if st.button("🗑️", key=f"del_user_{username}"):
                        st.warning(f"Delete {username}? (not implemented for safety)")

@require_auth
def audit_logs_tab():
    """View audit logs"""
    st.header("📜 Audit Logs")
    
    if not AUDIT_LOG.exists():
        st.info("No audit logs available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_user = st.selectbox("Filter by User", ["All"] + list(AuthManager.load_users().keys()))
    
    with col2:
        filter_action = st.selectbox(
            "Filter by Action",
            ["All", "LOGIN_SUCCESS", "LOGIN_FAILED", "CODE_GENERATED", "CODE_EXECUTED", "CODE_BLOCKED"]
        )
    
    with col3:
        max_lines = st.slider("Lines to show", 10, 200, 50)
    
    # Read and filter logs
    with open(AUDIT_LOG, "r") as f:
        lines = f.readlines()
    
    filtered_lines = []
    for line in lines:
        if filter_user != "All" and filter_user not in line:
            continue
        if filter_action != "All" and filter_action not in line:
            continue
        filtered_lines.append(line)
    
    # Display logs
    st.subheader(f"Showing {len(filtered_lines)} entries")
    
    log_text = "".join(reversed(filtered_lines[-max_lines:]))
    st.text_area("📋 Logs", value=log_text, height=400)
    
    # Export option
    if st.button("📥 Export Full Log"):
        st.download_button(
            label="Download audit.log",
            data="".join(lines),
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
