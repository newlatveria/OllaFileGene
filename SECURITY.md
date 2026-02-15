# Security Documentation - Secure LLM Model Factory

## 🛡️ Security Features Overview

### 1. Authentication & Authorization

**Multi-Level Access Control:**
- **Admin**: Full system access, user management, all operations
- **User**: Code generation, execution, file management
- **Readonly**: View-only access to logs and monitoring

**Security Features:**
- SHA-256 password hashing with salt
- Session-based authentication
- Secure password storage in JSON database
- Audit logging of all authentication attempts
- Automatic session timeout (configurable)

**Default Credentials:**
```
Username: admin
Password: admin123
```
⚠️ **IMPORTANT**: Change default password immediately after first login!

### 2. Sandboxed Execution

**Isolation Mechanism:**
- Each code execution runs in a temporary, isolated directory
- No access to parent filesystem
- Limited environment variables
- Automatic cleanup after execution

**Resource Limits:**
- Maximum execution time: 30 seconds (configurable)
- Maximum file size: 10 MB
- Memory and CPU limits (OS-level, requires additional setup)

**Process Isolation:**
```python
# Each execution creates isolated sandbox:
sandbox_id = secrets.token_hex(8)
sandbox_path = /sandbox/sandbox_{id}/
# Cleaned up after execution
```

### 3. Input Validation & Sanitization

**Code Validation:**
Blocks dangerous patterns including:
- Shell command execution (`subprocess`, `os.system`)
- File system manipulation (`rm -rf`, `shutil.rmtree`)
- Privilege escalation (`sudo`, `chmod 777`)
- System commands (`shutdown`, `reboot`)
- Dangerous imports (`pickle`, `ctypes`)
- Path traversal attempts (`../`)
- Access to system directories (`/etc/`, `/sys/`, `/proc/`)

**Filename Validation:**
- Only alphanumeric, dash, underscore, and dot allowed
- Strips path components (prevents traversal)
- Whitelist of allowed extensions: `.py`, `.txt`, `.json`, `.yaml`, `.md`
- Maximum filename length enforced

**Input Sanitization:**
- Removes control characters
- Truncates to maximum length (10,000 chars)
- SQL injection prevention (N/A - no database)
- XSS prevention (minimal risk in Streamlit)

### 4. Rate Limiting

**Protection Against Abuse:**
- 100 code generations per user per day (configurable)
- Per-user, per-action tracking
- 24-hour sliding window
- Configurable limits per role

**Implementation:**
```python
can_proceed, remaining = rate_limiter.check_limit(
    username, 
    action, 
    limit=100, 
    window=86400
)
```

### 5. Comprehensive Audit Logging

**All Actions Logged:**
- Login attempts (success/failure)
- Code generation requests
- Code execution (with results)
- Security blocks
- File operations
- User management changes
- Administrative actions

**Log Format:**
```
2024-02-15T10:30:45 | username | ACTION_TYPE | SUCCESS/FAILURE | details
```

**Log Locations:**
- Audit log: `logs/audit.log`
- Application log: `logs/app.log`
- Execution logs: Sandbox-specific

### 6. Security Monitoring

**Real-Time Security Features:**
- Security validation before every execution
- Pattern matching for malicious code
- Blocked code tracking
- Failed login monitoring
- Suspicious activity detection

**Security Dashboard:**
- Total actions tracked
- Failed action count
- Blocked code attempts
- Success rate metrics

### 7. File System Security

**Protected Directories:**
- Read-only: `/etc/`, `/sys/`, `/proc/`
- Isolated: Sandbox directories (auto-cleanup)
- Controlled: Workspace directory (validated access)
- Secure: Config and user database

**File Operation Security:**
- All file writes go through validation
- No direct file system access from generated code
- Automatic cleanup of temporary files
- Size limits on uploaded files

## 🔒 Security Best Practices

### For Administrators

1. **Change Default Password Immediately**
   ```python
   # In User Management tab, change admin password
   ```

2. **Regular Audit Log Review**
   - Check for failed login attempts
   - Monitor blocked code patterns
   - Review unusual activity

3. **User Management**
   - Assign minimum required privileges
   - Regularly review user accounts
   - Remove inactive users

4. **System Updates**
   - Keep Python packages updated
   - Monitor security advisories
   - Apply patches promptly

5. **Backup Strategy**
   - Regular backups of user database
   - Audit log archival
   - Workspace file backups

### For Users

1. **Password Security**
   - Use strong, unique passwords
   - Change password regularly
   - Never share credentials

2. **Code Review**
   - Review generated code before execution
   - Understand what code does
   - Report suspicious patterns

3. **Data Handling**
   - Don't upload sensitive data
   - Clean up workspace files
   - Use appropriate file permissions

## 🚨 Threat Model & Mitigations

### Identified Threats

| Threat | Risk Level | Mitigation |
|--------|-----------|------------|
| Arbitrary Code Execution | HIGH | Sandboxing, validation, pattern blocking |
| Command Injection | HIGH | Input sanitization, command whitelist |
| Path Traversal | MEDIUM | Filename validation, path sanitization |
| Brute Force Login | MEDIUM | Rate limiting, audit logging |
| Resource Exhaustion | MEDIUM | Execution timeouts, resource limits |
| Data Exfiltration | LOW | Sandboxing, network restrictions |
| Privilege Escalation | LOW | Role-based access control |

### Additional Security Layers (Recommended)

1. **Network Security**
   - Firewall rules
   - VPN access only
   - TLS/HTTPS encryption
   - API rate limiting at network level

2. **Container Security** (Docker)
   ```dockerfile
   # Run application in Docker container
   # Provides additional isolation layer
   ```

3. **OS-Level Security**
   - AppArmor/SELinux profiles
   - User namespace isolation
   - cgroups for resource limits

4. **Monitoring & Alerting**
   - SIEM integration
   - Real-time alerting on security events
   - Automated response to threats

## 📊 Security Configuration

### SecurityConfig Class

```python
class SecurityConfig:
    MAX_FILE_SIZE_MB = 10              # Maximum upload size
    MAX_EXECUTION_TIME = 30            # Seconds
    ALLOWED_FILE_EXTENSIONS = [...]    # Whitelist
    BLOCKED_PATTERNS = [...]           # Regex patterns
    MAX_DAILY_EXECUTIONS = 100         # Per user
    REQUIRE_CONFIRMATION = True        # Double-confirm dangerous actions
    ENABLE_AUDIT_LOG = True           # Logging on/off
    SANDBOX_ENABLED = True            # Sandbox enforcement
```

### Customization

Edit these values in the configuration section:

```python
SECURITY_CONFIG = SecurityConfig()

# Adjust as needed:
SECURITY_CONFIG.MAX_EXECUTION_TIME = 60  # Increase timeout
SECURITY_CONFIG.MAX_DAILY_EXECUTIONS = 50  # Reduce limit
```

## 🔍 Security Testing

### Recommended Tests

1. **Authentication Tests**
   - Invalid credentials
   - SQL injection in login
   - Session hijacking attempts

2. **Input Validation Tests**
   ```python
   # Test blocked patterns
   dangerous_code = "import os; os.system('rm -rf /')"
   # Should be blocked
   ```

3. **Sandbox Escape Tests**
   - Path traversal attempts
   - Symlink attacks
   - Resource exhaustion

4. **Authorization Tests**
   - Role escalation attempts
   - Unauthorized access to admin functions

### Security Checklist

- [ ] Default password changed
- [ ] Audit logs reviewed
- [ ] Rate limits configured
- [ ] User roles assigned correctly
- [ ] Backup system in place
- [ ] Monitoring enabled
- [ ] Security patterns updated
- [ ] Documentation read
- [ ] Incident response plan created

## 🚑 Incident Response

### Security Incident Procedure

1. **Detect**
   - Monitor audit logs
   - Check security alerts
   - Review blocked attempts

2. **Contain**
   - Disable affected user accounts
   - Block suspicious IP addresses
   - Isolate compromised components

3. **Investigate**
   - Review audit logs thoroughly
   - Identify attack vector
   - Assess damage

4. **Remediate**
   - Patch vulnerabilities
   - Reset compromised credentials
   - Update security patterns

5. **Learn**
   - Document incident
   - Update procedures
   - Improve defenses

### Emergency Contacts

```
Security Team: security@your-org.com
Admin Contact: admin@your-org.com
Incident Hotline: +1-XXX-XXX-XXXX
```

## 📝 Compliance & Legal

### Data Protection
- User credentials stored hashed
- No PII collected beyond username
- Audit logs contain action history
- Right to data deletion supported

### Responsibility
- Admin responsible for secure configuration
- Users responsible for code they generate
- Organization responsible for deployment security
- Regular security audits recommended

## 🔄 Version History

**v2.0.0 - Secure Release**
- Complete security overhaul
- Authentication system
- Sandboxed execution
- Comprehensive audit logging
- Rate limiting
- Input validation
- Security monitoring

**v1.0.0 - Original Release**
- Basic functionality
- ⚠️ INSECURE - Do not use

## 📞 Support & Reporting

### Security Issues
To report security vulnerabilities:
1. Do NOT post publicly
2. Email: security@your-org.com
3. Include detailed description
4. Proof of concept if available

### Feature Requests
- Use GitHub issues
- Tag with 'security' for security-related features

---

**Last Updated:** February 2024  
**Version:** 2.0.0  
**Status:** Production Ready with Proper Configuration
