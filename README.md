# 🔐 Secure LLM Model Factory

> **Production-ready AI application suite with enterprise-grade security, model management, and RAG capabilities**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/yourusername/llm-factory)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Security](#security)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🎯 Overview

**Secure LLM Model Factory** is a comprehensive, production-ready application suite designed for secure interaction with Large Language Models (LLMs) through Ollama. Built with enterprise-grade security practices, the application provides a robust framework for AI-powered code generation, interactive chat, model management, and Retrieval Augmented Generation (RAG) capabilities.

### Why Choose LLM Factory?

- **🔐 Security-First Design**: Built with zero-trust architecture and comprehensive input validation
- **🎨 User-Friendly Interface**: Intuitive Streamlit-based UI requiring no technical expertise
- **🤖 Complete Model Control**: Download, manage, and switch between models seamlessly
- **📚 RAG Integration**: Leverage your own documents to enhance AI responses
- **🛡️ Production-Ready**: Includes authentication, audit logging, and role-based access control
- **📦 Easy Deployment**: Multiple installation methods from single-command to full Docker orchestration

### Key Statistics

- **30+ Security Vulnerabilities Fixed** from original implementation
- **Zero Known Critical Vulnerabilities** in current release
- **7 Integrated Tabs** for complete functionality
- **3 Deployment Options** (Python, Docker, Systemd)
- **Multi-Format RAG Support** (PDF, DOCX, TXT, MD, JSON)
- **Automatic Model Detection** from Ollama installation

---

## ✨ Features

### Core Capabilities

#### 💬 Interactive Chat Interface
- Full-context conversational AI with message history
- Support for multiple Ollama models with hot-swapping
- Customizable system prompts for behavior modification
- Message regeneration and conversation export
- RAG-enhanced responses using uploaded documents
- Real-time response streaming

#### 🤖 Model Management
- **One-Click Downloads**: Install popular models (llama3, mistral, codellama, phi3, gemma2, qwen2)
- **Custom Model Support**: Download any Ollama community model
- **Model Information**: Detailed specs, parameters, and architecture
- **Storage Management**: View sizes and delete unused models
- **Auto-Detection**: Automatically discovers installed models
- **Version Control**: Support for specific model versions

#### 📚 RAG (Retrieval Augmented Generation)
- **Multi-Format Support**: PDF, DOCX, TXT, MD, JSON document processing
- **Intelligent Search**: Keyword-based relevance scoring with context extraction
- **Seamless Integration**: Toggle RAG on/off during conversations
- **Document Management**: Upload, view, delete, and organize knowledge base
- **Context Indicators**: Visual feedback showing when RAG is active
- **Batch Processing**: Upload multiple documents simultaneously

#### 💻 Code Generation
- **Multi-Language Support**: Python, JavaScript, Java, C++, Go, Rust, TypeScript, PHP
- **Security Scanning**: Automatic validation of generated code
- **Syntax Highlighting**: Language-specific code display
- **Export Options**: Save to workspace or download directly
- **Template Support**: Pre-configured prompts for common tasks

#### 🛡️ Security Features
- **Multi-Level Authentication**: Admin, User, and Read-Only roles
- **Sandboxed Execution**: Isolated environment for code running
- **Input Validation**: Comprehensive sanitization and pattern blocking
- **Audit Logging**: Complete trail of all actions and security events
- **Rate Limiting**: Configurable request limits per user
- **Session Management**: Secure token-based sessions
- **Password Hashing**: SHA-256 with salts

### Version Comparison

| Feature | Secure Edition | Enhanced Edition | Ultimate Edition |
|---------|---------------|------------------|------------------|
| **Authentication** | ✅ | ✅ | ✅ |
| **Security Scanning** | ✅ | ✅ | ✅ |
| **Code Generation** | ✅ | ✅ | ✅ |
| **Chat Interface** | ❌ | ✅ | ✅ |
| **Model Dropdown** | ⚠️ Manual | ✅ Auto | ✅ Auto |
| **Conversation History** | ❌ | ✅ | ✅ |
| **Model Download** | ❌ | ❌ | ✅ |
| **Model Management** | ❌ | ❌ | ✅ |
| **RAG System** | ❌ | ❌ | ✅ |
| **Document Upload** | ❌ | ❌ | ✅ |
| **Recommended For** | Learning | Interactive Use | Production |

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (Streamlit Web UI)                        │
├─────────────────────────────────────────────────────────────┤
│                   Authentication Layer                       │
│              (Session Management & RBAC)                     │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │   Chat   │  Model   │   RAG    │   Code   │ Security │  │
│  │ Interface│ Manager  │  System  │   Gen    │  Scanner │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                           │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │   Ollama     │   Security   │   File Management    │    │
│  │   Manager    │   Validator  │   & Storage          │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                       Data Layer                             │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │   User DB    │   RAG Docs   │   Audit Logs         │    │
│  │   (JSON)     │   (Files)    │   (Text)             │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Ollama Service (localhost:11434)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Request
     │
     ▼
┌─────────────────┐
│ Authentication  │──────► Check Session
└────────┬────────┘       Verify Role
         │
         ▼
┌─────────────────┐
│ Input Validator │──────► Sanitize Input
└────────┬────────┘       Check Patterns
         │
         ▼
┌─────────────────┐       Yes ┌──────────────┐
│ RAG Enabled?    │───────────►│ RAG Manager  │
└────────┬────────┘            │ Search Docs  │
         │ No                  │ Extract Ctx  │
         │                     └──────┬───────┘
         │                            │
         │◄───────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Ollama Manager  │──────► Generate Response
└────────┬────────┘       Model Inference
         │
         ▼
┌─────────────────┐
│ Security Check  │──────► Validate Output
└────────┬────────┘       Scan for Issues
         │
         ▼
┌─────────────────┐
│ Audit Logger    │──────► Record Action
└────────┬────────┘       Store Event
         │
         ▼
    Response to User
```

### Directory Structure

```
llm-model-factory/
├── llm_model_factory_ultimate.py    # Main application (Ultimate Edition)
├── llm_model_factory_enhanced.py    # Enhanced Edition
├── llm_model_factory_secure.py      # Secure Edition
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container configuration
├── docker-compose.yml                # Multi-container orchestration
├── start.sh                          # Installation & start script
├── menu.sh                           # Interactive management menu
├── quick-install.sh                  # Fast installation
├── test.sh                           # Validation test suite
├── workspace/                        # User workspace files
├── sandbox/                          # Isolated execution environment
├── logs/                            # Application & audit logs
│   ├── app.log                      # General application logs
│   ├── audit.log                    # Security audit trail
│   └── install.log                  # Installation logs
├── config/                          # Configuration files
│   ├── users.json                   # User database (hashed passwords)
│   ├── chat_history/                # Saved conversations
│   ├── rag_documents/               # RAG document storage
│   └── embeddings/                  # Vector embeddings (future)
└── docs/                            # Documentation
    ├── README.md                    # This file
    ├── SECURITY.md                  # Security documentation
    ├── INSTALLATION.md              # Installation guide
    ├── ULTIMATE_GUIDE.md            # Feature guide
    ├── QUICKSTART.md                # Quick reference
    └── API.md                       # API documentation
```

---

## 🚀 Installation

### Prerequisites

#### Required
- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Disk Space**: 2GB minimum (10GB+ recommended with models)
- **Memory**: 4GB RAM minimum (8GB+ recommended)

#### Optional
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for orchestrated deployment)
- **Git**: For version control integration
- **Ollama**: Automatically installed by scripts, or install manually

### System Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| **Ubuntu 20.04+** | ✅ Tested | Recommended |
| **Ubuntu 22.04** | ✅ Tested | Recommended |
| **Debian 11+** | ✅ Compatible | |
| **CentOS 8+** | ✅ Compatible | |
| **macOS 10.15+** | ✅ Compatible | Intel & Apple Silicon |
| **Windows 10+** | ✅ WSL2 | Native support planned |
| **Docker** | ✅ All Platforms | Recommended for production |

### Installation Methods

#### Method 1: Quick Install (Recommended for First-Time Users)

The fastest way to get started:

```bash
# Download the quick installer
chmod +x quick-install.sh

# Run installation
./quick-install.sh

# Start the application
source venv/bin/activate
streamlit run llm_model_factory_ultimate.py
```

**Time**: ~2-3 minutes

#### Method 2: Interactive Menu (Recommended for Production)

Full-featured installation with guided setup:

```bash
# Make menu executable
chmod +x menu.sh

# Launch interactive menu
./menu.sh

# Follow prompts:
# 1. Check System Requirements
# 2. Installation Options → Complete Installation
# 3. Configuration → Security Setup
# 4. Start Application
```

**Time**: ~5-30 minutes (depending on options)

#### Method 3: Manual Installation (For Developers)

Complete control over the installation process:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p workspace sandbox logs config config/chat_history config/rag_documents

# Set permissions
chmod 700 config

# Start application
streamlit run llm_model_factory_ultimate.py
```

**Time**: ~5 minutes

#### Method 4: Docker Installation (Recommended for Production)

Containerized deployment with isolation:

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
# http://localhost:8501
```

**Time**: ~10 minutes

#### Method 5: Advanced Start Script

Automated installation with configuration options:

```bash
# Make executable
chmod +x start.sh

# Run with auto-install
./start.sh

# Choose from menu:
# 1. Start Application (auto-installs dependencies)
# 2. Start with Docker
# 3. Start Ollama Service
# 4. Start Everything (App + Ollama)
```

**Time**: ~2-5 minutes

### Post-Installation

After installation, verify everything is working:

```bash
# Run test suite
./test.sh

# Expected output:
# Total Tests:    16
# Passed:         14-16
# Failed:         0
# Success Rate:   95-100%
```

---

## ⚡ Quick Start

### 1. First Launch

```bash
# Start the application
streamlit run llm_model_factory_ultimate.py

# Application opens at: http://localhost:8501
```

### 2. Initial Login

```
Username: admin
Password: admin123
```

⚠️ **CRITICAL**: Change the default password immediately after first login!

### 3. Download Your First Model

```
Navigate to: 🤖 Model Manager → 📥 Download Models
Select: phi3 (Fastest, 2.2GB)
Click: 📥 Download Selected Model
Wait: 2-5 minutes (depending on connection)
```

### 4. Start Chatting

```
Select Model: phi3 (from sidebar dropdown)
Navigate to: 💬 Chat Interface
Type: "Hello! Can you help me with Python?"
Click: 📤 Send
```

### 5. Try RAG (Optional)

```
Navigate to: 📚 RAG Documents → 📤 Upload
Upload: Your PDF or text documents
Click: Process Uploaded Files
Enable: Toggle "🔍 Enable RAG" in sidebar
Chat: Ask questions about your documents
```

### Quick Reference Commands

```bash
# Start application
streamlit run llm_model_factory_ultimate.py

# Start with specific port
streamlit run llm_model_factory_ultimate.py --server.port 8502

# Start in background
nohup streamlit run llm_model_factory_ultimate.py > logs/app.log 2>&1 &

# Stop application
pkill -f streamlit

# View logs
tail -f logs/app.log
tail -f logs/audit.log

# Check status
ps aux | grep streamlit
```

---

## 📖 Usage Guide

### User Interface Overview

The application features 7 main tabs, each serving a specific purpose:

#### 1. 💬 Chat Interface

**Purpose**: Interactive conversations with AI models

**Key Features**:
- Real-time message streaming
- Full conversation history
- Message regeneration
- System prompt customization
- RAG integration toggle
- Export conversations

**Usage Example**:
```
1. Select a model from sidebar (e.g., llama3)
2. Adjust temperature slider (0.0 = focused, 1.0 = creative)
3. Type your message in the text area
4. Click "📤 Send"
5. View response in chat window
6. Use "🔄 Regen" to regenerate last response
```

**Pro Tips**:
- Use lower temperature (0.2-0.4) for factual questions
- Use higher temperature (0.7-0.9) for creative tasks
- Enable RAG for domain-specific questions
- Save important conversations for later reference

#### 2. 🤖 Model Manager

**Purpose**: Complete Ollama model lifecycle management

**Sub-Tabs**:

**📋 Installed Models**:
```
View all installed models with:
- Model name and version
- Size on disk
- Last modified date
- Quick actions (info, delete)

Actions:
- Click "ℹ️ Details" for model specifications
- Click "🗑️ Delete" to remove model (confirms before deletion)
- Click "🔄 Refresh" to update list
```

**📥 Download Models**:
```
Popular Models:
- llama3 (4.7GB): General purpose, well-balanced
- llama3:70b (40GB): Most capable, resource-intensive
- mistral (4.1GB): Fast and efficient
- codellama (3.8GB): Specialized for code
- phi3 (2.2GB): Lightweight, fast responses
- gemma2 (5.4GB): Google's open model
- qwen2 (4.4GB): Alibaba's multilingual model

Custom Models:
- Enter any Ollama model name
- Supports version tags (e.g., llama3:7b)
- Downloads from Ollama library
```

**⚙️ Model Info**:
```
Displays detailed information:
- Model architecture
- Parameter count
- Context window size
- Quantization method
- License information
- System prompt template
```

#### 3. 📚 RAG Documents

**Purpose**: Manage your knowledge base for enhanced AI responses

**Sub-Tabs**:

**📤 Upload**:
```
Supported Formats:
- PDF: Extracts text from PDFs
- DOCX: Microsoft Word documents
- TXT: Plain text files
- MD: Markdown documents
- JSON: Structured data

Process:
1. Click "Upload documents for RAG"
2. Select one or multiple files
3. Click "Process Uploaded Files"
4. Wait for processing (shows progress)
5. Documents indexed and ready for use
```

**📋 Manage Documents**:
```
For each document:
- Filename and upload date
- Character count
- View: Preview first 1000 characters
- Delete: Remove from knowledge base

Bulk Actions:
- View all documents at once
- Sort by date or size
- Filter by name
```

**🔍 Search Test**:
```
Test your RAG system:
1. Enter a test query
2. Click "Search Documents"
3. View ranked results
4. See relevance scores
5. Preview matched context

Use this to verify your documents are properly indexed
```

#### 4. 💻 Code Generation

**Purpose**: AI-powered code creation with security validation

**Features**:
```
Input Panel:
- Describe what code you need
- Select programming language
- Specify any constraints

Output Panel:
- Syntax-highlighted code display
- Security scan results
- Action buttons (save, download, copy)

Supported Languages:
Python, JavaScript, Java, C++, Go, Rust, TypeScript, PHP

Security Features:
- Automatic scanning for dangerous patterns
- Input validation
- Safe code indicators
```

**Example Workflow**:
```
1. Select Language: Python
2. Enter Prompt: "Create a binary search function with error handling"
3. Click: 🚀 Generate
4. Review: Check security scan results
5. Save: To workspace or download
```

#### 5. 📊 Execution Monitor

**Purpose**: Manage workspace files and view execution history

**Features**:
```
File List:
- View all workspace files
- File size and metadata
- Quick actions (view, delete)

Actions:
- 👁️ View: Display file contents
- 🗑️ Delete: Remove file
- 📥 Download: Export file

Use Cases:
- Clean up old generated code
- Review previous work
- Manage storage space
```

#### 6. 🛡️ Security

**Purpose**: Security scanning and statistics

**Features**:
```
Code Scanner:
- Paste code for security analysis
- Real-time threat detection
- Detailed issue reporting

Security Statistics:
- Total actions logged
- Failed actions
- Blocked code attempts
- Success rate

Use Cases:
- Verify third-party code
- Audit generated code
- Monitor security health
```

#### 7. 📜 Audit Logs

**Purpose**: Complete activity trail for compliance and debugging

**Features**:
```
Log Viewer:
- Filterable by user
- Filterable by action type
- Adjustable line count
- Export capability

Log Format:
TIMESTAMP | USER | ACTION | STATUS | DETAILS

Actions Logged:
- Login attempts
- Model changes
- Code generation
- File operations
- RAG queries
- Security events
```

### Advanced Usage Patterns

#### Pattern 1: Multi-Model Comparison

```
Use Case: Compare responses across models

Steps:
1. Download multiple models (llama3, mistral, phi3)
2. Ask the same question with each model
3. Compare quality, speed, and accuracy
4. Choose the best model for your use case

Example:
Question: "Explain quantum entanglement"
- llama3: Detailed, academic explanation
- mistral: Concise, practical explanation
- phi3: Quick, simplified explanation
```

#### Pattern 2: RAG-Enhanced Conversations

```
Use Case: Company knowledge base assistant

Setup:
1. Upload documents:
   - employee_handbook.pdf
   - benefits_guide.pdf
   - it_policies.docx
   - faq.txt

2. Enable RAG in sidebar

Usage:
Employee: "What's the vacation policy?"
AI: [Searches documents]
    [Finds relevant section]
    [Answers using actual policy text]
    [Shows: 📚 Used 1 document(s)]

Benefits:
- Consistent answers
- Always up-to-date
- References source material
- No hallucinations
```

#### Pattern 3: Specialized Model Workflow

```
Use Case: Software development assistant

Setup:
1. Download codellama
2. Set temperature to 0.2 (precise)
3. Upload project documentation

Workflow:
General Questions → llama3
Code Generation → codellama
Code Review → codellama (temperature 0.1)
Documentation → llama3 (temperature 0.5)

Switch models seamlessly based on task!
```

#### Pattern 4: Conversation Templates

```
Research Assistant:
System Prompt: "You are a research assistant. Provide detailed, 
well-structured responses with citations when using documents."
Temperature: 0.3
RAG: Enabled

Creative Writer:
System Prompt: "You are a creative writer. Use vivid language 
and imaginative descriptions."
Temperature: 0.9
RAG: Disabled

Code Expert:
System Prompt: "You are a senior software engineer. Always 
follow best practices and include error handling."
Temperature: 0.2
Model: codellama
```

---

## 🔒 Security

### Security Architecture

The application implements a **defense-in-depth** security model with multiple layers of protection:

#### Layer 1: Authentication & Authorization

```
┌─────────────────────────────────────────┐
│ User Login Request                       │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ Credential Verification                  │
│ - SHA-256 password hashing              │
│ - Salt-based encryption                 │
│ - Brute force protection                │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ Role-Based Access Control (RBAC)        │
│ - Admin: Full access                    │
│ - User: Standard features               │
│ - ReadOnly: View-only                   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ Session Management                       │
│ - Secure session tokens                 │
│ - Automatic timeout                     │
│ - Activity tracking                     │
└─────────────────────────────────────────┘
```

**Default Credentials** (⚠️ CHANGE IMMEDIATELY):
```
Username: admin
Password: admin123
```

**Password Management**:
- Passwords stored as SHA-256 hashes
- Unique salt per installation
- No plaintext password storage
- Failed login attempt tracking

#### Layer 2: Input Validation

**Validation Rules**:
```python
Blocked Patterns (Regex):
- rm\s+-rf           # Destructive file operations
- sudo\s+            # Privilege escalation
- chmod\s+777        # Permission manipulation
- eval\(             # Dynamic code execution
- exec\(             # Direct code execution
- __import__         # Import manipulation
- os\.system         # Shell command execution
- subprocess\.       # Process spawning
- \.\.\/            # Path traversal

Dangerous Imports:
- os, subprocess, shutil, sys
- ctypes, pickle
- socket (for network operations)

File Operations:
- All write operations validated
- Path traversal prevention
- Extension whitelist enforcement
- Size limit checks (10MB default)
```

**Sanitization Process**:
1. Input length limiting (10,000 chars)
2. Control character removal
3. Pattern matching against blacklist
4. Output validation

#### Layer 3: Sandboxed Execution

**Sandbox Features**:
```
Isolation:
- Temporary directory per execution
- No access to parent filesystem
- Limited environment variables
- Restricted system calls

Resource Limits:
- 30-second execution timeout
- Memory limits (OS-level)
- CPU limits (configurable)
- File size limits

Cleanup:
- Automatic sandbox deletion
- No residual files
- Memory cleanup
- Process termination
```

**Sandbox Implementation**:
```python
sandbox_path = /sandbox/sandbox_<random_id>/
environment = {
    "PATH": "/usr/bin",
    "PYTHONDONTWRITEBYTECODE": "1"
}
timeout = 30 seconds
cleanup = automatic
```

#### Layer 4: Audit Logging

**Logged Events**:
```
Authentication:
- LOGIN_SUCCESS
- LOGIN_FAILED
- LOGOUT
- PASSWORD_CHANGED

Model Operations:
- MODEL_DOWNLOADED
- MODEL_DELETED
- MODEL_CHANGED

Code Operations:
- CODE_GENERATED
- CODE_EXECUTED
- CODE_BLOCKED
- FILE_SAVED
- FILE_DELETED

Chat Operations:
- CHAT_MESSAGE
- CHAT_SAVED
- CHAT_LOADED

RAG Operations:
- RAG_DOC_UPLOADED
- RAG_DOC_DELETED
- RAG_SEARCH

Security Events:
- SECURITY_SCAN
- BLOCKED_PATTERN
- UNAUTHORIZED_ACCESS
- RATE_LIMIT_HIT
```

**Log Format**:
```
TIMESTAMP | USERNAME | ACTION | STATUS | DETAILS

Example:
2024-02-15T14:30:45 | admin | CODE_EXECUTED | SUCCESS | File: test.py
2024-02-15T14:31:12 | user1 | LOGIN_FAILED | FAILURE | Invalid password
2024-02-15T14:32:00 | admin | MODEL_DOWNLOADED | SUCCESS | Model: phi3
```

#### Layer 5: Rate Limiting

**Limits**:
```
Per-User Daily Limits:
- Code Generation: 100 requests
- Model Downloads: 10 requests
- File Operations: 50 requests

Per-Action Limits:
- Configurable per role
- Sliding window (24 hours)
- Automatic reset

Enforcement:
- Request counting
- Time-window tracking
- Graceful degradation
```

### Security Configuration

**Security Config Class**:
```python
MAX_FILE_SIZE_MB = 10
MAX_EXECUTION_TIME = 30
ALLOWED_FILE_EXTENSIONS = ['.py', '.txt', '.json', '.yaml', '.md']
BLOCKED_PATTERNS = [<comprehensive list>]
MAX_DAILY_EXECUTIONS = 100
REQUIRE_CONFIRMATION = True
ENABLE_AUDIT_LOG = True
SANDBOX_ENABLED = True
```

**Customization**:
```python
# Edit in application file
SECURITY_CONFIG.MAX_EXECUTION_TIME = 60
SECURITY_CONFIG.MAX_DAILY_EXECUTIONS = 50
SECURITY_CONFIG.ALLOWED_FILE_EXTENSIONS.append('.cpp')
```

### Security Best Practices

**For Administrators**:
1. Change default password immediately
2. Use strong, unique passwords (16+ characters)
3. Review audit logs weekly
4. Monitor failed login attempts
5. Keep models updated
6. Regularly backup user database
7. Implement firewall rules
8. Use HTTPS in production
9. Enable SSL certificates
10. Regular security audits

**For Users**:
1. Never share credentials
2. Use unique passwords
3. Log out when finished
4. Review generated code before execution
5. Report suspicious activity
6. Keep conversations appropriate
7. Don't upload sensitive data

**For Production Deployments**:
1. Use Docker for isolation
2. Implement reverse proxy (Nginx)
3. Enable SSL/TLS
4. Configure firewall (UFW/iptables)
5. Set up monitoring and alerts
6. Implement backup strategy
7. Use systemd for service management
8. Enable log rotation
9. Regular security scans
10. Incident response plan

### Security Audit Checklist

```
☐ Default password changed
☐ Strong password policy enforced
☐ Audit logs reviewed regularly
☐ Failed login attempts monitored
☐ Rate limits configured
☐ Firewall rules active
☐ HTTPS enabled (production)
☐ Regular backups scheduled
☐ User roles properly assigned
☐ Security patterns updated
☐ Sandbox isolation verified
☐ Input validation tested
☐ Access logs reviewed
☐ Incident response documented
☐ Security training completed
```

### Known Limitations

Current security limitations to be aware of:

1. **PDF Processing**: Requires external library for full security
2. **Network Access**: Models can't access external URLs (by design)
3. **Binary Execution**: Not supported in sandbox
4. **File Size**: Limited to configured maximum (default 10MB)
5. **Concurrent Users**: Single-threaded execution per instance

### Vulnerability Reporting

To report security vulnerabilities:

1. **Do NOT** create public GitHub issues
2. Email: security@your-organization.com
3. Include detailed description
4. Provide proof of concept if applicable
5. Allow 90 days for patching before disclosure

---

## ⚙️ Configuration

### Application Configuration

#### Environment Variables

```bash
# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# Security Settings
MAX_FILE_SIZE_MB=10
MAX_EXECUTION_TIME=30
ENABLE_AUDIT_LOG=true

# Paths
WORKSPACE_DIR=./workspace
LOGS_DIR=./logs
CONFIG_DIR=./config
```

#### Configuration Files

**users.json** (config/users.json):
```json
{
  "admin": {
    "password": "<hashed>",
    "role": "admin",
    "created": "2024-02-15T10:00:00"
  },
  "user1": {
    "password": "<hashed>",
    "role": "user",
    "created": "2024-02-15T11:00:00"
  }
}
```

**Security Configuration** (in-app):
```python
class SecurityConfig:
    MAX_FILE_SIZE_MB: int = 10
    MAX_EXECUTION_TIME: int = 30
    ALLOWED_FILE_EXTENSIONS: List[str] = ['.py', '.txt', '.json']
    MAX_DAILY_EXECUTIONS: int = 100
    REQUIRE_CONFIRMATION: bool = True
```

### Model Configuration

**Available Models**:
```yaml
llama3:
  size: 4.7GB
  parameters: 8B
  context: 8192 tokens
  best_for: General conversation

llama3:70b:
  size: 40GB
  parameters: 70B
  context: 8192 tokens
  best_for: Complex reasoning

mistral:
  size: 4.1GB
  parameters: 7B
  context: 8192 tokens
  best_for: Fast responses

codellama:
  size: 3.8GB
  parameters: 7B
  context: 16384 tokens
  best_for: Code generation

phi3:
  size: 2.2GB
  parameters: 3.8B
  context: 4096 tokens
  best_for: Lightweight tasks
```

**Model Selection Guidelines**:
- **Memory < 8GB**: Use phi3
- **Memory 8-16GB**: Use llama3 or mistral
- **Memory > 16GB**: Use llama3:70b for best quality
- **Coding Tasks**: Always prefer codellama
- **Fast Responses**: Use phi3 or mistral

### RAG Configuration

**Document Settings**:
```python
# Supported formats
SUPPORTED_FORMATS = ['.txt', '.md', '.pdf', '.docx', '.json']

# Processing limits
MAX_DOCUMENT_SIZE = 10MB
MAX_DOCUMENTS = 100

# Search settings
MAX_SEARCH_RESULTS = 3
CONTEXT_CHARS = 500
```

**Search Algorithm**:
```python
# Simple keyword-based search
# Scores by occurrence count
# Extracts surrounding context
# Returns top N results
```

### Logging Configuration

**Log Levels**:
```python
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
```

**Log Rotation** (recommended):
```bash
# /etc/logrotate.d/llm-factory
/opt/llm-factory/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 appuser appuser
    sharedscripts
}
```

---

## 🔌 API Reference

### Ollama Manager API

```python
class OllamaManager:
    @staticmethod
    def get_available_models() -> List[Dict]:
        """Get list of installed models"""
        
    @staticmethod
    def get_model_info(model_name: str) -> Dict:
        """Get detailed model information"""
        
    @staticmethod
    def pull_model(model_name: str) -> Tuple[bool, str]:
        """Download a model"""
        
    @staticmethod
    def delete_model(model_name: str) -> Tuple[bool, str]:
        """Delete a model"""
        
    @staticmethod
    def generate_response(model: str, prompt: str, 
                         system: str = None, 
                         temperature: float = 0.7) -> Dict:
        """Generate response"""
        
    @staticmethod
    def chat_with_history(model: str, messages: List[Dict], 
                         temperature: float = 0.7) -> Dict:
        """Chat with conversation history"""
```

### RAG Manager API

```python
class RAGManager:
    @staticmethod
    def process_document(file_path: Path, 
                        file_name: str) -> Tuple[bool, str]:
        """Process uploaded document"""
        
    @staticmethod
    def get_documents() -> List[Dict]:
        """Get list of processed documents"""
        
    @staticmethod
    def delete_document(filename: str) -> bool:
        """Delete a document"""
        
    @staticmethod
    def search_documents(query: str, 
                        max_results: int = 3) -> List[Dict]:
        """Search documents for relevant content"""
```

### Security Validator API

```python
class SecurityValidator:
    @staticmethod
    def validate_code(code: str) -> Tuple[bool, List[str]]:
        """Validate code for security issues"""
        
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """Validate filename for security"""
        
    @staticmethod
    def sanitize_input(text: str, 
                      max_length: int = 10000) -> str:
        """Sanitize user input"""
```

### Authentication Manager API

```python
class AuthManager:
    @staticmethod
    def authenticate(username: str, 
                    password: str) -> Tuple[bool, Optional[str]]:
        """Authenticate user and return role"""
        
    @staticmethod
    def create_user(username: str, password: str, 
                   role: str) -> bool:
        """Create new user (admin only)"""
        
    @staticmethod
    def change_password(username: str, old_password: str, 
                       new_password: str) -> bool:
        """Change user password"""
```

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/llm-factory.git
cd llm-factory

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
./test.sh

# Start development server
streamlit run llm_model_factory_ultimate.py --logger.level=debug
```

### Development Dependencies

```
requirements-dev.txt:
pytest>=7.4.0
black>=23.3.0
flake8>=6.0.0
mypy>=1.4.0
pylint>=2.17.0
```

### Code Style

**Formatting**:
```bash
# Format code
black llm_model_factory_ultimate.py

# Lint code
flake8 llm_model_factory_ultimate.py

# Type checking
mypy llm_model_factory_ultimate.py
```

**Style Guidelines**:
- PEP 8 compliant
- Type hints for all functions
- Docstrings for all classes and methods
- Maximum line length: 100 characters
- Use meaningful variable names

### Testing

```bash
# Run all tests
./test.sh

# Run specific test
python3 -m pytest tests/test_security.py

# Run with coverage
python3 -m pytest --cov=. tests/
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick checklist**:
- [ ] Code follows style guidelines
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] Backward compatibility maintained
- [ ] Changelog updated

---

## 🚢 Deployment

### Production Deployment Options

#### Option 1: Systemd Service (Recommended)

```bash
# Create service file
sudo nano /etc/systemd/system/llm-factory.service
```

```ini
[Unit]
Description=Secure LLM Model Factory
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/llm-factory
Environment="PATH=/opt/llm-factory/venv/bin"
ExecStart=/opt/llm-factory/venv/bin/streamlit run llm_model_factory_ultimate.py --server.port=8501
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/llm-factory/workspace /opt/llm-factory/logs /opt/llm-factory/config

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable llm-factory
sudo systemctl start llm-factory
sudo systemctl status llm-factory
```

#### Option 2: Docker Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  llm-factory:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./workspace:/app/workspace
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/sandbox
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

#### Option 3: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/llm-factory
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

### Monitoring & Maintenance

**Health Checks**:
```bash
# Application health
curl http://localhost:8501/_stcore/health

# Ollama health
curl http://localhost:11434/api/tags

# System resources
htop
df -h
```

**Log Monitoring**:
```bash
# Watch application logs
tail -f logs/app.log

# Watch audit logs
tail -f logs/audit.log

# Search for errors
grep "ERROR" logs/app.log

# Count failed logins
grep -c "LOGIN_FAILED" logs/audit.log
```

**Backup Strategy**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/llm-factory"

mkdir -p "$BACKUP_DIR"

# Backup user database
cp config/users.json "$BACKUP_DIR/users_$DATE.json"

# Backup audit logs
cp logs/audit.log "$BACKUP_DIR/audit_$DATE.log"

# Backup RAG documents
tar -czf "$BACKUP_DIR/rag_docs_$DATE.tar.gz" config/rag_documents/

# Backup workspace
tar -czf "$BACKUP_DIR/workspace_$DATE.tar.gz" workspace/

# Keep only last 30 days
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: ModuleNotFoundError: streamlit

**Symptom**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or use start script
./start.sh
```

#### Issue: Port 8501 Already in Use

**Symptom**:
```
OSError: [Errno 98] Address already in use
```

**Solution**:
```bash
# Find process using port
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port
streamlit run llm_model_factory_ultimate.py --server.port 8502
```

#### Issue: Ollama Not Running

**Symptom**:
```
❌ Ollama Service: Not Running
```

**Solution**:
```bash
# Start Ollama
ollama serve

# Or in background
nohup ollama serve > /dev/null 2>&1 &

# Verify
curl http://localhost:11434/api/tags
```

#### Issue: Permission Denied

**Symptom**:
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod 755 .
chmod 700 config
chmod +x *.sh
```

#### Issue: Model Download Fails

**Symptom**:
```
Error downloading model: timeout
```

**Solution**:
```bash
# Increase timeout
export OLLAMA_TIMEOUT=600

# Check internet connection
ping ollama.com

# Check disk space
df -h

# Try manual download
ollama pull llama3
```

#### Issue: RAG Documents Not Processing

**Symptom**:
```
Failed to process document
```

**Solution**:
```bash
# Check file format
file your-document.pdf

# Check file size
ls -lh your-document.pdf

# Check permissions
chmod 644 your-document.pdf

# For PDFs, install PyPDF2
pip install PyPDF2
```

### Debug Mode

Enable detailed logging:

```bash
# Start with debug logging
streamlit run llm_model_factory_ultimate.py --logger.level=debug

# View detailed logs
tail -f logs/app.log
```

### Diagnostic Commands

```bash
# Check Python version
python3 --version

# Check pip packages
pip list | grep -E "streamlit|requests"

# Check Ollama
ollama list

# Check ports
netstat -tuln | grep -E ":(8501|11434)"

# Check processes
ps aux | grep -E "streamlit|ollama"

# Check disk space
df -h

# Check memory
free -h

# Run test suite
./test.sh
```

### Getting Help

1. **Check Documentation**: Read relevant docs first
2. **Search Issues**: Look for similar problems on GitHub
3. **Run Diagnostics**: Use `./test.sh` to identify issues
4. **Check Logs**: Review `logs/app.log` and `logs/audit.log`
5. **Ask Community**: Post in discussions with diagnostics
6. **Report Bugs**: Create detailed issue on GitHub

**When Reporting Issues, Include**:
- Application version
- Python version
- Operating system
- Error messages (full stack trace)
- Steps to reproduce
- Diagnostic output from `./test.sh`

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide

1. **Fork** the repository
2. **Clone** your fork
3. **Create** a feature branch
4. **Make** your changes
5. **Test** thoroughly
6. **Commit** with clear messages
7. **Push** to your fork
8. **Submit** a pull request

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX enhancements
- 🌍 Internationalization
- ♿ Accessibility improvements
- 🔒 Security enhancements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

```
MIT License

Copyright (c) 2024 LLM Model Factory Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 💬 Support

### Getting Support

- **Documentation**: Check the comprehensive docs in `/docs`
- **FAQ**: See [FAQ.md](docs/FAQ.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/llm-factory/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/llm-factory/discussions)
- **Email**: security@your-organization.com (security issues only)

### Community

- **Discord**: [Join our server](https://discord.gg/llm-factory)
- **Twitter**: [@llmfactory](https://twitter.com/llmfactory)
- **Blog**: [blog.llmfactory.com](https://blog.llmfactory.com)

### Professional Support

For enterprise support, custom development, or consulting:
- Email: enterprise@your-organization.com
- Website: https://llmfactory.com/enterprise

---

## 🙏 Acknowledgments

### Built With

- [Streamlit](https://streamlit.io/) - Web framework
- [Ollama](https://ollama.com/) - LLM runtime
- [Python](https://www.python.org/) - Programming language
- [Docker](https://www.docker.com/) - Containerization

### Contributors

Thanks to all contributors who have helped improve this project!

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

### Inspiration

This project was inspired by the need for secure, enterprise-ready LLM applications with proper authentication, audit trails, and production-grade security.

---

## 📚 Additional Resources

### Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Security Guide](docs/SECURITY.md) - Security architecture and best practices
- [Ultimate Guide](docs/ULTIMATE_GUIDE.md) - Complete feature guide
- [Quick Start](docs/QUICKSTART.md) - Quick reference guide
- [API Documentation](docs/API.md) - API reference

### Tutorials

- [Getting Started](docs/tutorials/getting-started.md)
- [Model Management](docs/tutorials/model-management.md)
- [RAG Setup](docs/tutorials/rag-setup.md)
- [Production Deployment](docs/tutorials/production-deployment.md)

### External Resources

- [Ollama Documentation](https://ollama.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

## 🗺️ Roadmap

### Current Version: 3.0.0

### Planned Features

**Version 3.1.0** (Q2 2024):
- [ ] Two-factor authentication (2FA)
- [ ] LDAP/Active Directory integration
- [ ] Advanced RAG with vector embeddings
- [ ] Multi-user conversation support
- [ ] Enhanced analytics dashboard

**Version 3.2.0** (Q3 2024):
- [ ] API endpoints for external integration
- [ ] Webhook support
- [ ] Advanced model fine-tuning interface
- [ ] Custom model creation tools
- [ ] Team collaboration features

**Version 4.0.0** (Q4 2024):
- [ ] Multi-tenant support
- [ ] Advanced role permissions
- [ ] Real-time collaboration
- [ ] Mobile application
- [ ] GraphQL API

### Feature Requests

Vote on or submit feature requests in our [GitHub Discussions](https://github.com/yourusername/llm-factory/discussions/categories/feature-requests).

---

## 📊 Statistics

- **⭐ Stars**: [![GitHub stars](https://img.shields.io/github/stars/yourusername/llm-factory.svg)](https://github.com/yourusername/llm-factory/stargazers)
- **🍴 Forks**: [![GitHub forks](https://img.shields.io/github/forks/yourusername/llm-factory.svg)](https://github.com/yourusername/llm-factory/network)
- **🐛 Issues**: [![GitHub issues](https://img.shields.io/github/issues/yourusername/llm-factory.svg)](https://github.com/yourusername/llm-factory/issues)
- **📥 Downloads**: [![GitHub downloads](https://img.shields.io/github/downloads/yourusername/llm-factory/total.svg)](https://github.com/yourusername/llm-factory/releases)

---

## ⚖️ Disclaimer

This software is provided "as is" without warranty of any kind. While comprehensive security measures have been implemented, no system is 100% secure. Users are responsible for:

- Proper configuration and deployment
- Regular security audits
- Keeping software updated
- Following security best practices
- Compliance with applicable laws and regulations

The authors and contributors are not liable for any damages arising from the use of this software.

---

<div align="center">

**Built with ❤️ by the LLM Factory Team**

[Website](https://llmfactory.com) • [Documentation](https://docs.llmfactory.com) • [Blog](https://blog.llmfactory.com)

[![Follow on Twitter](https://img.shields.io/twitter/follow/llmfactory?style=social)](https://twitter.com/llmfactory)
[![Star on GitHub](https://img.shields.io/github/stars/yourusername/llm-factory.svg?style=social)](https://github.com/yourusername/llm-factory)

© 2024 LLM Factory Contributors. All rights reserved.

</div>
