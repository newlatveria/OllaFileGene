# 🚀 Complete Installation Guide - All Methods

## Quick Reference Table

| Method | Time | Difficulty | Best For | Command |
|--------|------|------------|----------|---------|
| **Quick Install** | 2 min | ⭐ Easy | Testing | `./quick-install.sh` |
| **Interactive Menu** | 5 min | ⭐ Easy | All users | `./menu.sh` |
| **Basic Manual** | 5 min | ⭐⭐ Medium | Development | See below |
| **Docker** | 10 min | ⭐⭐ Medium | Production | `docker-compose up` |
| **Full Production** | 30 min | ⭐⭐⭐ Advanced | Enterprise | `./menu.sh` → Complete |

## 🚀 Method 1: Quick Install (Fastest)

**Perfect for:** Quick testing, getting started fast

```bash
# One command installation
./quick-install.sh

# Then start
source venv/bin/activate
streamlit run llm_model_factory_secure.py
```

**What it does:**
- ✅ Checks Python
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Creates directories
- ✅ Sets permissions

**Time:** ~2 minutes

---

## 🎮 Method 2: Interactive Menu (Recommended)

**Perfect for:** All users, all scenarios

```bash
# Launch interactive menu
./menu.sh

# Follow on-screen prompts:
# 1. Check System Requirements
# 2. Choose Installation Type
# 3. Configure Security
# 4. Start Application
```

**Features:**
- 📊 System requirement checks
- 🔧 Multiple installation options
- ⚙️ Configuration wizards
- 📈 Status monitoring
- 🛡️ Security audits
- 📚 Built-in documentation

**Time:** ~5-10 minutes (depending on options)

**See:** MENU_GUIDE.md for detailed guide

---

## 🔧 Method 3: Basic Manual Installation

**Perfect for:** Developers, custom setups

### Step-by-Step

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create directories
mkdir -p workspace sandbox logs config
chmod 700 config

# 4. Start application
streamlit run llm_model_factory_secure.py
```

**Access:** http://localhost:8501  
**Login:** admin / admin123

**Time:** ~5 minutes

---

## 🐳 Method 4: Docker Installation

**Perfect for:** Production, isolated environments

### Quick Start

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### With Ollama (Local LLM)

```bash
# Starts both application and Ollama
docker-compose up -d

# Pull a model
docker-compose exec ollama ollama pull llama3

# Restart to use new model
docker-compose restart llm-factory
```

**Access:** http://localhost:8501  
**Time:** ~10 minutes (+ model download)

---

## 🏢 Method 5: Full Production Deployment

**Perfect for:** Enterprise, public-facing deployments

### Using Interactive Menu

```bash
sudo ./menu.sh

# Navigate through:
1. Check System Requirements
2. Installation Options → Complete Installation
   - This installs: Python, Docker, Ollama, Nginx, SSL
3. Configuration
   - Security Configuration
   - Firewall Setup
   - Backup Configuration
4. Start Application → Systemd Service
```

### Manual Production Setup

```bash
# 1. Basic installation
./quick-install.sh

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3

# 3. Install and configure Nginx
sudo apt-get install nginx
sudo nano /etc/nginx/sites-available/llm-factory
# (See INSTALLATION.md for config)

# 4. Install SSL certificate
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# 5. Create systemd service
sudo nano /etc/systemd/system/llm-factory.service
# (See INSTALLATION.md for config)
sudo systemctl enable llm-factory
sudo systemctl start llm-factory

# 6. Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8501
sudo ufw enable
```

**Access:** https://yourdomain.com  
**Time:** ~30 minutes

---

## 🧪 Method 6: Test Installation

**Perfect for:** Validation, CI/CD

```bash
# Run comprehensive tests
./test.sh

# Tests include:
# ✓ File structure
# ✓ Python environment
# ✓ Security configuration
# ✓ Docker setup
# ✓ Network ports
# ✓ And more...
```

**Time:** ~1 minute

---

## 📋 Comparison of Installation Methods

### Quick Install
**Pros:**
- ✅ Fastest setup
- ✅ Minimal decisions
- ✅ Great for testing

**Cons:**
- ❌ Basic setup only
- ❌ No production features
- ❌ Manual configuration needed

### Interactive Menu
**Pros:**
- ✅ User-friendly
- ✅ All features available
- ✅ Guided configuration
- ✅ Built-in help

**Cons:**
- ❌ Requires terminal interaction
- ❌ Not scriptable

### Docker
**Pros:**
- ✅ Isolated environment
- ✅ Easy updates
- ✅ Consistent deployment
- ✅ Production-ready

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Larger resource usage
- ❌ Slightly slower startup

### Full Production
**Pros:**
- ✅ Enterprise-grade
- ✅ HTTPS/SSL
- ✅ Auto-restart
- ✅ Monitoring

**Cons:**
- ❌ Complex setup
- ❌ Requires root access
- ❌ Time-consuming

---

## 🎯 Recommended Path by Use Case

### For Quick Testing
```bash
./quick-install.sh
source venv/bin/activate
streamlit run llm_model_factory_secure.py
```

### For Development
```bash
./menu.sh
# → Basic Installation
# → Start → Virtual Environment
```

### For Team Deployment
```bash
docker-compose up -d
# Share: http://your-server:8501
```

### For Public Website
```bash
sudo ./menu.sh
# → Complete Installation
# → Configure with domain name
# → Enable SSL
# → Start as service
```

---

## 🔍 Post-Installation Checklist

After any installation method:

- [ ] Application starts successfully
- [ ] Can access web interface
- [ ] Can login with default credentials
- [ ] **Changed default admin password**
- [ ] Security settings reviewed
- [ ] Backup configured (production)
- [ ] Firewall enabled (production)
- [ ] SSL certificate installed (public)
- [ ] Monitoring setup (production)
- [ ] Documentation reviewed

---

## 🐛 Troubleshooting Quick Guide

### Application Won't Start

```bash
# Check Python version
python3 --version  # Need 3.8+

# Check dependencies
source venv/bin/activate
pip list | grep streamlit

# Check logs
tail -f logs/app.log

# Test manually
streamlit run llm_model_factory_secure.py
```

### Port Already in Use

```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run llm_model_factory_secure.py --server.port 8502
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod 755 .
chmod 700 config
chmod +x *.sh
```

### Docker Issues

```bash
# Check Docker
docker --version
sudo systemctl status docker

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 📊 Installation Validation

Run the test suite after installation:

```bash
./test.sh
```

Expected output:
```
Total Tests:    16
Passed:         14-16
Failed:         0
Warnings:       0-2

✓ All critical tests passed!
```

---

## 🆘 Getting Help

### Check Documentation
```bash
./menu.sh
# → 7. Documentation
# → Select document to view
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Audit logs
tail -f logs/audit.log

# Installation logs
tail -f logs/install.log

# Or use menu
./menu.sh → Status & Monitoring → View Logs
```

### Run Diagnostics
```bash
./menu.sh
# → 5. Status & Monitoring
# → 1. Check Status
```

---

## 📚 Additional Resources

### Documentation Files
- `README.md` - Main documentation
- `SECURITY.md` - Security guide
- `INSTALLATION.md` - Detailed installation
- `COMPARISON.md` - Security comparison
- `MENU_GUIDE.md` - Menu system guide

### Scripts
- `menu.sh` - Interactive menu system
- `quick-install.sh` - Fast installation
- `test.sh` - Validation tests
- `backup.sh` - Backup script (created during setup)

### Configuration Files
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup
- `.gitignore` - Git ignore patterns

---

## 🎓 Next Steps After Installation

1. **First Login**
   - Access: http://localhost:8501
   - Login: admin / admin123
   - **Immediately change password!**

2. **Configure LLM**
   - Sidebar → Model Settings
   - Enter API URL or use local Ollama
   - Test connection

3. **Generate First Code**
   - Go to "Code Generation" tab
   - Enter a prompt
   - Review security validation
   - Execute safely

4. **Review Security**
   - Go to "Security Audit" tab
   - Check security statistics
   - Review audit logs

5. **Set Up Backups** (Production)
   ```bash
   ./menu.sh
   # → Configuration → Backup Configuration
   ```

6. **Monitor System**
   ```bash
   ./menu.sh
   # → Status & Monitoring
   ```

---

## 🔄 Updating

### Update Application
```bash
# Using menu
./menu.sh
# → Security & Maintenance → Update Application

# Or manually
source venv/bin/activate
pip install --upgrade -r requirements.txt
git pull  # If using git
```

### Update Docker
```bash
docker-compose pull
docker-compose up -d --build
```

---

## 🎉 Quick Command Reference

```bash
# Installation
./quick-install.sh              # Quick install
./menu.sh                        # Interactive menu
docker-compose up -d             # Docker start

# Running
source venv/bin/activate         # Activate venv
streamlit run llm_model_factory_secure.py  # Start app

# Management
./menu.sh                        # Full menu system
./test.sh                        # Run tests
docker-compose logs -f           # View logs

# Status
./menu.sh → Status & Monitoring  # Check status
tail -f logs/audit.log           # Watch audit log

# Stopping
docker-compose down              # Stop Docker
sudo systemctl stop llm-factory  # Stop service
pkill -f streamlit              # Kill process
```

---

**Choose Your Adventure:**

- 🏃 **In a hurry?** → `./quick-install.sh`
- 🎮 **Want guidance?** → `./menu.sh`
- 🐳 **Need containers?** → `docker-compose up -d`
- 🏢 **Going production?** → `sudo ./menu.sh` → Complete Installation

**Questions?** Check the documentation or run `./menu.sh` → Documentation

---

**Version:** 2.0.0  
**Last Updated:** February 2024  
**Tested On:** Ubuntu 20.04+, macOS 10.15+, WSL2
