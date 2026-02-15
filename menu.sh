#!/bin/bash

################################################################################
# Secure LLM Model Factory - Interactive Installation & Management Menu
# Version: 2.0.0
# This script provides a comprehensive menu system for all installation,
# configuration, deployment, and management options.
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="Secure LLM Model Factory"
VERSION="2.0.0"
VENV_DIR="$SCRIPT_DIR/venv"
APP_FILE="llm_model_factory_secure.py"
COMPOSE_FILE="docker-compose.yml"

# Log file
LOG_FILE="$SCRIPT_DIR/logs/install.log"
mkdir -p "$SCRIPT_DIR/logs"

################################################################################
# Utility Functions
################################################################################

print_header() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${MAGENTA}          🔐 $APP_NAME - v$VERSION${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BOLD}${BLUE}▶ $1${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

pause() {
    echo ""
    read -p "Press Enter to continue..."
}

confirm() {
    local prompt="$1"
    local default="${2:-n}"
    
    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    read -p "$prompt" response
    response=${response:-$default}
    
    [[ "$response" =~ ^[Yy]$ ]]
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# System Checks
################################################################################

check_system_requirements() {
    print_section "System Requirements Check"
    
    local all_good=true
    
    # Python version
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_success "Python $PYTHON_VERSION detected"
        else
            print_error "Python 3.8+ required (found $PYTHON_VERSION)"
            all_good=false
        fi
    else
        print_error "Python 3 not found"
        all_good=false
    fi
    
    # pip
    if check_command pip3 || check_command pip; then
        print_success "pip is installed"
    else
        print_error "pip not found"
        all_good=false
    fi
    
    # Git
    if check_command git; then
        print_success "Git is installed"
    else
        print_warning "Git not found (optional but recommended)"
    fi
    
    # Docker (optional)
    if check_command docker; then
        print_success "Docker is installed"
    else
        print_info "Docker not found (optional - for containerized deployment)"
    fi
    
    # Docker Compose (optional)
    if check_command docker-compose; then
        print_success "Docker Compose is installed"
    else
        print_info "Docker Compose not found (optional)"
    fi
    
    # Disk space
    AVAILABLE_SPACE=$(df -BG "$SCRIPT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [[ $AVAILABLE_SPACE -ge 2 ]]; then
        print_success "Sufficient disk space ($AVAILABLE_SPACE GB available)"
    else
        print_warning "Low disk space ($AVAILABLE_SPACE GB available, 2GB+ recommended)"
    fi
    
    # Memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $TOTAL_MEM -ge 4 ]]; then
        print_success "Sufficient memory ($TOTAL_MEM GB)"
    else
        print_warning "Limited memory ($TOTAL_MEM GB, 4GB+ recommended)"
    fi
    
    echo ""
    if [[ "$all_good" == true ]]; then
        print_success "All requirements met!"
    else
        print_error "Some requirements not met. Installation may fail."
    fi
    
    log_message "System requirements check completed"
    pause
}

################################################################################
# Installation Functions
################################################################################

install_basic() {
    print_section "Basic Installation (Virtual Environment)"
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip &>> "$LOG_FILE"
    print_success "pip upgraded"
    
    # Install requirements
    print_info "Installing Python dependencies..."
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        pip install -r "$SCRIPT_DIR/requirements.txt" &>> "$LOG_FILE"
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Create directory structure
    print_info "Creating directory structure..."
    mkdir -p "$SCRIPT_DIR"/{workspace,sandbox,logs,config}
    print_success "Directories created"
    
    # Set permissions
    chmod 755 "$SCRIPT_DIR"
    chmod 700 "$SCRIPT_DIR/config"
    print_success "Permissions set"
    
    print_success "Basic installation completed!"
    log_message "Basic installation completed successfully"
    
    echo ""
    print_info "To activate the virtual environment, run:"
    echo "  source $VENV_DIR/bin/activate"
    
    pause
}

install_docker() {
    print_section "Docker Installation"
    
    if ! check_command docker; then
        print_error "Docker not found. Please install Docker first."
        print_info "Visit: https://docs.docker.com/get-docker/"
        pause
        return 1
    fi
    
    if [[ ! -f "$SCRIPT_DIR/$COMPOSE_FILE" ]]; then
        print_error "docker-compose.yml not found"
        pause
        return 1
    fi
    
    print_info "Building Docker images..."
    docker-compose build
    print_success "Docker images built"
    
    print_info "Creating volumes and networks..."
    docker-compose up --no-start
    print_success "Container setup complete"
    
    print_success "Docker installation completed!"
    log_message "Docker installation completed successfully"
    
    echo ""
    print_info "To start the application, run:"
    echo "  docker-compose up -d"
    
    pause
}

install_systemd() {
    print_section "Systemd Service Installation"
    
    if ! check_root; then
        print_error "Root privileges required for systemd installation"
        print_info "Please run: sudo ./menu.sh"
        pause
        return 1
    fi
    
    SERVICE_FILE="/etc/systemd/system/llm-factory.service"
    
    print_info "Creating systemd service..."
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Secure LLM Model Factory
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/streamlit run $APP_FILE --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$SCRIPT_DIR/workspace $SCRIPT_DIR/logs $SCRIPT_DIR/config

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Service file created"
    
    systemctl daemon-reload
    systemctl enable llm-factory.service
    print_success "Service enabled"
    
    log_message "Systemd service installed successfully"
    
    echo ""
    print_info "Service installed. To start:"
    echo "  sudo systemctl start llm-factory"
    echo "  sudo systemctl status llm-factory"
    
    pause
}

install_nginx() {
    print_section "Nginx Reverse Proxy Installation"
    
    if ! check_root; then
        print_error "Root privileges required"
        pause
        return 1
    fi
    
    if ! check_command nginx; then
        print_info "Installing Nginx..."
        apt-get update &>> "$LOG_FILE"
        apt-get install -y nginx &>> "$LOG_FILE"
        print_success "Nginx installed"
    else
        print_info "Nginx already installed"
    fi
    
    read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
    
    NGINX_CONF="/etc/nginx/sites-available/llm-factory"
    
    print_info "Creating Nginx configuration..."
    
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
EOF
    
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    nginx -t &>> "$LOG_FILE"
    systemctl reload nginx
    
    print_success "Nginx configured for domain: $DOMAIN_NAME"
    
    if confirm "Install SSL certificate with Let's Encrypt?" y; then
        install_ssl "$DOMAIN_NAME"
    fi
    
    log_message "Nginx installed successfully"
    pause
}

install_ssl() {
    local domain="$1"
    
    print_section "SSL Certificate Installation"
    
    if ! check_command certbot; then
        print_info "Installing Certbot..."
        apt-get update &>> "$LOG_FILE"
        apt-get install -y certbot python3-certbot-nginx &>> "$LOG_FILE"
        print_success "Certbot installed"
    fi
    
    print_info "Obtaining SSL certificate for $domain..."
    certbot --nginx -d "$domain" --non-interactive --agree-tos --email admin@"$domain"
    
    print_success "SSL certificate installed!"
    print_info "Your site is now accessible at https://$domain"
}

install_ollama() {
    print_section "Ollama Local LLM Installation"
    
    if check_command ollama; then
        print_info "Ollama already installed"
    else
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        print_success "Ollama installed"
    fi
    
    print_info "Available models:"
    echo "  1) llama3 (7B - Recommended)"
    echo "  2) mistral (7B)"
    echo "  3) codellama (7B - Code focused)"
    echo "  4) phi3 (3.8B - Lightweight)"
    echo "  5) Skip model download"
    
    read -p "Select model to download (1-5): " MODEL_CHOICE
    
    case $MODEL_CHOICE in
        1) MODEL="llama3" ;;
        2) MODEL="mistral" ;;
        3) MODEL="codellama" ;;
        4) MODEL="phi3" ;;
        5) print_info "Skipping model download"; pause; return ;;
        *) print_error "Invalid choice"; pause; return ;;
    esac
    
    print_info "Downloading $MODEL model (this may take a while)..."
    ollama pull "$MODEL"
    print_success "$MODEL model downloaded"
    
    print_info "Testing Ollama..."
    ollama list
    
    log_message "Ollama installed with model: $MODEL"
    pause
}

################################################################################
# Configuration Functions
################################################################################

configure_security() {
    print_section "Security Configuration"
    
    echo "Current security settings can be modified in $APP_FILE"
    echo ""
    echo "Available settings:"
    echo "  • MAX_FILE_SIZE_MB: Maximum upload size (default: 10)"
    echo "  • MAX_EXECUTION_TIME: Code execution timeout (default: 30s)"
    echo "  • MAX_DAILY_EXECUTIONS: Rate limit per user (default: 100)"
    echo "  • REQUIRE_CONFIRMATION: Double-confirm actions (default: True)"
    echo "  • SANDBOX_ENABLED: Enforce sandboxing (default: True)"
    echo ""
    
    if confirm "Change default admin password now?" y; then
        change_admin_password
    fi
    
    if confirm "Configure firewall rules?" n; then
        configure_firewall
    fi
    
    pause
}

change_admin_password() {
    print_info "The default password will be changed on first login"
    print_warning "Default credentials: admin / admin123"
    print_info "Please change this immediately after first login!"
}

configure_firewall() {
    print_section "Firewall Configuration"
    
    if ! check_root; then
        print_error "Root privileges required"
        return 1
    fi
    
    if check_command ufw; then
        print_info "Configuring UFW firewall..."
        
        ufw allow 22/tcp comment "SSH"
        ufw allow 80/tcp comment "HTTP"
        ufw allow 443/tcp comment "HTTPS"
        ufw deny 8501/tcp comment "Block direct Streamlit access"
        
        if confirm "Enable firewall now?" y; then
            ufw --force enable
            print_success "Firewall enabled and configured"
        fi
    else
        print_warning "UFW not found. Install with: sudo apt-get install ufw"
    fi
    
    log_message "Firewall configured"
}

configure_backup() {
    print_section "Backup Configuration"
    
    BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"
    
    cat > "$BACKUP_SCRIPT" << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/backups/llm-factory"

mkdir -p "$BACKUP_DIR"

# Backup user database
cp config/users.json "$BACKUP_DIR/users_$DATE.json" 2>/dev/null

# Backup audit logs
cp logs/audit.log "$BACKUP_DIR/audit_$DATE.log" 2>/dev/null

# Backup workspace
tar -czf "$BACKUP_DIR/workspace_$DATE.tar.gz" workspace/ 2>/dev/null

# Keep only last 30 days
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x "$BACKUP_SCRIPT"
    print_success "Backup script created at $BACKUP_SCRIPT"
    
    if confirm "Add to crontab (daily 2 AM)?" y; then
        (crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT") | crontab -
        print_success "Backup scheduled in crontab"
    fi
    
    log_message "Backup configured"
    pause
}

################################################################################
# Management Functions
################################################################################

start_application() {
    print_section "Start Application"
    
    echo "Choose startup method:"
    echo "  1) Virtual Environment (development)"
    echo "  2) Docker Compose"
    echo "  3) Systemd Service"
    echo "  4) Back"
    
    read -p "Select option (1-4): " choice
    
    case $choice in
        1)
            if [[ ! -d "$VENV_DIR" ]]; then
                print_error "Virtual environment not found. Run installation first."
                pause
                return
            fi
            
            print_info "Starting application..."
            source "$VENV_DIR/bin/activate"
            streamlit run "$APP_FILE" --server.address 0.0.0.0 --server.port 8501
            ;;
        2)
            if ! check_command docker-compose; then
                print_error "Docker Compose not found"
                pause
                return
            fi
            
            print_info "Starting Docker containers..."
            docker-compose up -d
            print_success "Containers started"
            
            echo ""
            print_info "View logs with: docker-compose logs -f"
            pause
            ;;
        3)
            if ! check_root; then
                print_error "Root privileges required"
                pause
                return
            fi
            
            systemctl start llm-factory
            systemctl status llm-factory
            pause
            ;;
        4)
            return
            ;;
        *)
            print_error "Invalid option"
            pause
            ;;
    esac
}

stop_application() {
    print_section "Stop Application"
    
    echo "Choose method:"
    echo "  1) Docker Compose"
    echo "  2) Systemd Service"
    echo "  3) Kill all Streamlit processes"
    echo "  4) Back"
    
    read -p "Select option (1-4): " choice
    
    case $choice in
        1)
            docker-compose down
            print_success "Docker containers stopped"
            ;;
        2)
            if check_root; then
                systemctl stop llm-factory
                print_success "Service stopped"
            else
                print_error "Root privileges required"
            fi
            ;;
        3)
            pkill -f streamlit
            print_success "Streamlit processes killed"
            ;;
        4)
            return
            ;;
    esac
    
    pause
}

view_logs() {
    print_section "View Logs"
    
    echo "Select log to view:"
    echo "  1) Application log"
    echo "  2) Audit log"
    echo "  3) Installation log"
    echo "  4) Docker logs (if applicable)"
    echo "  5) Systemd logs (if applicable)"
    echo "  6) Back"
    
    read -p "Select option (1-6): " choice
    
    case $choice in
        1)
            if [[ -f "$SCRIPT_DIR/logs/app.log" ]]; then
                tail -f "$SCRIPT_DIR/logs/app.log"
            else
                print_error "Application log not found"
            fi
            ;;
        2)
            if [[ -f "$SCRIPT_DIR/logs/audit.log" ]]; then
                tail -f "$SCRIPT_DIR/logs/audit.log"
            else
                print_error "Audit log not found"
            fi
            ;;
        3)
            if [[ -f "$LOG_FILE" ]]; then
                less "$LOG_FILE"
            else
                print_error "Installation log not found"
            fi
            ;;
        4)
            docker-compose logs -f
            ;;
        5)
            if check_root; then
                journalctl -u llm-factory -f
            else
                print_error "Root privileges required"
            fi
            ;;
        6)
            return
            ;;
    esac
    
    pause
}

check_status() {
    print_section "System Status"
    
    # Check if application is running
    if pgrep -f streamlit > /dev/null; then
        print_success "Application is running (PID: $(pgrep -f streamlit))"
    else
        print_warning "Application is not running"
    fi
    
    # Check Docker
    if check_command docker; then
        if docker-compose ps 2>/dev/null | grep -q "Up"; then
            print_success "Docker containers are running"
            docker-compose ps
        else
            print_info "Docker containers not running"
        fi
    fi
    
    # Check systemd
    if systemctl is-active --quiet llm-factory 2>/dev/null; then
        print_success "Systemd service is active"
    else
        print_info "Systemd service not active"
    fi
    
    # Check Ollama
    if check_command ollama; then
        if pgrep -f ollama > /dev/null; then
            print_success "Ollama is running"
            echo ""
            ollama list
        else
            print_info "Ollama is installed but not running"
        fi
    fi
    
    # Disk usage
    echo ""
    print_info "Disk Usage:"
    du -sh "$SCRIPT_DIR"/{workspace,logs,sandbox} 2>/dev/null || true
    
    # Port check
    echo ""
    print_info "Port 8501 status:"
    if netstat -tuln 2>/dev/null | grep -q ":8501 "; then
        print_success "Port 8501 is in use (application likely running)"
    else
        print_warning "Port 8501 is not in use"
    fi
    
    pause
}

run_security_audit() {
    print_section "Security Audit"
    
    print_info "Checking security configuration..."
    
    # Check file permissions
    if [[ $(stat -c %a "$SCRIPT_DIR/config") == "700" ]]; then
        print_success "Config directory permissions: OK"
    else
        print_warning "Config directory should be 700"
    fi
    
    # Check for default password
    if [[ -f "$SCRIPT_DIR/config/users.json" ]]; then
        if grep -q "admin123" "$SCRIPT_DIR/config/users.json" 2>/dev/null; then
            print_error "Default admin password detected! Change immediately!"
        else
            print_success "Default password has been changed"
        fi
    else
        print_info "User database not yet created"
    fi
    
    # Check audit log
    if [[ -f "$SCRIPT_DIR/logs/audit.log" ]]; then
        FAILED_LOGINS=$(grep -c "LOGIN_FAILED" "$SCRIPT_DIR/logs/audit.log" 2>/dev/null || echo 0)
        BLOCKED_CODE=$(grep -c "CODE_BLOCKED" "$SCRIPT_DIR/logs/audit.log" 2>/dev/null || echo 0)
        
        echo ""
        print_info "Security Events:"
        echo "  Failed logins: $FAILED_LOGINS"
        echo "  Blocked code: $BLOCKED_CODE"
    fi
    
    # Check for updates
    echo ""
    print_info "Checking for outdated Python packages..."
    if [[ -d "$VENV_DIR" ]]; then
        source "$VENV_DIR/bin/activate"
        pip list --outdated 2>/dev/null || true
    fi
    
    pause
}

backup_now() {
    print_section "Manual Backup"
    
    if [[ -f "$SCRIPT_DIR/backup.sh" ]]; then
        print_info "Running backup..."
        bash "$SCRIPT_DIR/backup.sh"
        print_success "Backup completed"
    else
        print_error "Backup script not found. Run configuration first."
    fi
    
    pause
}

update_application() {
    print_section "Update Application"
    
    print_warning "This will pull the latest code and restart services"
    
    if ! confirm "Continue with update?" n; then
        return
    fi
    
    # Backup current version
    print_info "Creating backup..."
    cp "$APP_FILE" "$APP_FILE.backup.$(date +%s)"
    
    # Update Python dependencies
    if [[ -d "$VENV_DIR" ]]; then
        print_info "Updating Python packages..."
        source "$VENV_DIR/bin/activate"
        pip install --upgrade -r requirements.txt
    fi
    
    # Restart services
    if systemctl is-active --quiet llm-factory 2>/dev/null; then
        print_info "Restarting systemd service..."
        sudo systemctl restart llm-factory
    fi
    
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        print_info "Restarting Docker containers..."
        docker-compose restart
    fi
    
    print_success "Update completed"
    log_message "Application updated"
    
    pause
}

################################################################################
# Main Menu
################################################################################

show_main_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Main Menu${NC}"
        echo ""
        echo "  1) 🔍 Check System Requirements"
        echo "  2) 📦 Installation Options"
        echo "  3) ⚙️  Configuration"
        echo "  4) 🚀 Start/Stop Application"
        echo "  5) 📊 Status & Monitoring"
        echo "  6) 🛡️  Security & Maintenance"
        echo "  7) 📚 Documentation"
        echo "  8) 🚪 Exit"
        echo ""
        read -p "Select option (1-8): " choice
        
        case $choice in
            1) check_system_requirements ;;
            2) show_installation_menu ;;
            3) show_configuration_menu ;;
            4) show_management_menu ;;
            5) show_monitoring_menu ;;
            6) show_security_menu ;;
            7) show_documentation_menu ;;
            8) 
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                pause
                ;;
        esac
    done
}

show_installation_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Installation Options${NC}"
        echo ""
        echo "  1) 🐍 Basic Installation (Virtual Environment)"
        echo "  2) 🐳 Docker Installation"
        echo "  3) ⚙️  Systemd Service Installation"
        echo "  4) 🌐 Nginx Reverse Proxy"
        echo "  5) 🤖 Install Ollama (Local LLM)"
        echo "  6) 📦 Complete Installation (All)"
        echo "  7) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-7): " choice
        
        case $choice in
            1) install_basic ;;
            2) install_docker ;;
            3) install_systemd ;;
            4) install_nginx ;;
            5) install_ollama ;;
            6) 
                install_basic
                install_docker
                install_ollama
                configure_backup
                print_success "Complete installation finished!"
                pause
                ;;
            7) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

show_configuration_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Configuration${NC}"
        echo ""
        echo "  1) 🔐 Security Configuration"
        echo "  2) 🔥 Firewall Setup"
        echo "  3) 💾 Backup Configuration"
        echo "  4) 🌐 Network Settings"
        echo "  5) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-5): " choice
        
        case $choice in
            1) configure_security ;;
            2) configure_firewall ;;
            3) configure_backup ;;
            4) 
                print_info "Network settings can be configured in:"
                echo "  • $APP_FILE (API settings)"
                echo "  • docker-compose.yml (Docker networks)"
                echo "  • /etc/nginx/sites-available/llm-factory (Nginx)"
                pause
                ;;
            5) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

show_management_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Application Management${NC}"
        echo ""
        echo "  1) ▶️  Start Application"
        echo "  2) ⏹️  Stop Application"
        echo "  3) 🔄 Restart Application"
        echo "  4) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-4): " choice
        
        case $choice in
            1) start_application ;;
            2) stop_application ;;
            3) 
                stop_application
                sleep 2
                start_application
                ;;
            4) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

show_monitoring_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Status & Monitoring${NC}"
        echo ""
        echo "  1) 📊 Check Status"
        echo "  2) 📜 View Logs"
        echo "  3) 💻 System Resources"
        echo "  4) 🌐 Network Connections"
        echo "  5) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-5): " choice
        
        case $choice in
            1) check_status ;;
            2) view_logs ;;
            3) 
                print_section "System Resources"
                echo "CPU Usage:"
                top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
                echo ""
                echo "Memory Usage:"
                free -h
                echo ""
                echo "Disk Usage:"
                df -h "$SCRIPT_DIR"
                pause
                ;;
            4)
                print_section "Network Connections"
                netstat -tuln | grep -E ":(8501|11434|80|443) "
                pause
                ;;
            5) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

show_security_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Security & Maintenance${NC}"
        echo ""
        echo "  1) 🔍 Run Security Audit"
        echo "  2) 💾 Backup Now"
        echo "  3) 🔄 Update Application"
        echo "  4) 🗑️  Clean Up"
        echo "  5) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-5): " choice
        
        case $choice in
            1) run_security_audit ;;
            2) backup_now ;;
            3) update_application ;;
            4)
                print_section "Cleanup"
                print_info "Cleaning temporary files..."
                rm -rf "$SCRIPT_DIR/sandbox/"*
                find "$SCRIPT_DIR/logs" -name "*.log.*" -mtime +30 -delete
                print_success "Cleanup completed"
                pause
                ;;
            5) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

show_documentation_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Documentation${NC}"
        echo ""
        echo "  1) 📖 View README"
        echo "  2) 🔐 View Security Guide"
        echo "  3) 📦 View Installation Guide"
        echo "  4) 🔄 View Comparison Document"
        echo "  5) 🌐 Open Documentation in Browser"
        echo "  6) 🔙 Back to Main Menu"
        echo ""
        read -p "Select option (1-6): " choice
        
        case $choice in
            1) less "$SCRIPT_DIR/README.md" 2>/dev/null || print_error "README.md not found" ;;
            2) less "$SCRIPT_DIR/SECURITY.md" 2>/dev/null || print_error "SECURITY.md not found" ;;
            3) less "$SCRIPT_DIR/INSTALLATION.md" 2>/dev/null || print_error "INSTALLATION.md not found" ;;
            4) less "$SCRIPT_DIR/COMPARISON.md" 2>/dev/null || print_error "COMPARISON.md not found" ;;
            5)
                if check_command xdg-open; then
                    xdg-open "$SCRIPT_DIR/README.md" 2>/dev/null
                elif check_command open; then
                    open "$SCRIPT_DIR/README.md" 2>/dev/null
                else
                    print_error "Cannot open browser automatically"
                fi
                ;;
            6) break ;;
            *) print_error "Invalid option"; pause ;;
        esac
    done
}

################################################################################
# Script Entry Point
################################################################################

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log script start
log_message "===== Script started ====="

# Check if running in correct directory
if [[ ! -f "$SCRIPT_DIR/$APP_FILE" ]]; then
    print_error "Application file not found: $APP_FILE"
    print_info "Please run this script from the application directory"
    exit 1
fi

# Show main menu
show_main_menu
