#!/bin/bash

# ==========================================================
# 🤖 OLLAMA MANAGER v1.0
# Complete Ollama Management Control Menu
# ==========================================================

set -o pipefail  # Exit on pipe failures

# --- GLOBAL CONFIGURATION ---
SCRIPT_VERSION="1.0"
SCRIPT_PATH="/usr/local/bin/ollama-manager"
LOG_DIR="$HOME/.ollama-manager/logs"
BACKUP_DIR="$HOME/.ollama-manager/backups"
CONFIG_FILE="$HOME/.ollama-manager/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directories
mkdir -p "$LOG_DIR" "$BACKUP_DIR" "$HOME/.ollama-manager"

# Colors
RED='\033[1;31m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'
BLUE='\033[1;34m'; MAGENTA='\033[1;35m'; CYAN='\033[1;36m'
WHITE='\033[1;37m'; STD='\033[0m'; BOLD='\033[1m'

# Ollama defaults
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
OLLAMA_MODELS_DIR="${OLLAMA_MODELS:-$HOME/.ollama/models}"

# --- LOGGING FUNCTIONS ---
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_DIR/ollama_${TIMESTAMP}.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_DIR/ollama_${TIMESTAMP}.log"
    echo -e "${RED}ERROR: $1${STD}" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "$LOG_DIR/ollama_${TIMESTAMP}.log"
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

check_ollama_installed() {
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama is not installed"
        return 1
    fi
    return 0
}

check_ollama_running() {
    if ! pgrep -x ollama > /dev/null; then
        log_error "Ollama service is not running"
        return 1
    fi
    return 0
}

get_ollama_version() {
    if check_ollama_installed; then
        ollama --version 2>/dev/null | head -n1 || echo "Unknown"
    else
        echo "Not Installed"
    fi
}

# --- PACKAGE MANAGER DETECTION ---
detect_package_manager() {
    if command -v apt &> /dev/null; then
        PKGMGR="apt"
        INSTALL_CMD="sudo apt install -y"
        UPDATE_CMD="sudo apt update"
    elif command -v dnf &> /dev/null; then
        PKGMGR="dnf"
        INSTALL_CMD="sudo dnf install -y"
        UPDATE_CMD="sudo dnf check-update"
    elif command -v pacman &> /dev/null; then
        PKGMGR="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
        UPDATE_CMD="sudo pacman -Sy"
    else
        log_error "Unsupported package manager"
        exit 1
    fi
    log_msg "Detected package manager: $PKGMGR"
}

# --- HEADER DISPLAY ---
DrawHeader() {
    clear
    local ollama_status="Not Running"
    local ollama_version=$(get_ollama_version)
    
    if check_ollama_running 2>/dev/null; then
        ollama_status="${GREEN}Running${STD}"
    else
        ollama_status="${RED}Stopped${STD}"
    fi
    
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════════════════════════╗${STD}"
    echo -e "${CYAN}║${STD}                              ${BOLD}🤖 OLLAMA MANAGER v${SCRIPT_VERSION}${STD}                                        ${CYAN}║${STD}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════════════════════════╝${STD}"
    printf "${BLUE}║${STD} ${YELLOW}%-15s${STD}: %-25s ${YELLOW}%-15s${STD}: %-28s ${BLUE}║${STD}\n" \
        "Ollama Status" "$ollama_status" "Version" "$ollama_version"
    printf "${BLUE}║${STD} ${YELLOW}%-15s${STD}: %-25s ${YELLOW}%-15s${STD}: %-28s ${BLUE}║${STD}\n" \
        "API Endpoint" "$OLLAMA_HOST" "Models Dir" "$OLLAMA_MODELS_DIR"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════════════════╝${STD}"
}

# =============================================================================
# MODULE: INSTALLATION & SETUP
# =============================================================================

install_ollama() {
    echo -e "${CYAN}--- Installing Ollama ---${STD}"
    
    if check_ollama_installed; then
        log_error "Ollama is already installed"
        echo -e "${YELLOW}Current version: $(get_ollama_version)${STD}"
        if confirm_action "Reinstall Ollama?"; then
            log_msg "User confirmed reinstallation"
        else
            return
        fi
    fi
    
    if ! check_internet; then
        return 1
    fi
    
    echo "Downloading and installing Ollama..."
    log_msg "Starting Ollama installation"
    
    if curl -fsSL https://ollama.com/install.sh | sh; then
        log_success "Ollama installed successfully"
        
        # Start service
        if command -v systemctl &> /dev/null; then
            sudo systemctl enable ollama
            sudo systemctl start ollama
            log_success "Ollama service enabled and started"
        fi
        
        echo ""
        echo -e "${GREEN}Ollama has been installed!${STD}"
        echo "You can now pull and run models."
    else
        log_error "Failed to install Ollama"
    fi
    
    pause
}

uninstall_ollama() {
    echo -e "${RED}--- Uninstall Ollama ---${STD}"
    
    if ! check_ollama_installed; then
        log_error "Ollama is not installed"
        pause
        return
    fi
    
    echo -e "${RED}WARNING: This will remove Ollama and all its data!${STD}"
    if ! confirm_action "Are you sure you want to uninstall Ollama?"; then
        return
    fi
    
    log_msg "Starting Ollama uninstallation"
    
    # Stop service
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop ollama 2>/dev/null
        sudo systemctl disable ollama 2>/dev/null
    fi
    
    # Remove binary
    sudo rm -f /usr/local/bin/ollama
    sudo rm -f /usr/bin/ollama
    
    # Remove service file
    sudo rm -f /etc/systemd/system/ollama.service
    sudo systemctl daemon-reload 2>/dev/null
    
    # Ask about data
    if confirm_action "Also remove all models and data (~/.ollama)?"; then
        rm -rf ~/.ollama
        log_msg "Removed Ollama data directory"
    fi
    
    log_success "Ollama uninstalled"
    pause
}

update_ollama() {
    echo -e "${CYAN}--- Update Ollama ---${STD}"
    
    if ! check_ollama_installed; then
        log_error "Ollama is not installed"
        pause
        return
    fi
    
    if ! check_internet; then
        pause
        return 1
    fi
    
    local current_version=$(get_ollama_version)
    echo "Current version: $current_version"
    echo ""
    
    if ! confirm_action "Update Ollama to the latest version?"; then
        return
    fi
    
    log_msg "Updating Ollama"
    
    # Stop service
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop ollama
    else
        pkill ollama
    fi
    
    # Update
    if curl -fsSL https://ollama.com/install.sh | sh; then
        log_success "Ollama updated successfully"
        
        # Restart service
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
        fi
        
        echo ""
        echo "New version: $(get_ollama_version)"
    else
        log_error "Failed to update Ollama"
    fi
    
    pause
}

# =============================================================================
# MODULE: SERVICE MANAGEMENT
# =============================================================================

service_control() {
    echo -e "${CYAN}--- Ollama Service Control ---${STD}"
    
    if ! command -v systemctl &> /dev/null; then
        echo -e "${YELLOW}systemd not available. Manual control only.${STD}"
        pause
        return
    fi
    
    while true; do
        clear
        echo -e "${CYAN}=== Ollama Service Control ===${STD}"
        echo ""
        
        # Show current status
        echo -e "${BOLD}Current Status:${STD}"
        systemctl status ollama --no-pager 2>/dev/null | head -n 10
        echo ""
        
        echo " 1. Start Ollama Service"
        echo " 2. Stop Ollama Service"
        echo " 3. Restart Ollama Service"
        echo " 4. Enable Auto-start (on boot)"
        echo " 5. Disable Auto-start"
        echo " 6. View Service Logs"
        echo " 7. Back to Main Menu"
        echo ""
        read -r -p " → Select option: " choice
        
        case $choice in
            1)
                sudo systemctl start ollama
                log_msg "Started Ollama service"
                log_success "Service started"
                sleep 2
                ;;
            2)
                sudo systemctl stop ollama
                log_msg "Stopped Ollama service"
                log_success "Service stopped"
                sleep 2
                ;;
            3)
                sudo systemctl restart ollama
                log_msg "Restarted Ollama service"
                log_success "Service restarted"
                sleep 2
                ;;
            4)
                sudo systemctl enable ollama
                log_msg "Enabled Ollama auto-start"
                log_success "Auto-start enabled"
                sleep 2
                ;;
            5)
                sudo systemctl disable ollama
                log_msg "Disabled Ollama auto-start"
                log_success "Auto-start disabled"
                sleep 2
                ;;
            6)
                clear
                echo -e "${CYAN}=== Ollama Service Logs ===${STD}"
                sudo journalctl -u ollama -n 50 --no-pager
                pause
                ;;
            7)
                return
                ;;
            *)
                echo "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# =============================================================================
# MODULE: MODEL MANAGEMENT
# =============================================================================

model_list() {
    echo -e "${CYAN}--- Installed Models ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    if ! check_ollama_running; then
        echo -e "${YELLOW}Ollama service is not running. Starting it...${STD}"
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
            sleep 2
        fi
    fi
    
    echo ""
    ollama list
    echo ""
    
    pause
}

model_pull() {
    echo -e "${CYAN}--- Pull Model from Library ---${STD}"
    
    if ! check_ollama_installed || ! check_internet; then
        pause
        return
    fi
    
    if ! check_ollama_running; then
        echo -e "${YELLOW}Ollama service is not running. Starting it...${STD}"
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
            sleep 2
        fi
    fi
    
    echo ""
    echo "Popular models:"
    echo "  • llama3.3:latest (70B)"
    echo "  • llama3.2:latest (3B)"
    echo "  • llama3.2:1b"
    echo "  • qwen2.5:latest (7B)"
    echo "  • mistral:latest (7B)"
    echo "  • phi4:latest (14B)"
    echo "  • deepseek-r1:latest (70B)"
    echo "  • codellama:latest"
    echo "  • gemma2:latest"
    echo ""
    echo "Browse all at: https://ollama.com/library"
    echo ""
    
    read -r -p "Enter model name (e.g., llama3.2:latest): " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    log_msg "Pulling model: $model_name"
    echo ""
    
    if ollama pull "$model_name"; then
        log_success "Model $model_name pulled successfully"
    else
        log_error "Failed to pull model $model_name"
    fi
    
    pause
}

model_remove() {
    echo -e "${CYAN}--- Remove Model ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter model name to remove: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    if ! confirm_action "Remove model $model_name?"; then
        return
    fi
    
    log_msg "Removing model: $model_name"
    
    if ollama rm "$model_name"; then
        log_success "Model $model_name removed"
    else
        log_error "Failed to remove model $model_name"
    fi
    
    pause
}

model_copy() {
    echo -e "${CYAN}--- Copy/Rename Model ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter source model name: " source_model
    read -r -p "Enter destination model name: " dest_model
    
    if [[ -z "$source_model" ]] || [[ -z "$dest_model" ]]; then
        echo "Both source and destination required"
        pause
        return
    fi
    
    log_msg "Copying model: $source_model -> $dest_model"
    
    if ollama cp "$source_model" "$dest_model"; then
        log_success "Model copied: $source_model -> $dest_model"
    else
        log_error "Failed to copy model"
    fi
    
    pause
}

model_show() {
    echo -e "${CYAN}--- Show Model Information ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter model name: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    echo ""
    ollama show "$model_name"
    echo ""
    
    pause
}

# =============================================================================
# MODULE: INTERACTIVE SESSIONS
# =============================================================================

run_interactive() {
    echo -e "${CYAN}--- Run Interactive Chat ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    if ! check_ollama_running; then
        echo -e "${YELLOW}Ollama service is not running. Starting it...${STD}"
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
            sleep 2
        fi
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter model name to run: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    log_msg "Starting interactive session with: $model_name"
    echo ""
    echo -e "${GREEN}Starting chat with $model_name...${STD}"
    echo -e "${YELLOW}Type /bye to exit${STD}"
    echo ""
    
    ollama run "$model_name"
    
    log_msg "Interactive session ended"
}

run_prompt() {
    echo -e "${CYAN}--- Run Single Prompt ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    if ! check_ollama_running; then
        echo -e "${YELLOW}Ollama service is not running. Starting it...${STD}"
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
            sleep 2
        fi
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter model name: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    echo ""
    read -r -p "Enter your prompt: " prompt_text
    
    if [[ -z "$prompt_text" ]]; then
        echo "No prompt specified"
        pause
        return
    fi
    
    log_msg "Running prompt on $model_name"
    echo ""
    
    ollama run "$model_name" "$prompt_text"
    
    echo ""
    pause
}

# =============================================================================
# MODULE: MODELFILE OPERATIONS
# =============================================================================

create_custom_model() {
    echo -e "${CYAN}--- Create Custom Model from Modelfile ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    echo ""
    echo "This will create a custom model from a Modelfile"
    echo ""
    
    read -r -p "Enter path to Modelfile: " modelfile_path
    
    if [[ ! -f "$modelfile_path" ]]; then
        log_error "Modelfile not found: $modelfile_path"
        pause
        return
    fi
    
    read -r -p "Enter name for new model: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model name specified"
        pause
        return
    fi
    
    log_msg "Creating custom model: $model_name from $modelfile_path"
    echo ""
    
    if ollama create "$model_name" -f "$modelfile_path"; then
        log_success "Custom model $model_name created"
    else
        log_error "Failed to create custom model"
    fi
    
    pause
}

# =============================================================================
# MODULE: SYSTEM INFORMATION
# =============================================================================

show_system_info() {
    echo -e "${CYAN}--- Ollama System Information ---${STD}"
    
    echo ""
    echo -e "${BOLD}Installation Status:${STD}"
    if check_ollama_installed; then
        echo -e "  Ollama Binary: ${GREEN}Installed${STD}"
        echo "  Version: $(get_ollama_version)"
        echo "  Binary Path: $(which ollama)"
    else
        echo -e "  Ollama Binary: ${RED}Not Installed${STD}"
    fi
    
    echo ""
    echo -e "${BOLD}Service Status:${STD}"
    if command -v systemctl &> /dev/null; then
        systemctl status ollama --no-pager 2>/dev/null | head -n 5
    else
        if pgrep -x ollama > /dev/null; then
            echo -e "  Status: ${GREEN}Running${STD}"
            echo "  PID: $(pgrep -x ollama)"
        else
            echo -e "  Status: ${RED}Not Running${STD}"
        fi
    fi
    
    echo ""
    echo -e "${BOLD}Configuration:${STD}"
    echo "  OLLAMA_HOST: $OLLAMA_HOST"
    echo "  Models Directory: $OLLAMA_MODELS_DIR"
    
    if [[ -d "$OLLAMA_MODELS_DIR" ]]; then
        local disk_usage=$(du -sh "$OLLAMA_MODELS_DIR" 2>/dev/null | cut -f1)
        echo "  Disk Usage: $disk_usage"
    fi
    
    echo ""
    echo -e "${BOLD}Network:${STD}"
    if check_ollama_running 2>/dev/null; then
        if curl -s "$OLLAMA_HOST/api/tags" &> /dev/null; then
            echo -e "  API Endpoint: ${GREEN}Accessible${STD}"
        else
            echo -e "  API Endpoint: ${YELLOW}Not Accessible${STD}"
        fi
    else
        echo -e "  API Endpoint: ${RED}Service Not Running${STD}"
    fi
    
    echo ""
    echo -e "${BOLD}Installed Models:${STD}"
    if check_ollama_running 2>/dev/null; then
        ollama list 2>/dev/null || echo "  Unable to list models"
    else
        echo "  Service not running"
    fi
    
    echo ""
    pause
}

# =============================================================================
# MODULE: CONFIGURATION
# =============================================================================

configure_ollama() {
    while true; do
        clear
        echo -e "${CYAN}=== Ollama Configuration ===${STD}"
        echo ""
        echo "Current Settings:"
        echo "  OLLAMA_HOST: $OLLAMA_HOST"
        echo "  Models Dir: $OLLAMA_MODELS_DIR"
        echo ""
        echo " 1. Change API Host/Port"
        echo " 2. Change Models Directory"
        echo " 3. Set Environment Variables"
        echo " 4. View Current Config"
        echo " 5. Reset to Defaults"
        echo " 6. Back to Main Menu"
        echo ""
        read -r -p " → Select option: " choice
        
        case $choice in
            1)
                echo ""
                read -r -p "Enter new OLLAMA_HOST (current: $OLLAMA_HOST): " new_host
                if [[ -n "$new_host" ]]; then
                    export OLLAMA_HOST="$new_host"
                    echo "OLLAMA_HOST=$new_host" >> "$CONFIG_FILE"
                    log_success "OLLAMA_HOST updated to $new_host"
                fi
                pause
                ;;
            2)
                echo ""
                read -r -p "Enter new models directory (current: $OLLAMA_MODELS_DIR): " new_dir
                if [[ -n "$new_dir" ]]; then
                    mkdir -p "$new_dir"
                    export OLLAMA_MODELS="$new_dir"
                    OLLAMA_MODELS_DIR="$new_dir"
                    echo "OLLAMA_MODELS=$new_dir" >> "$CONFIG_FILE"
                    log_success "Models directory updated to $new_dir"
                fi
                pause
                ;;
            3)
                clear
                echo -e "${CYAN}=== Environment Variables ===${STD}"
                echo ""
                echo "Common Ollama environment variables:"
                echo "  OLLAMA_HOST - API endpoint (default: http://127.0.0.1:11434)"
                echo "  OLLAMA_MODELS - Models storage path"
                echo "  OLLAMA_NUM_PARALLEL - Number of parallel requests"
                echo "  OLLAMA_MAX_LOADED_MODELS - Max models in memory"
                echo "  OLLAMA_KEEP_ALIVE - Model keep-alive duration"
                echo ""
                pause
                ;;
            4)
                clear
                echo -e "${CYAN}=== Current Configuration ===${STD}"
                echo ""
                env | grep OLLAMA || echo "No OLLAMA variables set"
                echo ""
                if [[ -f "$CONFIG_FILE" ]]; then
                    echo "Config file contents:"
                    cat "$CONFIG_FILE"
                fi
                pause
                ;;
            5)
                if confirm_action "Reset all configuration to defaults?"; then
                    export OLLAMA_HOST="http://127.0.0.1:11434"
                    export OLLAMA_MODELS="$HOME/.ollama/models"
                    OLLAMA_MODELS_DIR="$HOME/.ollama/models"
                    rm -f "$CONFIG_FILE"
                    log_success "Configuration reset to defaults"
                fi
                pause
                ;;
            6)
                return
                ;;
            *)
                echo "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# =============================================================================
# MODULE: BACKUP & RESTORE
# =============================================================================

backup_models() {
    echo -e "${CYAN}--- Backup Ollama Models ---${STD}"
    
    if [[ ! -d "$OLLAMA_MODELS_DIR" ]]; then
        log_error "Models directory not found: $OLLAMA_MODELS_DIR"
        pause
        return
    fi
    
    local backup_name="ollama_models_${TIMESTAMP}.tar.gz"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    echo ""
    echo "Backing up models from: $OLLAMA_MODELS_DIR"
    echo "Backup will be saved to: $backup_path"
    echo ""
    
    if ! confirm_action "Proceed with backup?"; then
        return
    fi
    
    log_msg "Creating backup: $backup_name"
    
    if tar -czf "$backup_path" -C "$(dirname "$OLLAMA_MODELS_DIR")" "$(basename "$OLLAMA_MODELS_DIR")"; then
        local size=$(du -h "$backup_path" | cut -f1)
        log_success "Backup created successfully"
        echo ""
        echo "Backup file: $backup_path"
        echo "Size: $size"
    else
        log_error "Backup failed"
    fi
    
    pause
}

restore_models() {
    echo -e "${CYAN}--- Restore Ollama Models ---${STD}"
    
    if [[ ! -d "$BACKUP_DIR" ]] || [[ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]]; then
        log_error "No backups found in $BACKUP_DIR"
        pause
        return
    fi
    
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "No backup files found"
    echo ""
    
    read -r -p "Enter backup filename to restore: " backup_file
    
    if [[ ! -f "$BACKUP_DIR/$backup_file" ]]; then
        log_error "Backup file not found"
        pause
        return
    fi
    
    echo ""
    echo -e "${RED}WARNING: This will replace current models!${STD}"
    if ! confirm_action "Proceed with restore?"; then
        return
    fi
    
    log_msg "Restoring from backup: $backup_file"
    
    # Stop Ollama service
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop ollama
    fi
    
    # Backup current models
    if [[ -d "$OLLAMA_MODELS_DIR" ]]; then
        mv "$OLLAMA_MODELS_DIR" "${OLLAMA_MODELS_DIR}.old.${TIMESTAMP}"
    fi
    
    # Restore
    if tar -xzf "$BACKUP_DIR/$backup_file" -C "$(dirname "$OLLAMA_MODELS_DIR")"; then
        log_success "Models restored successfully"
        
        # Restart service
        if command -v systemctl &> /dev/null; then
            sudo systemctl start ollama
        fi
    else
        log_error "Restore failed"
        
        # Restore old directory if restore failed
        if [[ -d "${OLLAMA_MODELS_DIR}.old.${TIMESTAMP}" ]]; then
            mv "${OLLAMA_MODELS_DIR}.old.${TIMESTAMP}" "$OLLAMA_MODELS_DIR"
        fi
    fi
    
    pause
}

# =============================================================================
# MODULE: ADVANCED OPERATIONS
# =============================================================================

cleanup_unused() {
    echo -e "${CYAN}--- Cleanup Unused Data ---${STD}"
    
    if ! check_ollama_installed; then
        pause
        return
    fi
    
    echo ""
    echo "This will remove:"
    echo "  • Temporary files"
    echo "  • Cache files"
    echo "  • Orphaned model data"
    echo ""
    
    if ! confirm_action "Proceed with cleanup?"; then
        return
    fi
    
    log_msg "Starting cleanup"
    
    # Clean cache
    if [[ -d "$HOME/.ollama/cache" ]]; then
        rm -rf "$HOME/.ollama/cache"/*
        log_success "Cache cleaned"
    fi
    
    # Clean temporary files
    if [[ -d "/tmp/ollama" ]]; then
        rm -rf /tmp/ollama/*
        log_success "Temporary files cleaned"
    fi
    
    echo ""
    log_success "Cleanup completed"
    pause
}

benchmark_model() {
    echo -e "${CYAN}--- Benchmark Model Performance ---${STD}"
    
    if ! check_ollama_installed || ! check_ollama_running; then
        pause
        return
    fi
    
    echo ""
    echo "Installed models:"
    ollama list
    echo ""
    
    read -r -p "Enter model name to benchmark: " model_name
    
    if [[ -z "$model_name" ]]; then
        echo "No model specified"
        pause
        return
    fi
    
    echo ""
    echo "Running benchmark on $model_name..."
    echo "Testing prompt: 'Write a short poem about technology'"
    echo ""
    
    log_msg "Starting benchmark for $model_name"
    local start_time=$(date +%s)
    
    ollama run "$model_name" "Write a short poem about technology"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    echo -e "${GREEN}Benchmark completed in ${duration} seconds${STD}"
    log_msg "Benchmark completed: $model_name took ${duration}s"
    
    pause
}

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

show_help() {
    cat << EOF
${CYAN}Ollama Manager v${SCRIPT_VERSION}${STD}

Usage: $(basename "$0") [OPTION]

Installation & Setup:
  --install           Install Ollama
  --uninstall         Uninstall Ollama
  --update            Update Ollama to latest version

Service Management:
  --start             Start Ollama service
  --stop              Stop Ollama service
  --restart           Restart Ollama service
  --status            Show service status

Model Management:
  --list              List installed models
  --pull <model>      Pull a model from library
  --remove <model>    Remove a model
  --show <model>      Show model information

Interactive:
  --run <model>       Run interactive chat with model
  --chat <model>      Alias for --run

Information:
  --info              Show system information
  --version           Show Ollama version
  --help              Show this help message

Examples:
  $(basename "$0") --install
  $(basename "$0") --pull llama3.2:latest
  $(basename "$0") --run llama3.2:latest
  $(basename "$0") --list

EOF
}

handle_cli_args() {
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --version|-v)
            echo "Ollama Manager v${SCRIPT_VERSION}"
            echo "Ollama Version: $(get_ollama_version)"
            exit 0
            ;;
        --install)
            detect_package_manager
            install_ollama
            exit 0
            ;;
        --uninstall)
            uninstall_ollama
            exit 0
            ;;
        --update)
            update_ollama
            exit 0
            ;;
        --start)
            if command -v systemctl &> /dev/null; then
                sudo systemctl start ollama
                echo "Ollama service started"
            else
                echo "systemctl not available"
                exit 1
            fi
            exit 0
            ;;
        --stop)
            if command -v systemctl &> /dev/null; then
                sudo systemctl stop ollama
                echo "Ollama service stopped"
            else
                echo "systemctl not available"
                exit 1
            fi
            exit 0
            ;;
        --restart)
            if command -v systemctl &> /dev/null; then
                sudo systemctl restart ollama
                echo "Ollama service restarted"
            else
                echo "systemctl not available"
                exit 1
            fi
            exit 0
            ;;
        --status)
            if command -v systemctl &> /dev/null; then
                systemctl status ollama --no-pager
            else
                if pgrep -x ollama > /dev/null; then
                    echo "Ollama is running (PID: $(pgrep -x ollama))"
                else
                    echo "Ollama is not running"
                fi
            fi
            exit 0
            ;;
        --list)
            ollama list
            exit 0
            ;;
        --pull)
            if [[ -z "$2" ]]; then
                echo "Error: Model name required"
                echo "Usage: $0 --pull <model_name>"
                exit 1
            fi
            ollama pull "$2"
            exit 0
            ;;
        --remove)
            if [[ -z "$2" ]]; then
                echo "Error: Model name required"
                echo "Usage: $0 --remove <model_name>"
                exit 1
            fi
            ollama rm "$2"
            exit 0
            ;;
        --show)
            if [[ -z "$2" ]]; then
                echo "Error: Model name required"
                echo "Usage: $0 --show <model_name>"
                exit 1
            fi
            ollama show "$2"
            exit 0
            ;;
        --run|--chat)
            if [[ -z "$2" ]]; then
                echo "Error: Model name required"
                echo "Usage: $0 --run <model_name>"
                exit 1
            fi
            ollama run "$2"
            exit 0
            ;;
        --info)
            show_system_info
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

# =============================================================================
# INSTALLER
# =============================================================================

run_installer() {
    if [[ "$0" != "$SCRIPT_PATH" && "$1" != "--no-install" ]]; then
        clear
        echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${STD}"
        echo -e "${CYAN}║           Ollama Manager Installer v${SCRIPT_VERSION}                   ║${STD}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${STD}"
        echo ""
        echo "This will:"
        echo "  • Install the manager to /usr/local/bin/ollama-manager"
        echo "  • Make it accessible from anywhere as 'ollama-manager'"
        echo "  • Optionally install Ollama if not already installed"
        echo ""
        
        if confirm_action "Proceed with installation?"; then
            detect_package_manager
            
            echo ""
            echo "Installing manager script..."
            sudo cp "$0" "$SCRIPT_PATH"
            sudo chmod +x "$SCRIPT_PATH"
            
            log_success "Manager installed successfully!"
            echo ""
            
            if ! check_ollama_installed; then
                if confirm_action "Ollama is not installed. Install it now?"; then
                    install_ollama
                fi
            fi
            
            echo ""
            echo -e "${GREEN}You can now run 'ollama-manager' from anywhere!${STD}"
            echo -e "Run 'ollama-manager --help' for CLI options"
            exit 0
        else
            echo "Installation cancelled. Running in standalone mode..."
            sleep 2
        fi
    fi
}

# =============================================================================
# MAIN MENU
# =============================================================================

show_main_menu() {
    local lastmessage="Ready"
    
    while true; do
        DrawHeader
        echo ""
        echo -e " ${GREEN}╔═══════════════════════════════╗${STD}  ${BLUE}╔═══════════════════════════════╗${STD}"
        echo -e " ${GREEN}║     1. INSTALLATION           ║${STD}  ${BLUE}║     2. MODEL MANAGEMENT       ║${STD}"
        echo -e " ${GREEN}╚═══════════════════════════════╝${STD}  ${BLUE}╚═══════════════════════════════╝${STD}"
        printf "  %-33s  %-33s\n" "10. Install Ollama" "20. List Models"
        printf "  %-33s  %-33s\n" "11. Update Ollama" "21. Pull Model"
        printf "  %-33s  %-33s\n" "12. Uninstall Ollama" "22. Remove Model"
        printf "  %-33s  %-33s\n" "13. Service Control" "23. Copy/Rename Model"
        printf "  %-33s  %-33s\n" "" "24. Show Model Info"
        echo ""
        echo -e " ${CYAN}╔═══════════════════════════════╗${STD}  ${MAGENTA}╔═══════════════════════════════╗${STD}"
        echo -e " ${CYAN}║     3. INTERACTIVE            ║${STD}  ${MAGENTA}║     4. ADVANCED               ║${STD}"
        echo -e " ${CYAN}╚═══════════════════════════════╝${STD}  ${MAGENTA}╚═══════════════════════════════╝${STD}"
        printf "  %-33s  %-33s\n" "30. Run Interactive Chat" "40. Create Custom Model"
        printf "  %-33s  %-33s\n" "31. Run Single Prompt" "41. Configuration"
        printf "  %-33s  %-33s\n" "" "42. Backup Models"
        printf "  %-33s  %-33s\n" "" "43. Restore Models"
        printf "  %-33s  %-33s\n" "" "44. Cleanup Unused Data"
        printf "  %-33s  %-33s\n" "" "45. Benchmark Model"
        echo ""
        echo -e " ${YELLOW}╔═══════════════════════════════╗${STD}"
        echo -e " ${YELLOW}║     5. SYSTEM                 ║${STD}"
        echo -e " ${YELLOW}╚═══════════════════════════════╝${STD}"
        printf "  %-33s\n" "50. System Information"
        printf "  %-33s\n" "51. View Logs"
        echo ""
        echo -e " ${WHITE}99. Exit${STD}"
        echo " ────────────────────────────────────────────────────────────────────────────────────────────────"
        echo -e " ${YELLOW}Status: $lastmessage${STD}"
        echo ""
        read -r -p " → Select option: " choice
        lastmessage="Ready"
        
        case $choice in
            # Installation
            10) install_ollama ;;
            11) update_ollama ;;
            12) uninstall_ollama ;;
            13) service_control ;;
            
            # Model Management
            20) model_list ;;
            21) model_pull ;;
            22) model_remove ;;
            23) model_copy ;;
            24) model_show ;;
            
            # Interactive
            30) run_interactive ;;
            31) run_prompt ;;
            
            # Advanced
            40) create_custom_model ;;
            41) configure_ollama ;;
            42) backup_models ;;
            43) restore_models ;;
            44) cleanup_unused ;;
            45) benchmark_model ;;
            
            # System
            50) show_system_info ;;
            51)
                echo -e "${CYAN}Recent logs:${STD}"
                tail -n 50 "$LOG_DIR/ollama_${TIMESTAMP}.log" 2>/dev/null || echo "No logs available"
                pause
                ;;
            
            # Exit
            99)
                echo -e "${GREEN}Thanks for using Ollama Manager v${SCRIPT_VERSION}!${STD}"
                log_msg "Ollama Manager session ended"
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

# Resize terminal
printf '\033[8;50;120t'

# Show main menu
show_main_menu
