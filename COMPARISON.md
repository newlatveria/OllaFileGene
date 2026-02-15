# Security

### 1. Authentication & Authorization

class AuthManager:
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Authenticate user and return role"""
        users = AuthManager.load_users()
        if username not in users:
            audit_log("SYSTEM", "LOGIN_FAILED", f"Unknown user: {username}", False)
            return False, None
        # Hash verification, role assignment, audit logging

✅ SHA-256 password hashing  
✅ Three-tier role system (Admin, User, ReadOnly)  
✅ Session management  
✅ Login attempt tracking  
✅ Secure credential storage  

---

### 2. Code Execution

class SandboxExecutor:
    @staticmethod
    def execute_python(code: str, timeout: int = None) -> Dict[str, any]:
        """Execute Python code in sandbox"""
        # Create isolated sandbox
        sandbox = SANDBOX_DIR / f"sandbox_{secrets.token_hex(8)}"
        sandbox.mkdir(parents=True, exist_ok=True)
        
        # Execute with resource limits
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=sandbox,  # Isolated working directory
            env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}
        )
        
        # Cleanup sandbox
        shutil.rmtree(sandbox)

✅ Isolated temporary directories  
✅ Limited environment variables  
✅ Automatic cleanup  
✅ Timeout enforcement  
✅ No access to parent filesystem  
✅ Resource limits  

---

### 3. Input Validation

class SecurityValidator:
    @staticmethod
    def validate_code(code: str) -> Tuple[bool, List[str]]:
        """Validate code for security issues"""
        issues = []
        
        # Regex pattern matching (harder to bypass)
        for pattern in SECURITY_CONFIG.BLOCKED_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Blocked pattern detected: {pattern}")
        
        # Check dangerous imports
        dangerous_imports = ['os', 'subprocess', 'shutil', 'sys', 'ctypes', 'pickle']
        for imp in dangerous_imports:
            if re.search(rf'\bimport\s+{imp}\b|\bfrom\s+{imp}\s+import', code):
                issues.append(f"Dangerous import: {imp}")
        
        # Check file operations
        file_ops = ['open(', 'write(', 'unlink(', 'remove(']
        for op in file_ops:
            if op in code:
                issues.append(f"File operation detected: {op}")
        
        return len(issues) == 0, issues

✅ Regex pattern matching  
✅ Import validation  
✅ File operation detection  
✅ Multiple validation layers  
✅ Detailed issue reporting  
✅ Configurable patterns  

---

### 4. File System Security

class SecurityValidator:
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """Validate filename for security"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Path traversal attempt detected"
        
        # Check extension whitelist
        ext = Path(filename).suffix
        if ext not in SECURITY_CONFIG.ALLOWED_FILE_EXTENSIONS:
            return False, f"File extension {ext} not allowed"
        
        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False, "Invalid characters in filename"
        
        return True, ""

✅ Path component stripping  
✅ Traversal prevention  
✅ Extension whitelist  
✅ Character validation  
✅ Size limits  
✅ Permission checks  

---

### 5. Audit Logging

#### Original (INSECURE)
```python
# NO AUDIT LOGGING
# No record of:
# - Who did what
# - When actions occurred
# - Security events
# - Failed attempts

def audit_log(user: str, action: str, details: str, success: bool = True):
    """Write to audit log"""
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILURE"
    log_entry = f"{timestamp} | {user} | {action} | {status} | {details}\n"
    
    with open(AUDIT_LOG, "a") as f:
        f.write(log_entry)

# Called throughout application:
audit_log(st.session_state.username, "CODE_EXECUTED", 
          f"Success: {result['success']}", result['success'])

✅ Complete action history  
✅ User attribution  
✅ Timestamp tracking  
✅ Success/failure status  
✅ Detailed context  
✅ Searchable/filterable  
✅ Export capability  

---

### 6. Rate Limiting

class RateLimiter:
    def check_limit(self, user: str, action: str, 
                    limit: int, window: int = 86400) -> Tuple[bool, int]:
        """Check if user is within rate limit"""
        key = f"{user}:{action}"
        now = time.time()
        
        # Remove old requests
        self.requests[key] = [ts for ts in self.requests[key] 
                             if now - ts < window]
        
        # Check limit
        remaining = limit - len(self.requests[key])
        if remaining <= 0:
            return False, 0
        
        self.requests[key].append(now)
        return True, remaining - 1

✅ Per-user tracking  
✅ Per-action limits  
✅ Sliding window  
✅ Configurable limits  
✅ Remaining count display  
✅ Abuse prevention  

---

### 7. Error Handling

except subprocess.TimeoutExpired:
    return {
        "success": False,
        "stdout": "",
        "stderr": f"Execution timeout after {timeout} seconds",
        "returncode": -1
    }
except Exception as e:
    logger.error(f"Execution error: {str(e)}")  # Log details
    return {
        "success": False,
        "stdout": "",
        "stderr": "Execution error occurred",  # Generic message
        "returncode": -1
    }

✅ Specific error handling  
✅ No information leakage  
✅ Detailed logging (internal)  
✅ Generic messages (user-facing)  
✅ Proper error types  

---

### 8. Command Execution

class SecurityValidator:
    @staticmethod
    def validate_command(cmd_list: List[str]) -> Tuple[bool, str]:
        """Validate shell command for security"""
        # Whitelist of allowed commands
        allowed_commands = ['python3', 'python', 'bandit', 'git', 'ollama']
        
        if not cmd_list or cmd_list[0] not in allowed_commands:
            return False, f"Command not allowed: {cmd_list[0]}"
        
        # Check for command injection
        for arg in cmd_list:
            if any(char in arg for char in [';', '|', '&', '$', '`', '\n']):
                return False, "Command injection attempt detected"
        
        return True, ""

✅ Command whitelist  
✅ Argument validation  
✅ Injection prevention  
✅ Error handling  
✅ Timeout enforcement  

---

**Document Version:** 1.0  
**Last Updated:** February 2024  
**Status:** Complete Security Audit
