# Installation & Deployment Guide

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+ with WSL2
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk**: 2GB free space minimum
- **Network**: Internet access for LLM API

### Required Software
- Python 3.8+
- pip (Python package manager)
- Git (for version control features)
- Ollama (for local LLM hosting) - Optional

## 🚀 Quick Start Installation

### Step 1: Clone or Download

```bash
# Create project directory
mkdir secure-llm-factory
cd secure-llm-factory

# Copy the application file
# (llm_model_factory_secure.py should be in this directory)
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Create `requirements.txt`:
```
streamlit>=1.28.0
requests>=2.31.0
```

### Step 4: Initial Setup

```bash
# Create directory structure
python3 -c "
from pathlib import Path
for d in ['workspace', 'sandbox', 'logs', 'config']:
    Path(d).mkdir(exist_ok=True)
    print(f'Created: {d}/')
"
```

### Step 5: Run Application

```bash
# Start the application
streamlit run llm_model_factory_secure.py
```

The application will open in your browser at `http://localhost:8501`

### Step 6: First Login

1. Use default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

2. **IMMEDIATELY** change the password:
   - Go to User Management tab
   - Create new admin user with strong password
   - (Or implement password change feature)

## 🔧 Configuration

### Basic Configuration

Edit the configuration section in `llm_model_factory_secure.py`:

```python
# Security Configuration
SECURITY_CONFIG = SecurityConfig(
    MAX_FILE_SIZE_MB=10,
    MAX_EXECUTION_TIME=30,
    MAX_DAILY_EXECUTIONS=100,
    REQUIRE_CONFIRMATION=True,
    ENABLE_AUDIT_LOG=True,
    SANDBOX_ENABLED=True
)
```

### LLM API Configuration

**Option 1: Local Ollama**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Verify it's running
ollama list

# In the app, use:
# API URL: http://localhost:11434/api/generate
# Model Name: llama3
```

**Option 2: External API**
```python
# In sidebar settings:
API_URL = "https://your-api-endpoint.com/generate"
MODEL_NAME = "your-model-name"
```

### Advanced Configuration

#### 1. Custom Security Rules

Add custom blocked patterns:
```python
SECURITY_CONFIG.BLOCKED_PATTERNS.extend([
    r'your_custom_pattern',
    r'another_dangerous_pattern'
])
```

#### 2. Rate Limits by Role

```python
class RateLimiter:
    ROLE_LIMITS = {
        'admin': 1000,
        'user': 100,
        'readonly': 0
    }
```

#### 3. Allowed File Extensions

```python
SECURITY_CONFIG.ALLOWED_FILE_EXTENSIONS = [
    '.py', '.txt', '.json', '.yaml', '.yml', '.md', '.csv'
]
```

## 🐳 Docker Deployment (Recommended)

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY llm_model_factory_secure.py .

# Create necessary directories
RUN mkdir -p workspace sandbox logs config

# Expose Streamlit port
EXPOSE 8501

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Start application
CMD ["streamlit", "run", "llm_model_factory_secure.py", "--server.address", "0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
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
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Update
docker-compose pull
docker-compose up -d --build
```

## 🌐 Production Deployment

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/llm-factory`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
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
        
        # Timeouts
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/llm-factory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Systemd Service

Create `/etc/systemd/system/llm-factory.service`:
```ini
[Unit]
Description=Secure LLM Model Factory
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/llm-factory
Environment="PATH=/opt/llm-factory/venv/bin"
ExecStart=/opt/llm-factory/venv/bin/streamlit run llm_model_factory_secure.py
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

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-factory
sudo systemctl start llm-factory
sudo systemctl status llm-factory
```

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Block direct access to Streamlit port
sudo ufw deny 8501/tcp
```

### 2. AppArmor Profile

Create `/etc/apparmor.d/usr.bin.llm-factory`:
```
#include <tunables/global>

/opt/llm-factory/venv/bin/python3 {
  #include <abstractions/base>
  #include <abstractions/python>

  /opt/llm-factory/** r,
  /opt/llm-factory/workspace/** rw,
  /opt/llm-factory/logs/** rw,
  /opt/llm-factory/config/** rw,
  /opt/llm-factory/sandbox/** rw,

  # Deny everything else
  /** ix,
  deny /etc/** w,
  deny /sys/** rw,
  deny /proc/** w,
}
```

Load profile:
```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.llm-factory
```

### 3. Resource Limits

Edit `/etc/security/limits.conf`:
```
appuser soft nofile 4096
appuser hard nofile 8192
appuser soft nproc 256
appuser hard nproc 512
appuser soft memlock 2097152
appuser hard memlock 4194304
```

### 4. Regular Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/llm-factory"

mkdir -p $BACKUP_DIR

# Backup user database
cp /opt/llm-factory/config/users.json $BACKUP_DIR/users_$DATE.json

# Backup audit logs
cp /opt/llm-factory/logs/audit.log $BACKUP_DIR/audit_$DATE.log

# Backup workspace
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz /opt/llm-factory/workspace/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
0 2 * * * /usr/local/bin/backup.sh
```

## 📊 Monitoring & Maintenance

### 1. Log Monitoring

```bash
# Watch audit log
tail -f /opt/llm-factory/logs/audit.log

# Watch application log
tail -f /opt/llm-factory/logs/app.log

# Search for failed logins
grep "LOGIN_FAILED" /opt/llm-factory/logs/audit.log

# Count blocked code attempts
grep -c "CODE_BLOCKED" /opt/llm-factory/logs/audit.log
```

### 2. Performance Monitoring

```bash
# Check memory usage
ps aux | grep streamlit

# Check disk usage
du -sh /opt/llm-factory/*

# Monitor connections
netstat -an | grep 8501
```

### 3. Health Checks

Create monitoring script:
```bash
#!/bin/bash
# health-check.sh

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/_stcore/health)

if [ $STATUS -eq 200 ]; then
    echo "OK: Application is healthy"
    exit 0
else
    echo "ERROR: Application is down (HTTP $STATUS)"
    # Send alert
    # Restart service
    sudo systemctl restart llm-factory
    exit 1
fi
```

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 8501
lsof -i :8501
# Kill process
kill -9 <PID>
```

**2. Permission Errors**
```bash
# Fix ownership
sudo chown -R appuser:appuser /opt/llm-factory
# Fix permissions
chmod 755 /opt/llm-factory
chmod 700 /opt/llm-factory/config
```

**3. Ollama Connection Failed**
```bash
# Check Ollama status
systemctl status ollama
# Restart Ollama
sudo systemctl restart ollama
# Test API
curl http://localhost:11434/api/generate -d '{"model":"llama3","prompt":"hi"}'
```

**4. Audit Log Growing Large**
```bash
# Rotate logs
logrotate /etc/logrotate.d/llm-factory
# Or manually
mv /opt/llm-factory/logs/audit.log /opt/llm-factory/logs/audit.log.old
touch /opt/llm-factory/logs/audit.log
```

### Debug Mode

```bash
# Run with debug logging
streamlit run llm_model_factory_secure.py --logger.level=debug
```

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Ollama Documentation](https://ollama.com/docs)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Security Guidelines](https://owasp.org/)

## ✅ Deployment Checklist

- [ ] System requirements met
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Directory structure created
- [ ] Default password changed
- [ ] Security configuration reviewed
- [ ] Firewall configured
- [ ] HTTPS/SSL enabled (production)
- [ ] Backup system configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Health checks implemented
- [ ] Documentation reviewed
- [ ] Security audit performed

---

**For Support**: security@your-org.com  
**Version**: 2.0.0  
**Last Updated**: February 2024
