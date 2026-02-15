# Quick Start Guide - Interactive Menu System

## 🚀 Getting Started

The interactive menu system provides a user-friendly interface for installing, configuring, and managing the Secure LLM Model Factory.

### Launch the Menu

```bash
# Make the script executable (first time only)
chmod +x menu.sh

# Run the menu
./menu.sh

# Or with sudo for system-level installations
sudo ./menu.sh
```

## 📋 Menu Structure

```
Main Menu
├── 1. Check System Requirements
├── 2. Installation Options
│   ├── Basic Installation (Virtual Environment)
│   ├── Docker Installation
│   ├── Systemd Service Installation
│   ├── Nginx Reverse Proxy
│   ├── Install Ollama (Local LLM)
│   └── Complete Installation (All)
├── 3. Configuration
│   ├── Security Configuration
│   ├── Firewall Setup
│   ├── Backup Configuration
│   └── Network Settings
├── 4. Start/Stop Application
│   ├── Start Application
│   ├── Stop Application
│   └── Restart Application
├── 5. Status & Monitoring
│   ├── Check Status
│   ├── View Logs
│   ├── System Resources
│   └── Network Connections
├── 6. Security & Maintenance
│   ├── Run Security Audit
│   ├── Backup Now
│   ├── Update Application
│   └── Clean Up
├── 7. Documentation
│   └── View all documentation files
└── 8. Exit
```

## 🎯 Common Use Cases

### 1. First-Time Installation (Development)

```bash
./menu.sh

# Navigate through:
1. Check System Requirements      # Verify your system is ready
2. Installation Options
   → 1. Basic Installation        # Set up virtual environment
3. Configuration
   → 3. Backup Configuration      # Set up automated backups
4. Start/Stop Application
   → 1. Start Application
      → 1. Virtual Environment    # Start in dev mode
```

**Result**: Application running at `http://localhost:8501`

### 2. Production Deployment with Docker

```bash
sudo ./menu.sh

# Navigate through:
1. Check System Requirements
2. Installation Options
   → 2. Docker Installation       # Build containers
   → 5. Install Ollama           # Optional: local LLM
3. Configuration
   → 2. Firewall Setup           # Secure your server
   → 3. Backup Configuration      # Automated backups
4. Start/Stop Application
   → 1. Start Application
      → 2. Docker Compose         # Start containers
```

**Result**: Production deployment with Docker

### 3. Enterprise Deployment with SSL

```bash
sudo ./menu.sh

# Navigate through:
2. Installation Options
   → 6. Complete Installation     # Install everything
   → 4. Nginx Reverse Proxy       # Enter your domain
      (SSL will be offered automatically)
3. Configuration
   → 1. Security Configuration    # Review security
   → 2. Firewall Setup            # Configure UFW
4. Start/Stop Application
   → 1. Start Application
      → 3. Systemd Service        # Production service
```

**Result**: Enterprise-grade deployment with HTTPS

### 4. Quick Local Testing

```bash
./menu.sh

# Minimal path:
2. Installation Options
   → 1. Basic Installation
4. Start/Stop Application
   → 1. Start Application
      → 1. Virtual Environment
```

**Result**: Quick local instance for testing

## 📖 Detailed Feature Guide

### Check System Requirements
- ✅ Verifies Python 3.8+
- ✅ Checks pip availability
- ✅ Detects Docker (optional)
- ✅ Validates disk space (2GB+)
- ✅ Confirms memory (4GB+)

### Installation Options

#### Basic Installation
- Creates Python virtual environment
- Installs all dependencies
- Sets up directory structure
- Configures permissions
- **Use for**: Development, testing

#### Docker Installation
- Builds Docker images
- Creates volumes and networks
- Configures containers
- **Use for**: Production, isolation

#### Systemd Service
- Creates system service
- Enables auto-start on boot
- Configures security settings
- **Requires**: Root privileges
- **Use for**: Production servers

#### Nginx Reverse Proxy
- Installs and configures Nginx
- Sets up domain routing
- Optionally installs SSL certificate
- **Requires**: Root privileges, domain name
- **Use for**: Public-facing deployments

#### Ollama Installation
- Installs Ollama locally
- Downloads LLM models
- Configures local inference
- **Use for**: Privacy, offline usage

### Configuration Options

#### Security Configuration
- Review security settings
- Change default password
- Configure rate limits
- Set execution timeouts

#### Firewall Setup
- Configures UFW firewall
- Opens required ports (80, 443, 22)
- Blocks direct app access (8501)
- Enhances security

#### Backup Configuration
- Creates automated backup script
- Schedules daily backups (2 AM)
- Backs up: users, logs, workspace
- Retains 30 days of backups

### Management Options

#### Start Application
Choose from:
1. **Virtual Environment**: Direct execution, logs to console
2. **Docker Compose**: Containerized, runs in background
3. **Systemd Service**: System service, auto-restart

#### Stop Application
Gracefully stops the application using selected method

#### View Logs
Access to:
- Application logs (runtime)
- Audit logs (security events)
- Installation logs (setup)
- Docker logs (containers)
- Systemd logs (service)

### Monitoring Options

#### Check Status
- Application running status
- Docker container status
- Systemd service status
- Ollama status
- Disk usage
- Port availability

#### System Resources
- CPU usage
- Memory usage
- Disk space
- Network statistics

### Security & Maintenance

#### Security Audit
- Checks file permissions
- Detects default passwords
- Reviews security events
- Checks for package updates

#### Backup Now
- Immediate manual backup
- Backs up all critical data
- Stores in `~/backups/llm-factory`

#### Update Application
- Updates Python packages
- Restarts services
- Creates backup before update

#### Clean Up
- Removes temporary files
- Cleans sandbox directories
- Rotates old logs

## 🔧 Advanced Usage

### Running with Custom Options

```bash
# Start with specific Python version
python3.11 -m venv venv
./menu.sh

# Run in specific directory
cd /opt/llm-factory
./menu.sh

# Debug mode
bash -x menu.sh
```

### Environment Variables

```bash
# Set custom paths
export VENV_DIR="/custom/venv"
export APP_FILE="custom_app.py"
./menu.sh
```

### Non-Interactive Mode

For automation, you can extract functions:

```bash
# Source the menu script
source menu.sh --source-only

# Call functions directly
check_system_requirements
install_basic
start_application
```

## 🎨 Menu Features

### Color Coding
- 🔴 **Red**: Errors, critical issues
- 🟢 **Green**: Success, completed actions
- 🟡 **Yellow**: Warnings, important notes
- 🔵 **Blue**: Information, section headers
- 🟣 **Magenta**: Application name, version

### User-Friendly Elements
- ✅ Clear success/failure indicators
- 📊 Progress information
- ⚠️ Warning messages before destructive actions
- 📝 Confirmation prompts for important actions
- 📖 Built-in documentation viewer

### Logging
- All actions logged to `logs/install.log`
- Timestamp for each action
- Error details captured
- Useful for troubleshooting

## 🐛 Troubleshooting

### Menu Won't Start

```bash
# Check if file exists
ls -l menu.sh

# Make executable
chmod +x menu.sh

# Check shell
echo $SHELL  # Should be /bin/bash

# Try explicit bash
bash menu.sh
```

### Permission Errors

```bash
# Some features require root
sudo ./menu.sh

# Check file ownership
ls -l menu.sh

# Fix ownership
sudo chown $USER:$USER menu.sh
```

### Installation Fails

```bash
# Check system requirements first
./menu.sh
# → 1. Check System Requirements

# View detailed logs
tail -f logs/install.log

# Check Python version
python3 --version

# Check available disk space
df -h
```

### Application Won't Start

```bash
# Check status
./menu.sh
# → 5. Status & Monitoring
# → 1. Check Status

# View logs
./menu.sh
# → 5. Status & Monitoring
# → 2. View Logs

# Check port availability
netstat -tuln | grep 8501
```

### Docker Issues

```bash
# Check Docker status
docker --version
docker-compose --version

# Check Docker daemon
sudo systemctl status docker

# View Docker logs
docker-compose logs -f
```

## 📚 Additional Resources

### Documentation Files
- `README.md` - Main documentation
- `SECURITY.md` - Security guide
- `INSTALLATION.md` - Detailed installation
- `COMPARISON.md` - Original vs Secure comparison

### Access via Menu
Navigate to: **7. Documentation** to view any documentation file

### Command Line Viewing
```bash
# View README
less README.md

# View Security Guide
less SECURITY.md

# Search documentation
grep -r "authentication" *.md
```

## 🎓 Best Practices

### For Development
1. Use Basic Installation (Virtual Environment)
2. Start with `./menu.sh` → Option 1 → Option 2 → Option 4
3. Keep logs visible (start in foreground)
4. Review security settings

### For Production
1. Use Complete Installation (Option 6)
2. Configure Nginx with SSL
3. Set up systemd service
4. Enable firewall
5. Configure automated backups
6. Run security audit regularly

### For Testing
1. Use Docker installation
2. Easy to start/stop/reset
3. Isolated from host system
4. Quick cleanup

## 🔄 Update Workflow

```bash
# Pull latest code (if using git)
git pull

# Run menu
./menu.sh

# Navigate to:
6. Security & Maintenance
   → 3. Update Application

# Restart application
4. Start/Stop Application
   → 3. Restart Application
```

## 🎯 Pro Tips

1. **Always check requirements first** before installation
2. **Run security audit** after installation
3. **Configure backups** immediately
4. **Change default password** on first login
5. **Enable firewall** for production
6. **Monitor logs** regularly
7. **Update dependencies** monthly
8. **Test backups** periodically

## 📞 Getting Help

### Within the Menu
- All options have descriptions
- Confirmation prompts explain actions
- Error messages provide guidance
- Logs show detailed information

### Documentation
- Press `7` in main menu for documentation access
- All guides available offline
- Searchable with `less` or `grep`

### Support
- Check `logs/install.log` for errors
- Review `logs/audit.log` for security events
- Consult `TROUBLESHOOTING.md` (if available)

---

**Quick Command Reference:**

```bash
./menu.sh                    # Start interactive menu
sudo ./menu.sh              # Start with root privileges
bash -x menu.sh             # Debug mode
tail -f logs/install.log    # Watch installation log
```

**Emergency Commands:**

```bash
# Force stop everything
pkill -f streamlit
docker-compose down
sudo systemctl stop llm-factory

# Reset (BE CAREFUL - DELETES DATA)
rm -rf workspace/* sandbox/* logs/*
rm config/users.json
```

---

**Version**: 2.0.0  
**Last Updated**: February 2024  
**Compatibility**: Linux, macOS, WSL2
