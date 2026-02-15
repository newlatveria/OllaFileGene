# 🔐 Secure LLM Model Factory

A production-ready, security-hardened application for AI-assisted code generation with comprehensive safety controls, authentication, sandboxing, and audit logging.

## ⚠️ IMPORTANT SECURITY NOTICE

This is a **completely rebuilt, secure version** of the original application. The original version contained **critical security vulnerabilities** and should **NEVER** be used in production.

## 🌟 Key Features

### 🛡️ Enterprise-Grade Security
- **Multi-Level Authentication** - Admin, User, and Read-Only roles
- **Sandboxed Code Execution** - Isolated environments for safe code running
- **Comprehensive Input Validation** - Blocks dangerous patterns and commands
- **Rate Limiting** - Prevents abuse with configurable limits
- **Audit Logging** - Complete trail of all actions and security events
- **Zero-Trust Architecture** - Validate everything, trust nothing

### 🚀 Powerful Features
- **AI Code Generation** - Generate code using local or remote LLM models
- **Security Scanner** - Real-time code analysis for vulnerabilities
- **Execution Monitor** - Track all code executions and results
- **File Management** - Secure workspace with validated access
- **User Management** - Create and manage users with role-based permissions
- **Real-Time Logs** - Monitor system activity and security events

### 🎯 Perfect For
- Development teams needing AI assistance
- Educational environments teaching secure coding
- Research projects with safety requirements
- Organizations requiring audit trails
- Anyone wanting secure LLM integration

## 🚨 What Was Fixed from Original

### Critical Vulnerabilities Addressed

| Original Issue | Security Fix |
|---------------|--------------|
| ❌ Arbitrary code execution | ✅ Sandboxed execution with isolation |
| ❌ No authentication | ✅ Multi-level auth with session management |
| ❌ Command injection | ✅ Input validation and command whitelisting |
| ❌ Trivial security bypass | ✅ Comprehensive pattern blocking |
| ❌ Unrestricted file access | ✅ Path validation and permission controls |
| ❌ No audit trail | ✅ Complete audit logging |
| ❌ No rate limiting | ✅ Per-user rate limiting |
| ❌ Direct shell access | ✅ Controlled command execution |

## 📸 Screenshots

### Login Screen
```
🔐 Secure LLM Model Factory
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Authentication Required

Username: [admin         ]
Password: [••••••••      ]
         [🔓 Login]
```

### Main Interface
```
💻 Code Generation    📊 Monitor    🛡️ Security    👥 Users    📜 Logs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Input                          📤 Output
┌─────────────────────┐          ┌─────────────────────┐
│ What to build?      │          │ Generated Code      │
│                     │          │                     │
│ [Upload Files]      │          │ ✅ Security: PASS   │
│                     │          │                     │
│ [🚀 Generate Code]  │          │ [💾 Save] [▶️ Run] │
└─────────────────────┘          └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 4GB RAM minimum
- Linux/macOS/Windows with WSL2

### Installation

```bash
# 1. Create project directory
mkdir secure-llm-factory && cd secure-llm-factory

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install streamlit requests

# 4. Run application
streamlit run llm_model_factory_secure.py
```

### First Login
```
Username: admin
Password: admin123
```
**⚠️ Change this password immediately!**

## 📖 Usage Guide

### 1. Code Generation

```python
# In the application:
1. Go to "Code Generation" tab
2. Enter your prompt: "Create a function to calculate fibonacci"
3. Click "🚀 Generate Code"
4. Review the generated code
5. Check security validation results
6. Save or Execute (if safe)
```

### 2. Security Validation

All code is automatically scanned for:
- Dangerous system calls
- File system manipulation
- Privilege escalation attempts
- Path traversal attacks
- Suspicious imports
- Command injection

### 3. Sandboxed Execution

```python
# Code runs in isolated sandbox:
- Temporary directory created
- Limited environment variables
- No access to parent filesystem
- Automatic cleanup after execution
- 30-second timeout
```

### 4. User Management (Admin Only)

```python
# Create new user:
1. Go to "User Management" tab
2. Enter username and password
3. Select role: admin/user/readonly
4. Click "Create User"
```

### 5. Audit Log Review

```python
# Monitor security events:
1. Go to "Audit Logs" tab
2. Filter by user or action
3. Review security incidents
4. Export logs if needed
```

## 🔧 Configuration

### Security Settings

```python
# Edit in llm_model_factory_secure.py:

SECURITY_CONFIG = SecurityConfig(
    MAX_FILE_SIZE_MB=10,           # Max upload size
    MAX_EXECUTION_TIME=30,         # Execution timeout (seconds)
    MAX_DAILY_EXECUTIONS=100,      # Rate limit per user
    REQUIRE_CONFIRMATION=True,     # Double-confirm dangerous actions
    ENABLE_AUDIT_LOG=True,        # Enable logging
    SANDBOX_ENABLED=True          # Enforce sandboxing
)
```

### LLM Configuration

**Option 1: Local Ollama**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3

# In app sidebar:
API URL: http://localhost:11434/api/generate
Model: llama3
```

**Option 2: External API**
```python
# In app sidebar:
API URL: https://your-api-endpoint.com
Model: your-model-name
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│  (Authentication Layer)                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           Security Validation                    │
│  • Input Sanitization                           │
│  • Pattern Matching                             │
│  • Command Validation                           │
│  • File Permission Checks                       │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Sandbox Executor                        │
│  • Isolated Filesystem                          │
│  • Resource Limits                              │
│  • Timeout Enforcement                          │
│  • Auto Cleanup                                 │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Audit Logger                          │
│  • All Actions Logged                           │
│  • Security Events Tracked                      │
│  • Compliance Ready                             │
└─────────────────────────────────────────────────┘
```

## 📊 Security Validation

### Blocked Patterns

The system blocks code containing:
```python
# Dangerous commands
rm -rf, sudo, chmod 777, shutdown, reboot

# Dangerous Python
eval(), exec(), __import__, os.system()
subprocess (except safe calls)

# File operations
open() in write mode, shutil.rmtree()

# System access
/etc/, /sys/, /proc/, ../
```

### Example Validation

```python
# ❌ BLOCKED:
code = """
import os
os.system('rm -rf /')
"""
# Result: Security Issues Detected
# - Dangerous import: os
# - Blocked pattern: rm -rf

# ✅ ALLOWED:
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
# Result: Code passed security validation
```

## 🐳 Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Access application
http://localhost:8501
```

See `INSTALLATION.md` for complete deployment guide.

## 📁 Project Structure

```
secure-llm-factory/
├── llm_model_factory_secure.py  # Main application
├── requirements.txt              # Python dependencies
├── workspace/                    # User workspace (isolated)
├── sandbox/                      # Execution sandboxes (temp)
├── logs/                        # Application and audit logs
│   ├── audit.log               # Security audit trail
│   └── app.log                 # Application logs
├── config/                      # Configuration files
│   └── users.json              # User database
├── SECURITY.md                  # Security documentation
├── INSTALLATION.md              # Deployment guide
└── README.md                    # This file
```

## 🔐 Security Best Practices

### For Administrators
1. ✅ Change default password immediately
2. ✅ Review audit logs regularly
3. ✅ Update blocked patterns as needed
4. ✅ Implement regular backups
5. ✅ Use HTTPS in production
6. ✅ Enable firewall rules
7. ✅ Monitor resource usage
8. ✅ Keep dependencies updated

### For Users
1. ✅ Use strong passwords
2. ✅ Review generated code before execution
3. ✅ Report suspicious patterns
4. ✅ Don't share credentials
5. ✅ Clean up workspace files
6. ✅ Understand rate limits

## 📋 Security Checklist

```
Pre-Deployment:
□ Default password changed
□ Security configuration reviewed
□ Firewall rules configured
□ HTTPS/SSL enabled
□ Backup system tested

Post-Deployment:
□ Monitor audit logs
□ Review blocked attempts
□ Check resource usage
□ Verify user permissions
□ Test security controls

Weekly:
□ Review audit logs
□ Check for updates
□ Backup user database
□ Monitor disk space

Monthly:
□ Security audit
□ Update dependencies
□ Review user accounts
□ Test incident response
```

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip list | grep streamlit

# Check logs
tail -f logs/app.log
```

### Login Issues
```bash
# Reset admin password (emergency)
rm config/users.json
# Restart app - default credentials restored
```

### Execution Timeouts
```python
# Increase timeout in config:
SECURITY_CONFIG.MAX_EXECUTION_TIME = 60  # seconds
```

### Rate Limit Hit
```python
# Check remaining requests:
# Shown in UI: "Daily Requests Remaining: X/100"

# Reset (admin):
# Delete rate limiter state (requires restart)
```

## 📞 Support & Contributing

### Reporting Security Issues
**DO NOT** post security vulnerabilities publicly!

Email: security@your-org.com

Include:
- Detailed description
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

### Feature Requests
Open an issue on GitHub with:
- Clear description
- Use case
- Expected behavior

### Contributing
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Streamlit team for the framework
- Ollama for local LLM hosting
- Security community for best practices
- All contributors and testers

## 📚 Additional Documentation

- [SECURITY.md](SECURITY.md) - Comprehensive security guide
- [INSTALLATION.md](INSTALLATION.md) - Deployment instructions
- [API.md](API.md) - API documentation (if applicable)

## 🔄 Version History

### v2.0.0 (Current) - Secure Release
- ✅ Complete security overhaul
- ✅ Authentication system
- ✅ Sandboxed execution
- ✅ Audit logging
- ✅ Rate limiting
- ✅ Input validation
- ✅ Production ready

### v1.0.0 - Original Release
- ⚠️ **INSECURE** - Do not use
- Multiple critical vulnerabilities
- No authentication
- Arbitrary code execution
- Command injection risks

## ⚖️ Disclaimer

This software is provided "as is" without warranty. While comprehensive security measures have been implemented, no system is 100% secure. Users are responsible for:
- Proper configuration
- Regular security audits
- Keeping software updated
- Following security best practices
- Compliance with applicable laws

## 🎯 Roadmap

### Planned Features
- [ ] Two-factor authentication (2FA)
- [ ] LDAP/OAuth integration
- [ ] Enhanced monitoring dashboard
- [ ] Automated security scanning
- [ ] Container orchestration support
- [ ] API rate limiting per endpoint
- [ ] Advanced analytics
- [ ] Export/import functionality

### Under Consideration
- [ ] GraphQL API
- [ ] Mobile app
- [ ] Plugin system
- [ ] Multi-tenancy support
- [ ] Advanced role permissions
- [ ] Real-time collaboration

---

## 🚀 Get Started Now

```bash
git clone https://github.com/your-org/secure-llm-factory
cd secure-llm-factory
pip install -r requirements.txt
streamlit run llm_model_factory_secure.py
```

**Default Login:**
- Username: `admin`
- Password: `admin123`

**First Steps:**
1. Log in with default credentials
2. Change admin password
3. Configure LLM API
4. Generate your first secure code!

---

**Built with ❤️ and 🔒 by the Security Team**

**Questions?** security@your-org.com  
**Website:** https://your-org.com  
**Docs:** https://docs.your-org.com  
**Status:** https://status.your-org.com

---

*Last Updated: February 2024 | Version 2.0.0*
