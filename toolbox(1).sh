#!/bin/bash

# ==========================================================
# 🚀 GRAND UNIFIED MASTER TOOLBOX v27.0
# ENHANCED EDITION - Added Ollama Management & Setup.sh
# ==========================================================

set -o pipefail  # Exit on pipe failures

# --- GLOBAL CONFIGURATION ---
SCRIPT_VERSION="27.0"
SCRIPT_PATH="/usr/local/bin/toolbox"
LOG_DIR="$HOME/.toolbox/logs"
BACKUP_DIR="$HOME/.toolbox/backups"
CONFIG_FILE="$HOME/.toolbox/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SETUP_SCRIPT="./setup.sh"  # Path to setup.sh script

# Create directories
mkdir -p "$LOG_DIR" "$BACKUP_DIR" "$HOME/.toolbox"

# Colors
RED='\033[1;31m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'
BLUE='\033[1;34m'; MAGENTA='\033[1;35m'; CYAN='\033[1;36m'
WHITE='\033[1;37m'; STD='\033[0m'; BOLD='\033[1m'

# --- LOGGING FUNCTIONS ---
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_DIR/toolbox_${TIMESTAMP}.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_DIR/toolbox_${TIMESTAMP}.log"
    echo -e "${RED}ERROR: $1${STD}" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "$LOG_DIR/toolbox_${TIMESTAMP}.log"
    echo -e "${GREEN}✓ $1${STD}"
}

# --- UTILITY FUNCTIONS ---
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This operation requires root privileges"
        return 1
    fi
    return 0
}

check_internet() {
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        log_error "No internet connection detected"
        return 1
    fi
    return 0
}

pause() {
    echo ""
    read -r -p "  Press [Enter] to continue..."
}

confirm_action() {
    local prompt="$1"
    local response
    read -p "$prompt (y/n): " response
    [[ "$response" =~ ^[Yy]$ ]]
}

create_backup() {
    local file="$1"
    local backup_name="$2"
    if [[ -f "$file" ]]; then
        cp "$file" "$BACKUP_DIR/${backup_name}_${TIMESTAMP}" && \
        log_success "Backup created: ${backup_name}_${TIMESTAMP}"
    fi
}

# --- PACKAGE MANAGER DETECTION ---
detect_package_manager() {
    if command -v apt &> /dev/null; then
        PKGMGR="apt"
        INSTALL_CMD="sudo apt install -y"
        UPDATE_CMD="sudo apt update"
        UPGRADE_CMD="sudo apt upgrade -y"
        CLEAN_CMD="sudo apt autoremove -y && sudo apt clean"
    elif command -v dnf &> /dev/null; then
        PKGMGR="dnf"
        INSTALL_CMD="sudo dnf install -y"
        UPDATE_CMD="sudo dnf check-update"
        UPGRADE_CMD="sudo dnf upgrade -y"
        CLEAN_CMD="sudo dnf autoremove -y && sudo dnf clean all"
    elif command -v pacman &> /dev/null; then
        PKGMGR="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
        UPDATE_CMD="sudo pacman -Sy"
        UPGRADE_CMD="sudo pacman -Syu --noconfirm"
        CLEAN_CMD="sudo pacman -Sc --noconfirm"
    else
        log_error "Unsupported package manager"
        exit 1
    fi
    log_msg "Detected package manager: $PKGMGR"
}

# --- DEPENDENCY INSTALLER ---
install_dependencies() {
    echo -e "${CYAN}--- Installing Dependencies ---${STD}"
    
    # Core dependencies
    local CORE_DEPS="bc curl pciutils htop ncdu git wget"
    
    # Optional but recommended
    local OPT_DEPS="xterm fastfetch stress-ng timeshift testdisk mc"
    
    # GPU-specific
    if [[ "$GPU_VENDOR" == "AMD" ]] || [[ "$GPU_VENDOR" == "Intel" ]]; then
        OPT_DEPS="$OPT_DEPS radeontop"
    fi
    
    # Try glmark2
    OPT_DEPS="$OPT_DEPS glmark2"
    
    # Android tools
    if confirm_action "Install Android tools (adb, scrcpy)?"; then
        OPT_DEPS="$OPT_DEPS android-tools-adb scrcpy"
    fi
    
    # Podman
    if confirm_action "Install Podman and Podman Compose?"; then
        OPT_DEPS="$OPT_DEPS podman"
        # Podman-compose via pip
        if command -v pip3 &> /dev/null; then
            sudo pip3 install podman-compose 2>/dev/null || true
        fi
    fi
    
    log_msg "Installing core dependencies: $CORE_DEPS"
    $UPDATE_CMD
    $INSTALL_CMD $CORE_DEPS || log_error "Failed to install some core dependencies"
    
    log_msg "Installing optional dependencies: $OPT_DEPS"
    $INSTALL_CMD $OPT_DEPS 2>/dev/null || log_msg "Some optional packages not available"
    
    log_success "Dependency installation completed"
}

# --- HARDWARE DETECTION ---
detect_hardware() {
    # GPU Detection with specific model identification
    GPU_VENDOR="Unknown"
    GPU_MODEL=""
    
    # Check for Intel Arc GPUs first (DG2/Alchemist)
    if lspci | grep -qi "Intel.*\(Arc\|DG2\|Alchemist\)"; then
        GPU_VENDOR="Intel Arc"
        GPU_MODEL=$(lspci | grep -i "vga\|3d\|display" | grep -i intel | head -n1)
    elif lspci | grep -qi "nvidia"; then
        GPU_VENDOR="Nvidia"
        GPU_MODEL=$(lspci | grep -i "vga\|3d" | grep -i nvidia | head -n1)
    elif lspci | grep -qi "amd" || lspci | grep -qi "ati"; then
        GPU_VENDOR="AMD"
        GPU_MODEL=$(lspci | grep -i "vga\|3d" | grep -i "amd\|ati" | head -n1)
    elif lspci | grep -qi "intel.*\(vga\|display\)"; then
        GPU_VENDOR="Intel iGPU"
        GPU_MODEL=$(lspci | grep -i "vga\|display" | grep -i intel | head -n1)
    fi
    
    # CPU Detection
    CPU_MODEL=$(lscpu | grep "Model name" | sed 's/Model name:[[:space:]]*//')
    CPU_CORES=$(nproc)
    
    # Memory
    TOTAL_RAM=$(free -h | awk '/^Mem:/ {print $2}')
    
    log_msg "Hardware detected - GPU: $GPU_VENDOR, CPU: $CPU_MODEL ($CPU_CORES cores), RAM: $TOTAL_RAM"
}

# --- TERMINAL SPAWNING ---
SpawnTerminal() {
    local CMD="$1"
    local TITLE="$2"
    
    if [[ -z "$DISPLAY" ]]; then
        eval "$CMD"
        pause
        return
    fi
    
    # Try various terminal emulators
    if command -v xterm &> /dev/null; then
        xterm -T "$TITLE" -e "bash -c \"$CMD; read -p 'Press Enter to close...'\"" &
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$TITLE" -- bash -c "$CMD; read -p 'Press Enter to close...'" &
    elif command -v konsole &> /dev/null; then
        konsole --title "$TITLE" -e bash -c "$CMD; read -p 'Press Enter to close...'" &
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal --title="$TITLE" -e "bash -c \"$CMD; read -p 'Press Enter to close...'\"" &
    else
        log_error "No suitable terminal emulator found"
        eval "$CMD"
        pause
    fi
}

# --- HEADER DISPLAY ---
DrawHeader() {
    clear
    
    # Fastfetch if available
    if command -v fastfetch &> /dev/null; then
        fastfetch --compact --structure OS:Host:Kernel:Uptime:Packages:DE:CPU:GPU:Memory
    else
        echo -e "${BOLD}System: $(hostname) | $(uname -r)${STD}"
        echo -e "CPU: $CPU_MODEL ($CPU_CORES cores) | RAM: $TOTAL_RAM"
    fi
    
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════════════════╗${STD}"
    printf "${BLUE}║${STD} ${YELLOW}%-15s${STD}: %-25s ${YELLOW}%-15s${STD}: %-28s ${BLUE}║${STD}\n" \
        "Version" "v$SCRIPT_VERSION" "GPU" "$GPU_VENDOR"
    printf "${BLUE}║${STD} ${YELLOW}%-15s${STD}: %-25s ${YELLOW}%-15s${STD}: %-28s ${BLUE}║${STD}\n" \
        "Package Mgr" "$PKGMGR" "Local IP" "$(hostname -I | awk '{print $1}')"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════════╝${STD}"
}

# --- MODULE: SYSTEM MAINTENANCE ---
maintenance_install_tools() {
    echo -e "${CYAN}Installing essential system tools...${STD}"
    local tools="curl wget bc htop ncdu timeshift testdisk git mc tree vim nano rsync"
    
    if confirm_action "Install all tools ($tools)?"; then
        log_msg "Installing tools: $tools"
        $INSTALL_CMD $tools
        log_success "Tools installed successfully"
    fi
    pause
}

maintenance_update_system() {
    echo -e "${CYAN}Updating system with $PKGMGR...${STD}"
    log_msg "System update started"
    
    $UPDATE_CMD
    $UPGRADE_CMD
    
    log_success "System updated successfully"
    pause
}

maintenance_cleanup() {
    echo -e "${CYAN}Cleaning up system...${STD}"
    log_msg "System cleanup started"
    
    $CLEAN_CMD
    
    # Clean logs older than 30 days
    find "$LOG_DIR" -type f -mtime +30 -delete 2>/dev/null
    
    # Clean old backups
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -type f -mtime +90 -delete 2>/dev/null
    fi
    
    log_success "System cleanup completed"
    pause
}

maintenance_kill_zombies() {
    echo -e "${CYAN}Searching for zombie processes...${STD}"
    
    zombies=$(ps aux | awk '$8=="Z" {print $2}')
    
    if [[ -z "$zombies" ]]; then
        echo -e "${GREEN}No zombie processes found${STD}"
    else
        echo "Found zombie processes:"
        ps aux | awk '$8=="Z"'
        echo ""
        if confirm_action "Attempt to clean zombies?"; then
            for pid in $zombies; do
                parent=$(ps -o ppid= -p $pid | tr -d ' ')
                if [[ -n "$parent" ]]; then
                    sudo kill -9 $parent 2>/dev/null && \
                        log_success "Killed parent process $parent" || \
                        log_error "Failed to kill parent process $parent"
                fi
            done
        fi
    fi
    pause
}

maintenance_service_manager() {
    echo -e "${CYAN}Service Manager${STD}"
    echo ""
    echo "1. List all services"
    echo "2. List running services"
    echo "3. Start a service"
    echo "4. Stop a service"
    echo "5. Restart a service"
    echo "6. Enable service at boot"
    echo "7. Disable service at boot"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " svc_choice
    
    case $svc_choice in
        1) systemctl list-units --type=service --all | less ;;
        2) systemctl list-units --type=service --state=running | less ;;
        3)
            read -r -p "Service name: " svc_name
            sudo systemctl start "$svc_name" && \
                log_success "Started $svc_name" || \
                log_error "Failed to start $svc_name"
            ;;
        4)
            read -r -p "Service name: " svc_name
            sudo systemctl stop "$svc_name" && \
                log_success "Stopped $svc_name" || \
                log_error "Failed to stop $svc_name"
            ;;
        5)
            read -r -p "Service name: " svc_name
            sudo systemctl restart "$svc_name" && \
                log_success "Restarted $svc_name" || \
                log_error "Failed to restart $svc_name"
            ;;
        6)
            read -r -p "Service name: " svc_name
            sudo systemctl enable "$svc_name" && \
                log_success "Enabled $svc_name at boot" || \
                log_error "Failed to enable $svc_name"
            ;;
        7)
            read -r -p "Service name: " svc_name
            sudo systemctl disable "$svc_name" && \
                log_success "Disabled $svc_name at boot" || \
                log_error "Failed to disable $svc_name"
            ;;
    esac
    pause
}

# --- MODULE: RESCUE & RECOVERY ---
rescue_auto_diagnostic() {
    echo -e "${CYAN}Running Auto-Diagnostic...${STD}"
    log_msg "Auto-diagnostic started"
    
    echo ""
    echo "Checking disk space..."
    df -h / | tail -1 | awk '{
        usage = substr($5, 1, length($5)-1);
        if (usage > 90) print "⚠ WARNING: Disk usage at " $5;
        else print "✓ Disk usage OK: " $5;
    }'
    
    echo ""
    echo "Checking memory..."
    free -h | awk '/^Mem:/ {
        used = substr($3, 1, length($3)-1);
        total = substr($2, 1, length($2)-1);
        percent = (used / total) * 100;
        if (percent > 90) print "⚠ WARNING: Memory usage high";
        else print "✓ Memory usage OK";
    }'
    
    echo ""
    echo "Checking for failed services..."
    failed=$(systemctl list-units --state=failed --no-legend | wc -l)
    if [[ $failed -gt 0 ]]; then
        echo "⚠ WARNING: $failed failed services"
        systemctl list-units --state=failed
    else
        echo "✓ No failed services"
    fi
    
    echo ""
    echo "Checking system logs for errors..."
    error_count=$(journalctl -p err -b --no-pager | wc -l)
    if [[ $error_count -gt 0 ]]; then
        echo "⚠ Found $error_count errors in system logs"
        if confirm_action "View error logs?"; then
            journalctl -p err -b | less
        fi
    else
        echo "✓ No critical errors in logs"
    fi
    
    log_success "Auto-diagnostic completed"
    pause
}

rescue_graphics_menu() {
    echo -e "${CYAN}Graphics Repair Menu (GPU: $GPU_VENDOR)${STD}"
    echo ""
    echo "1. Reinstall graphics drivers"
    echo "2. Check graphics configuration"
    echo "3. Reset graphics settings"
    echo "4. Switch to integrated graphics"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " gfx_choice
    
    case $gfx_choice in
        1)
            case $GPU_VENDOR in
                Nvidia)
                    echo "Reinstalling Nvidia drivers..."
                    $INSTALL_CMD nvidia-driver || log_error "Driver installation failed"
                    ;;
                AMD)
                    echo "Reinstalling AMD drivers..."
                    $INSTALL_CMD xserver-xorg-video-amdgpu || log_error "Driver installation failed"
                    ;;
                "Intel"*|"Intel Arc")
                    echo "Reinstalling Intel drivers..."
                    $INSTALL_CMD xserver-xorg-video-intel || log_error "Driver installation failed"
                    ;;
                *)
                    echo "Unknown GPU vendor. Install drivers manually."
                    ;;
            esac
            ;;
        2)
            echo "Graphics configuration:"
            lspci | grep -i "vga\|3d\|display"
            echo ""
            glxinfo | grep -i "renderer\|version" 2>/dev/null || echo "glxinfo not available"
            ;;
        3)
            echo "Resetting graphics settings..."
            mv ~/.config/monitors.xml ~/.config/monitors.xml.bak 2>/dev/null
            log_success "Graphics settings reset"
            ;;
        4)
            echo "This requires manual BIOS configuration"
            echo "Reboot and enter BIOS to switch graphics"
            ;;
    esac
    pause
}

rescue_disk_analyzer() {
    echo -e "${CYAN}Disk Analyzer${STD}"
    echo ""
    
    if command -v ncdu &> /dev/null; then
        echo "Starting ncdu..."
        ncdu /
    else
        echo "ncdu not installed. Using du..."
        echo ""
        echo "Top 20 largest directories:"
        sudo du -h / 2>/dev/null | sort -rh | head -20
    fi
    pause
}

rescue_grub_cheatsheet() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${STD}"
    echo -e "${CYAN}║              GRUB RESCUE CHEATSHEET                    ║${STD}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${STD}"
    echo ""
    echo "Common GRUB rescue commands:"
    echo ""
    echo -e "${GREEN}1. Find your boot partition:${STD}"
    echo "   ls"
    echo "   ls (hd0,1)/"
    echo ""
    echo -e "${GREEN}2. Set boot partition:${STD}"
    echo "   set root=(hd0,1)"
    echo "   set prefix=(hd0,1)/boot/grub"
    echo ""
    echo -e "${GREEN}3. Load modules:${STD}"
    echo "   insmod normal"
    echo "   normal"
    echo ""
    echo -e "${GREEN}4. After booting, reinstall GRUB:${STD}"
    echo "   sudo grub-install /dev/sda"
    echo "   sudo update-grub"
    echo ""
    pause
}

rescue_boot_repair() {
    echo -e "${CYAN}Boot Repair Utility${STD}"
    echo ""
    echo "This will attempt to repair your bootloader"
    echo ""
    
    if confirm_action "Proceed with boot repair?"; then
        echo "Reinstalling GRUB..."
        
        # Detect boot drive
        boot_drive=$(df /boot | tail -1 | awk '{print $1}' | sed 's/[0-9]*$//')
        
        echo "Detected boot drive: $boot_drive"
        
        if confirm_action "Install GRUB to $boot_drive?"; then
            sudo grub-install "$boot_drive" && \
                sudo update-grub && \
                log_success "GRUB reinstalled successfully" || \
                log_error "GRUB installation failed"
        fi
    fi
    pause
}

# --- MODULE: DEV, AI & CONTAINERS ---

# ── NEW: OLLAMA MANAGEMENT MENU ──
dev_ollama_management() {
    while true; do
        clear
        echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${STD}"
        echo -e "${CYAN}║            OLLAMA MANAGEMENT MENU                      ║${STD}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${STD}"
        echo ""
        
        # Check if Ollama is installed
        if command -v ollama &> /dev/null; then
            echo -e "${GREEN}✓ Ollama is installed${STD}"
            
            # Check if Ollama service is running
            if systemctl is-active --quiet ollama 2>/dev/null || pgrep -x ollama &>/dev/null; then
                echo -e "${GREEN}✓ Ollama service is running${STD}"
            else
                echo -e "${YELLOW}⚠ Ollama service is not running${STD}"
            fi
        else
            echo -e "${RED}✗ Ollama is not installed${STD}"
        fi
        
        echo ""
        echo " 1. Install Ollama"
        echo " 2. Start Ollama service"
        echo " 3. Stop Ollama service"
        echo " 4. Restart Ollama service"
        echo " 5. Check Ollama status"
        echo " 6. Update Ollama"
        echo " 7. List installed models"
        echo " 8. Pull/Download a model"
        echo " 9. Remove a model"
        echo "10. Run interactive model"
        echo "11. View Ollama logs"
        echo "12. Configure Ollama settings"
        echo "13. Uninstall Ollama"
        echo " 0. Back to main menu"
        echo ""
        read -r -p "Select option: " ollama_choice
        
        case $ollama_choice in
            1)
                echo -e "${CYAN}Installing Ollama...${STD}"
                if check_internet; then
                    curl -fsSL https://ollama.com/install.sh | sh
                    if [[ $? -eq 0 ]]; then
                        log_success "Ollama installed successfully"
                    else
                        log_error "Ollama installation failed"
                    fi
                fi
                pause
                ;;
            2)
                echo -e "${CYAN}Starting Ollama service...${STD}"
                if systemctl is-active --quiet ollama 2>/dev/null; then
                    echo "Ollama service is already running"
                else
                    # Try systemd first
                    sudo systemctl start ollama 2>/dev/null && \
                        log_success "Ollama service started" || {
                        # If systemd fails, try running directly
                        echo "Starting Ollama directly..."
                        nohup ollama serve &>/dev/null &
                        sleep 2
                        if pgrep -x ollama &>/dev/null; then
                            log_success "Ollama started successfully"
                        else
                            log_error "Failed to start Ollama"
                        fi
                    }
                fi
                pause
                ;;
            3)
                echo -e "${CYAN}Stopping Ollama service...${STD}"
                sudo systemctl stop ollama 2>/dev/null || \
                    pkill -9 ollama
                log_success "Ollama service stopped"
                pause
                ;;
            4)
                echo -e "${CYAN}Restarting Ollama service...${STD}"
                sudo systemctl restart ollama 2>/dev/null || {
                    pkill -9 ollama
                    sleep 1
                    nohup ollama serve &>/dev/null &
                }
                log_success "Ollama service restarted"
                pause
                ;;
            5)
                echo -e "${CYAN}Ollama Status:${STD}"
                echo ""
                ollama --version 2>/dev/null || echo "Ollama not found"
                echo ""
                if systemctl is-active --quiet ollama 2>/dev/null; then
                    echo -e "${GREEN}Service status: Running (systemd)${STD}"
                    systemctl status ollama --no-pager
                elif pgrep -x ollama &>/dev/null; then
                    echo -e "${GREEN}Service status: Running (process)${STD}"
                    ps aux | grep -v grep | grep ollama
                else
                    echo -e "${RED}Service status: Not running${STD}"
                fi
                pause
                ;;
            6)
                echo -e "${CYAN}Updating Ollama...${STD}"
                if check_internet; then
                    curl -fsSL https://ollama.com/install.sh | sh
                    log_success "Ollama updated successfully"
                fi
                pause
                ;;
            7)
                echo -e "${CYAN}Installed Ollama models:${STD}"
                echo ""
                ollama list
                pause
                ;;
            8)
                echo -e "${CYAN}Pull/Download a model${STD}"
                echo ""
                echo "Popular models:"
                echo "  - llama3.2:latest (small, fast)"
                echo "  - llama3.1:latest (medium)"
                echo "  - mistral:latest"
                echo "  - codellama:latest (coding)"
                echo "  - phi3:latest (small)"
                echo ""
                read -r -p "Enter model name (e.g., llama3.2): " model_name
                if [[ -n "$model_name" ]]; then
                    echo "Pulling $model_name..."
                    ollama pull "$model_name"
                    if [[ $? -eq 0 ]]; then
                        log_success "Model $model_name pulled successfully"
                    else
                        log_error "Failed to pull model $model_name"
                    fi
                fi
                pause
                ;;
            9)
                echo -e "${CYAN}Remove a model${STD}"
                echo ""
                ollama list
                echo ""
                read -r -p "Enter model name to remove: " model_name
                if [[ -n "$model_name" ]]; then
                    if confirm_action "Remove model $model_name?"; then
                        ollama rm "$model_name"
                        log_success "Model $model_name removed"
                    fi
                fi
                pause
                ;;
            10)
                echo -e "${CYAN}Run interactive model${STD}"
                echo ""
                ollama list
                echo ""
                read -r -p "Enter model name to run: " model_name
                if [[ -n "$model_name" ]]; then
                    echo "Starting interactive session with $model_name..."
                    echo "Type /bye to exit"
                    echo ""
                    ollama run "$model_name"
                fi
                pause
                ;;
            11)
                echo -e "${CYAN}Ollama logs:${STD}"
                echo ""
                if systemctl is-active --quiet ollama 2>/dev/null; then
                    journalctl -u ollama -n 50 --no-pager
                else
                    echo "Ollama service logs not available (not running via systemd)"
                fi
                pause
                ;;
            12)
                echo -e "${CYAN}Configure Ollama settings${STD}"
                echo ""
                echo "Ollama configuration file: /etc/systemd/system/ollama.service"
                echo ""
                echo "1. Set custom host/port (default: 127.0.0.1:11434)"
                echo "2. Set model storage location"
                echo "3. View current configuration"
                echo "0. Back"
                echo ""
                read -r -p "Select option: " config_choice
                
                case $config_choice in
                    1)
                        read -r -p "Enter host:port (e.g., 0.0.0.0:11434): " host_port
                        echo "Setting OLLAMA_HOST=$host_port"
                        echo "Add this to /etc/systemd/system/ollama.service:"
                        echo "Environment=\"OLLAMA_HOST=$host_port\""
                        ;;
                    2)
                        read -r -p "Enter model storage path: " model_path
                        echo "Setting OLLAMA_MODELS=$model_path"
                        echo "Add this to /etc/systemd/system/ollama.service:"
                        echo "Environment=\"OLLAMA_MODELS=$model_path\""
                        ;;
                    3)
                        if [[ -f /etc/systemd/system/ollama.service ]]; then
                            cat /etc/systemd/system/ollama.service
                        else
                            echo "Configuration file not found"
                        fi
                        ;;
                esac
                pause
                ;;
            13)
                echo -e "${RED}Uninstall Ollama${STD}"
                echo ""
                echo "This will:"
                echo "  - Stop Ollama service"
                echo "  - Remove Ollama binary"
                echo "  - Keep models (in ~/.ollama/models)"
                echo ""
                if confirm_action "Proceed with uninstall?"; then
                    sudo systemctl stop ollama 2>/dev/null
                    sudo systemctl disable ollama 2>/dev/null
                    sudo rm /usr/local/bin/ollama 2>/dev/null
                    sudo rm /etc/systemd/system/ollama.service 2>/dev/null
                    sudo systemctl daemon-reload
                    log_success "Ollama uninstalled"
                    echo ""
                    if confirm_action "Remove models too (~/.ollama)?"; then
                        rm -rf ~/.ollama
                        log_success "Models removed"
                    fi
                fi
                pause
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid option"
                sleep 1
                ;;
        esac
    done
}

dev_ollama_config() {
    echo -e "${CYAN}Ollama AI Setup${STD}"
    echo ""
    
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✓ Ollama is already installed${STD}"
        ollama --version
    else
        echo "Ollama is not installed"
        if confirm_action "Install Ollama now?"; then
            if check_internet; then
                echo "Installing Ollama..."
                curl -fsSL https://ollama.com/install.sh | sh
                log_success "Ollama installed successfully"
            fi
        fi
    fi
    pause
}

dev_ollama_update() {
    echo -e "${CYAN}Updating Ollama...${STD}"
    
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama is not installed"
        pause
        return
    fi
    
    if check_internet; then
        curl -fsSL https://ollama.com/install.sh | sh
        log_success "Ollama updated successfully"
    fi
    pause
}

dev_podman_menu() {
    echo -e "${CYAN}Podman Container Manager${STD}"
    echo ""
    echo "1. Install Podman"
    echo "2. List containers"
    echo "3. List images"
    echo "4. Start container"
    echo "5. Stop container"
    echo "6. Remove container"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " pod_choice
    
    case $pod_choice in
        1)
            $INSTALL_CMD podman
            log_success "Podman installed"
            ;;
        2) podman ps -a ;;
        3) podman images ;;
        4)
            read -r -p "Container name/ID: " cont_name
            podman start "$cont_name"
            ;;
        5)
            read -r -p "Container name/ID: " cont_name
            podman stop "$cont_name"
            ;;
        6)
            read -r -p "Container name/ID: " cont_name
            podman rm "$cont_name"
            ;;
    esac
    pause
}

dev_docker_menu() {
    echo -e "${CYAN}Docker Container Manager${STD}"
    echo ""
    echo "1. Install Docker"
    echo "2. List containers"
    echo "3. List images"
    echo "4. Start container"
    echo "5. Stop container"
    echo "6. Remove container"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " dock_choice
    
    case $dock_choice in
        1)
            if [[ "$PKGMGR" == "apt" ]]; then
                curl -fsSL https://get.docker.com | sh
                sudo usermod -aG docker $USER
                log_success "Docker installed. Log out and back in for group changes."
            else
                $INSTALL_CMD docker
                sudo systemctl enable docker
                sudo systemctl start docker
                log_success "Docker installed"
            fi
            ;;
        2) sudo docker ps -a ;;
        3) sudo docker images ;;
        4)
            read -r -p "Container name/ID: " cont_name
            sudo docker start "$cont_name"
            ;;
        5)
            read -r -p "Container name/ID: " cont_name
            sudo docker stop "$cont_name"
            ;;
        6)
            read -r -p "Container name/ID: " cont_name
            sudo docker rm "$cont_name"
            ;;
    esac
    pause
}

dev_install_go() {
    echo -e "${CYAN}Installing Go (latest version)${STD}"
    
    if check_internet; then
        # Get latest version
        GO_VERSION=$(curl -s https://go.dev/VERSION?m=text | head -n1)
        GO_TAR="${GO_VERSION}.linux-amd64.tar.gz"
        
        echo "Downloading $GO_VERSION..."
        cd /tmp
        wget "https://go.dev/dl/$GO_TAR"
        
        echo "Installing..."
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf "$GO_TAR"
        
        # Add to PATH
        if ! grep -q "/usr/local/go/bin" ~/.bashrc; then
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        fi
        
        log_success "Go installed: $GO_VERSION"
        echo "Run 'source ~/.bashrc' or restart terminal to use go"
    fi
    pause
}

dev_manage_users() {
    echo -e "${CYAN}User Management${STD}"
    echo ""
    echo "1. Add user"
    echo "2. Delete user"
    echo "3. List users"
    echo "4. Add user to group"
    echo "5. Change user password"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " user_choice
    
    case $user_choice in
        1)
            read -r -p "Username: " username
            sudo useradd -m "$username"
            sudo passwd "$username"
            log_success "User $username created"
            ;;
        2)
            read -r -p "Username: " username
            if confirm_action "Delete user $username?"; then
                sudo userdel -r "$username"
                log_success "User $username deleted"
            fi
            ;;
        3)
            cat /etc/passwd | cut -d: -f1
            ;;
        4)
            read -r -p "Username: " username
            read -r -p "Group: " groupname
            sudo usermod -aG "$groupname" "$username"
            log_success "User $username added to $groupname"
            ;;
        5)
            read -r -p "Username: " username
            sudo passwd "$username"
            ;;
    esac
    pause
}

# ── NEW: RUN SETUP.SH SCRIPT ──
run_setup_script() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${STD}"
    echo -e "${CYAN}║              RUN SETUP.SH SCRIPT                       ║${STD}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${STD}"
    echo ""
    
    # Check if setup.sh exists in current directory
    if [[ -f "$SETUP_SCRIPT" ]]; then
        echo -e "${GREEN}✓ Found: $SETUP_SCRIPT${STD}"
        echo ""
        
        # Check if executable
        if [[ -x "$SETUP_SCRIPT" ]]; then
            echo -e "${GREEN}✓ Script is executable${STD}"
        else
            echo -e "${YELLOW}⚠ Script is not executable${STD}"
            if confirm_action "Make it executable?"; then
                chmod +x "$SETUP_SCRIPT"
                log_success "Made setup.sh executable"
            fi
        fi
        
        echo ""
        echo "This will run: $SETUP_SCRIPT"
        echo ""
        
        if confirm_action "Proceed?"; then
            log_msg "Running setup.sh script"
            echo ""
            echo -e "${CYAN}═══════════════════════════════════════════════════${STD}"
            echo -e "${CYAN}          SETUP.SH OUTPUT                           ${STD}"
            echo -e "${CYAN}═══════════════════════════════════════════════════${STD}"
            echo ""
            
            # Run the script
            bash "$SETUP_SCRIPT"
            exit_code=$?
            
            echo ""
            echo -e "${CYAN}═══════════════════════════════════════════════════${STD}"
            
            if [[ $exit_code -eq 0 ]]; then
                log_success "setup.sh completed successfully"
            else
                log_error "setup.sh exited with code $exit_code"
            fi
        else
            echo "Cancelled"
        fi
    else
        echo -e "${RED}✗ setup.sh not found in current directory${STD}"
        echo ""
        echo "Expected location: $SETUP_SCRIPT"
        echo "Current directory: $(pwd)"
        echo ""
        read -r -p "Enter path to setup.sh (or press Enter to skip): " custom_path
        
        if [[ -n "$custom_path" && -f "$custom_path" ]]; then
            SETUP_SCRIPT="$custom_path"
            if confirm_action "Run $SETUP_SCRIPT?"; then
                bash "$SETUP_SCRIPT"
                exit_code=$?
                if [[ $exit_code -eq 0 ]]; then
                    log_success "Setup script completed"
                else
                    log_error "Setup script failed with code $exit_code"
                fi
            fi
        else
            echo "No valid setup.sh found"
        fi
    fi
    
    pause
}

# --- MODULE: HARDWARE & ANDROID ---
hardware_android_menu() {
    echo -e "${CYAN}Android Manager (ADB)${STD}"
    echo ""
    
    if ! command -v adb &> /dev/null; then
        echo "ADB not installed"
        if confirm_action "Install ADB tools?"; then
            $INSTALL_CMD android-tools-adb
        fi
        pause
        return
    fi
    
    echo "1. List connected devices"
    echo "2. Install APK"
    echo "3. Screen mirroring (scrcpy)"
    echo "4. Pull file from device"
    echo "5. Push file to device"
    echo "6. Reboot device"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " adb_choice
    
    case $adb_choice in
        1) adb devices ;;
        2)
            read -r -p "APK path: " apk_path
            adb install "$apk_path"
            ;;
        3)
            if command -v scrcpy &> /dev/null; then
                scrcpy
            else
                echo "scrcpy not installed"
                $INSTALL_CMD scrcpy
            fi
            ;;
        4)
            read -r -p "Remote path: " remote_path
            read -r -p "Local path: " local_path
            adb pull "$remote_path" "$local_path"
            ;;
        5)
            read -r -p "Local path: " local_path
            read -r -p "Remote path: " remote_path
            adb push "$local_path" "$remote_path"
            ;;
        6) adb reboot ;;
    esac
    pause
}

hardware_gpu_monitor() {
    echo -e "${CYAN}GPU Monitor ($GPU_VENDOR)${STD}"
    echo ""
    
    case $GPU_VENDOR in
        Nvidia)
            if command -v nvidia-smi &> /dev/null; then
                watch -n 1 nvidia-smi
            else
                echo "nvidia-smi not found"
            fi
            ;;
        AMD)
            if command -v radeontop &> /dev/null; then
                radeontop
            else
                echo "radeontop not installed"
                $INSTALL_CMD radeontop
            fi
            ;;
        "Intel"*)
            if command -v intel_gpu_top &> /dev/null; then
                sudo intel_gpu_top
            else
                echo "Intel GPU monitoring not available"
            fi
            ;;
        *)
            echo "GPU monitoring not available for: $GPU_VENDOR"
            ;;
    esac
    pause
}

hardware_stress_test() {
    echo -e "${CYAN}System Stress Test${STD}"
    echo ""
    
    if ! command -v stress-ng &> /dev/null; then
        echo "stress-ng not installed"
        if confirm_action "Install stress-ng?"; then
            $INSTALL_CMD stress-ng
        else
            pause
            return
        fi
    fi
    
    echo "1. CPU stress test (10 seconds)"
    echo "2. Memory stress test (10 seconds)"
    echo "3. Disk I/O stress test"
    echo "4. Full system stress test"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " stress_choice
    
    case $stress_choice in
        1) stress-ng --cpu $CPU_CORES --timeout 10s --metrics ;;
        2) stress-ng --vm 2 --vm-bytes 80% --timeout 10s --metrics ;;
        3) stress-ng --hdd 1 --timeout 10s --metrics ;;
        4) stress-ng --cpu $CPU_CORES --vm 2 --hdd 1 --timeout 10s --metrics ;;
    esac
    pause
}

hardware_system_info() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${STD}"
    echo -e "${CYAN}║              SYSTEM INFORMATION                        ║${STD}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${STD}"
    echo ""
    
    echo -e "${YELLOW}OS Information:${STD}"
    uname -a
    echo ""
    
    echo -e "${YELLOW}CPU Information:${STD}"
    lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|Socket"
    echo ""
    
    echo -e "${YELLOW}Memory Information:${STD}"
    free -h
    echo ""
    
    echo -e "${YELLOW}GPU Information:${STD}"
    lspci | grep -i "vga\|3d\|display"
    echo ""
    
    echo -e "${YELLOW}Disk Usage:${STD}"
    df -h | grep -E "^/dev"
    echo ""
    
    echo -e "${YELLOW}Network Interfaces:${STD}"
    ip -br addr
    echo ""
    
    pause
}

hardware_network_tools() {
    echo -e "${CYAN}Network Tools${STD}"
    echo ""
    echo "1. Show IP configuration"
    echo "2. Ping test"
    echo "3. DNS lookup"
    echo "4. Port scan (netstat)"
    echo "5. Network speed test"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " net_choice
    
    case $net_choice in
        1)
            ip addr show
            echo ""
            echo "Gateway:"
            ip route | grep default
            ;;
        2)
            read -r -p "Host to ping: " host
            ping -c 4 "$host"
            ;;
        3)
            read -r -p "Domain to lookup: " domain
            nslookup "$domain"
            ;;
        4)
            netstat -tuln
            ;;
        5)
            if command -v speedtest-cli &> /dev/null; then
                speedtest-cli
            else
                echo "speedtest-cli not installed"
                if confirm_action "Install speedtest-cli?"; then
                    sudo pip3 install speedtest-cli
                    speedtest-cli
                fi
            fi
            ;;
    esac
    pause
}

# --- MODULE: BACKUP & RESTORE ---
backup_manager() {
    echo -e "${CYAN}Backup Manager${STD}"
    echo ""
    echo "1. Backup home directory"
    echo "2. Backup /etc configuration"
    echo "3. Backup package list"
    echo "4. List backups"
    echo "5. Restore backup"
    echo "0. Back"
    echo ""
    read -r -p "Select option: " backup_choice
    
    case $backup_choice in
        1)
            backup_name="home_backup_${TIMESTAMP}.tar.gz"
            echo "Creating home directory backup..."
            tar -czf "$BACKUP_DIR/$backup_name" \
                --exclude="$HOME/.cache" \
                --exclude="$HOME/.local/share/Trash" \
                --exclude="$HOME/Downloads" \
                "$HOME" 2>/dev/null
            log_success "Backup created: $backup_name"
            ;;
        2)
            backup_name="etc_backup_${TIMESTAMP}.tar.gz"
            echo "Creating /etc backup..."
            sudo tar -czf "$BACKUP_DIR/$backup_name" /etc
            log_success "Backup created: $backup_name"
            ;;
        3)
            pkg_list="$BACKUP_DIR/packages_${TIMESTAMP}.txt"
            if [[ "$PKGMGR" == "apt" ]]; then
                dpkg --get-selections > "$pkg_list"
            elif [[ "$PKGMGR" == "dnf" ]]; then
                rpm -qa > "$pkg_list"
            elif [[ "$PKGMGR" == "pacman" ]]; then
                pacman -Qqe > "$pkg_list"
            fi
            log_success "Package list saved: $pkg_list"
            ;;
        4)
            echo "Available backups:"
            ls -lh "$BACKUP_DIR"
            ;;
        5)
            echo "Available backups:"
            ls "$BACKUP_DIR"
            echo ""
            read -r -p "Enter backup filename to restore: " backup_file
            if [[ -f "$BACKUP_DIR/$backup_file" ]]; then
                if confirm_action "Restore $backup_file?"; then
                    tar -xzf "$BACKUP_DIR/$backup_file" -C /
                    log_success "Backup restored"
                fi
            else
                log_error "Backup file not found"
            fi
            ;;
    esac
    pause
}

# --- CLI ARGUMENT HANDLER ---
handle_cli_args() {
    case "$1" in
        --help|-h)
            echo "Grand Unified Toolbox v$SCRIPT_VERSION"
            echo ""
            echo "Usage: toolbox [OPTION]"
            echo ""
            echo "Options:"
            echo "  --help, -h              Show this help"
            echo "  --version, -v           Show version"
            echo "  --update                Update system"
            echo "  --cleanup               Clean system"
            echo "  --install-deps          Install dependencies"
            echo "  --ollama-menu           Open Ollama management menu"
            echo "  --setup                 Run setup.sh script"
            echo "  --gpu-info              Show GPU information"
            echo "  --gpu-monitor           Monitor GPU usage"
            echo "  --stress-test           Run stress test"
            echo "  --android               Android tools menu"
            echo "  --network               Network tools"
            echo "  --system-info           Show system information"
            echo "  --backup-home           Backup home directory"
            echo "  --backup-etc            Backup /etc"
            echo "  --backup-packages       Backup package list"
            echo ""
            exit 0
            ;;
        --version|-v)
            echo "Toolbox v$SCRIPT_VERSION"
            exit 0
            ;;
        --update)
            detect_package_manager
            maintenance_update_system
            exit 0
            ;;
        --cleanup)
            detect_package_manager
            maintenance_cleanup
            exit 0
            ;;
        --install-deps)
            detect_package_manager
            detect_hardware
            install_dependencies
            exit 0
            ;;
        --ollama-menu)
            detect_package_manager
            dev_ollama_management
            exit 0
            ;;
        --setup)
            run_setup_script
            exit 0
            ;;
        --gpu-info)
            detect_hardware
            echo "GPU Vendor: $GPU_VENDOR"
            lspci | grep -i "vga\|3d\|display"
            exit 0
            ;;
        --gpu-monitor)
            detect_package_manager
            detect_hardware
            hardware_gpu_monitor
            exit 0
            ;;
        --stress-test)
            detect_package_manager
            detect_hardware
            hardware_stress_test
            exit 0
            ;;
        --android)
            detect_package_manager
            hardware_android_menu
            exit 0
            ;;
        --network)
            detect_package_manager
            hardware_network_tools
            exit 0
            ;;
        --system-info)
            detect_hardware
            hardware_system_info
            exit 0
            ;;
        --backup-home)
            backup_name="home_backup_${TIMESTAMP}.tar.gz"
            tar -czf "$BACKUP_DIR/$backup_name" \
                --exclude="$HOME/.cache" \
                --exclude="$HOME/.local/share/Trash" \
                "$HOME"
            echo "Backup created: $BACKUP_DIR/$backup_name"
            exit 0
            ;;
        --backup-etc)
            backup_name="etc_backup_${TIMESTAMP}.tar.gz"
            sudo tar -czf "$BACKUP_DIR/$backup_name" /etc && \
                echo "System config backed up: $BACKUP_DIR/$backup_name" || \
                echo "ERROR: Backup failed (root required)" >&2
            exit 0
            ;;
        --backup-packages)
            detect_package_manager
            pkg_list="$BACKUP_DIR/installed_packages_${TIMESTAMP}.txt"
            if [[ "$PKGMGR" == "apt" ]]; then
                dpkg --get-selections > "$pkg_list"
            elif [[ "$PKGMGR" == "dnf" ]]; then
                rpm -qa > "$pkg_list"
            elif [[ "$PKGMGR" == "pacman" ]]; then
                pacman -Qqe > "$pkg_list"
            fi
            echo "Package list saved: $pkg_list"
            exit 0
            ;;
        --no-install)
            # Skip installer, used internally
            ;;
        *)
            if [[ -n "$1" ]]; then
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
            fi
            ;;
    esac
}

# --- INSTALLER ---
run_installer() {
    if [[ "$0" != "$SCRIPT_PATH" && "$1" != "--no-install" ]]; then
        clear
        echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${STD}"
        echo -e "${CYAN}║           Grand Unified Toolbox Installer v${SCRIPT_VERSION}            ║${STD}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${STD}"
        echo ""
        echo "This will:"
        echo "  • Install the toolbox to /usr/local/bin/toolbox"
        echo "  • Install required dependencies"
        echo "  • Make it accessible from anywhere as 'toolbox'"
        echo ""
        
        if confirm_action "Proceed with installation?"; then
            detect_package_manager
            detect_hardware
            
            echo ""
            echo "Installing dependencies..."
            install_dependencies
            
            echo ""
            echo "Installing toolbox script..."
            sudo cp "$0" "$SCRIPT_PATH"
            sudo chmod +x "$SCRIPT_PATH"
            
            log_success "Installation complete!"
            echo ""
            echo -e "${GREEN}You can now run 'toolbox' from anywhere!${STD}"
            echo -e "Run 'toolbox --help' for CLI options"
            exit 0
        else
            echo "Installation cancelled. Running in standalone mode..."
            sleep 2
        fi
    fi
}

# --- MAIN MENU ---
show_main_menu() {
    local lastmessage="Ready"
    
    while true; do
        DrawHeader
        echo ""
        echo -e " ${GREEN}╔═══════════════════════════════╗${STD}  ${RED}╔═══════════════════════════════╗${STD}"
        echo -e " ${GREEN}║     1. MAINTENANCE            ║${STD}  ${RED}║     2. RESCUE & RECOVERY      ║${STD}"
        echo -e " ${GREEN}╚═══════════════════════════════╝${STD}  ${RED}╚═══════════════════════════════╝${STD}"
        printf "  %-33s  %-33s\n" "10. Install Core Tools" "20. Auto-Diagnostic Repair"
        printf "  %-33s  %-33s\n" "11. System Update ($PKGMGR)" "21. Graphics Repair ($GPU_VENDOR)"
        printf "  %-33s  %-33s\n" "12. System Cleanup" "22. Disk Analyzer"
        printf "  %-33s  %-33s\n" "13. Kill Zombie Processes" "23. GRUB Rescue Guide"
        printf "  %-33s  %-33s\n" "14. Service Manager" "24. Boot Repair"
        echo ""
        echo -e " ${CYAN}╔═══════════════════════════════╗${STD}  ${MAGENTA}╔═══════════════════════════════╗${STD}"
        echo -e " ${CYAN}║     3. DEV, AI & CONTAINERS   ║${STD}  ${MAGENTA}║     4. HARDWARE & ANDROID     ║${STD}"
        echo -e " ${CYAN}╚═══════════════════════════════╝${STD}  ${MAGENTA}╚═══════════════════════════════╝${STD}"
        printf "  %-33s  %-33s\n" "30. Ollama AI Setup" "40. Android Manager (ADB)"
        printf "  %-33s  %-33s\n" "31. Podman Manager" "41. GPU Monitor ($GPU_VENDOR)"
        printf "  %-33s  %-33s\n" "32. Install Go (Latest)" "42. Stress Test Suite"
        printf "  %-33s  %-33s\n" "33. User Management" "43. System Information"
        printf "  %-33s  %-33s\n" "34. Docker Manager" "44. Network Tools"
        printf "  %-33s\n" "35. Ollama Management Menu"
        printf "  %-33s\n" "36. Run setup.sh Script"
        echo ""
        echo -e " ${GREEN}╔═══════════════════════════════╗${STD}"
        echo -e " ${GREEN}║     5. BACKUP & RESTORE       ║${STD}"
        echo -e " ${GREEN}╚═══════════════════════════════╝${STD}"
        printf "  %-33s\n" "50. Backup Manager"
        echo ""
        echo -e " ${WHITE}80. Reboot System${STD}  |  ${WHITE}90. View Logs${STD}  |  ${WHITE}99. Exit${STD}"
        echo " ────────────────────────────────────────────────────────────────────────────────────────────────"
        echo -e " ${YELLOW}Status: $lastmessage${STD}"
        echo ""
        read -r -p " → Select option: " choice
        lastmessage="Ready"
        
        case $choice in
            # Maintenance
            10) maintenance_install_tools ;;
            11) maintenance_update_system ;;
            12) maintenance_cleanup ;;
            13) maintenance_kill_zombies ;;
            14) maintenance_service_manager ;;
            
            # Rescue
            20) rescue_auto_diagnostic ;;
            21) rescue_graphics_menu ;;
            22) rescue_disk_analyzer ;;
            23) rescue_grub_cheatsheet ;;
            24) rescue_boot_repair ;;
            
            # Dev & AI
            30) dev_ollama_config ;;
            31) dev_podman_menu ;;
            32) dev_install_go ;;
            33) dev_manage_users ;;
            34) dev_docker_menu ;;
            35) dev_ollama_management ;;
            36) run_setup_script ;;
            
            # Hardware
            40) hardware_android_menu ;;
            41) hardware_gpu_monitor ;;
            42) hardware_stress_test ;;
            43) hardware_system_info ;;
            44) hardware_network_tools ;;
            
            # Backup
            50) backup_manager ;;
            
            # System
            80)
                if confirm_action "Reboot system now?"; then
                    log_msg "System reboot initiated by user"
                    sudo reboot
                fi
                ;;
            90)
                echo -e "${CYAN}Recent logs:${STD}"
                tail -n 50 "$LOG_DIR/toolbox_${TIMESTAMP}.log" 2>/dev/null || echo "No logs available"
                pause
                ;;
            99)
                echo -e "${GREEN}Thanks for using Toolbox v${SCRIPT_VERSION}!${STD}"
                log_msg "Toolbox session ended"
                exit 0
                ;;
            *)
                lastmessage="Invalid option: $choice"
                ;;
        esac
    done
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Handle command line arguments first
handle_cli_args "$@"

# Run installer if needed
run_installer "$@"

# Initialize
detect_package_manager
detect_hardware

# Resize terminal
printf '\033[8;50;120t'

# Show main menu
show_main_menu
