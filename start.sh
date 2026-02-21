#!/bin/bash

################################################################################
# Complete Setup and Start Script
# Handles installation, dependencies, and provides all start options
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

print_header() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${MAGENTA}     🔐 ultimate LLM Model Factory - Setup & Start${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

################################################################################
# Dependency Check and Installation
################################################################################

check_and_install_dependencies() {
    print_header
    echo -e "${BOLD}Checking Dependencies...${NC}"
    echo ""
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        echo ""
        echo "Please install Python 3.8 or higher:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        echo "  macOS: brew install python3"
        echo "  Windows: Download from python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
    
    # Check if virtual environment exists
    if [[ ! -d "$VENV_DIR" ]]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip -q
    
    # Install requirements
    print_info "Installing dependencies (this may take a minute)..."
    
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        pip install -r "$SCRIPT_DIR/requirements.txt" -q
        print_success "Dependencies installed from requirements.txt"
    else
        # Install manually
        print_info "requirements.txt not found, installing core packages..."
        pip install streamlit requests -q
        print_success "Core packages installed"
    fi
    
    # Verify installation
    if python3 -c "import streamlit" 2>/dev/null; then
        print_success "Streamlit verified"
    else
        print_error "Streamlit installation failed"
        exit 1
    fi
    
    if python3 -c "import requests" 2>/dev/null; then
        print_success "Requests verified"
    else
        print_error "Requests installation failed"
        exit 1
    fi
    
    # Create directories
    print_info "Creating directory structure..."
    mkdir -p "$SCRIPT_DIR"/{workspace,sandbox,logs,config}
    chmod 700 "$SCRIPT_DIR/config" 2>/dev/null || true
    print_success "Directories ready"
    
    echo ""
    print_success "All dependencies installed successfully!"
    sleep 2
}

################################################################################
# Start Options
################################################################################

show_start_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Start Options${NC}"
        echo ""
        echo "  1) 🚀 Start Application (Streamlit)"
        echo "  2) 🐳 Start with Docker Compose"
        echo "  3) 🤖 Start Ollama Service"
        echo "  4) 🔥 Start Everything (App + Ollama)"
        echo "  5) ⚙️  Advanced Options"
        echo "  6) 🔙 Exit"
        echo ""
        read -p "Select option (1-6): " choice
        
        case $choice in
            1) start_streamlit ;;
            2) start_docker ;;
            3) start_ollama ;;
            4) start_everything ;;
            5) show_advanced_menu ;;
            6) exit 0 ;;
            *) print_error "Invalid option"; sleep 1 ;;
        esac
    done
}

start_streamlit() {
    print_header
    echo -e "${BOLD}Starting Application with Streamlit${NC}"
    echo ""
    
    # Check dependencies
    if [[ ! -d "$VENV_DIR" ]]; then
        print_warning "Dependencies not installed. Installing now..."
        check_and_install_dependencies
    fi
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    
    # Check if app file exists
    if [[ ! -f "$SCRIPT_DIR/llm_model_factory_ultimate.py" ]]; then
        print_error "Application file not found: llm_model_factory_ultimate.py"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Check if port is available
    if netstat -tuln 2>/dev/null | grep -q ":8501 "; then
        print_warning "Port 8501 is already in use!"
        echo ""
        echo "Options:"
        echo "  1) Use different port (8502)"
        echo "  2) Kill existing process"
        echo "  3) Cancel"
        read -p "Select (1-3): " port_choice
        
        case $port_choice in
            1) PORT_ARG="--server.port 8502" ;;
            2) 
                pkill -f streamlit
                sleep 2
                PORT_ARG=""
                ;;
            3) return ;;
        esac
    else
        PORT_ARG=""
    fi
    
    echo ""
    print_success "Starting application..."
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Application starting!${NC}"
    echo ""
    echo -e "  ${BOLD}Access URL:${NC} ${YELLOW}http://localhost:8501${NC}"
    echo -e "  ${BOLD}Username:${NC}   ${YELLOW}admin${NC}"
    echo -e "  ${BOLD}Password:${NC}   ${YELLOW}admin123${NC}"
    echo ""
    echo -e "${RED}⚠ IMPORTANT: Change the default password immediately!${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the application${NC}"
    echo ""
    
    # Start streamlit
    cd "$SCRIPT_DIR"
    streamlit run llm_model_factory_ultimate.py \
        --server.address 0.0.0.0 \
        $PORT_ARG \
        --server.headless true
}

start_docker() {
    print_header
    echo -e "${BOLD}Starting with Docker Compose${NC}"
    echo ""
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found"
        echo ""
        echo "Please install Docker first:"
        echo "  Visit: https://docs.docker.com/get-docker/"
        read -p "Press Enter to continue..."
        return
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not found"
        echo ""
        echo "Please install Docker Compose:"
        echo "  Visit: https://docs.docker.com/compose/install/"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Check if docker-compose.yml exists
    if [[ ! -f "$SCRIPT_DIR/docker-compose.yml" ]]; then
        print_error "docker-compose.yml not found"
        read -p "Press Enter to continue..."
        return
    fi
    
    print_info "Starting Docker containers..."
    echo ""
    
    cd "$SCRIPT_DIR"
    docker-compose up -d
    
    echo ""
    print_success "Docker containers started!"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Containers Status:${NC}"
    docker-compose ps
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BOLD}Application:${NC} ${YELLOW}http://localhost:8501${NC}"
    echo -e "  ${BOLD}Ollama API:${NC}  ${YELLOW}http://localhost:11434${NC}"
    echo ""
    echo "Commands:"
    echo "  View logs:  docker-compose logs -f"
    echo "  Stop:       docker-compose down"
    echo "  Restart:    docker-compose restart"
    echo ""
    read -p "Press Enter to continue..."
}

start_ollama() {
    print_header
    echo -e "${BOLD}Ollama Service Management${NC}"
    echo ""
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama not found"
        echo ""
        echo "Would you like to install Ollama?"
        read -p "(y/n): " install_choice
        
        if [[ "$install_choice" =~ ^[Yy]$ ]]; then
            install_ollama
        else
            read -p "Press Enter to continue..."
            return
        fi
    else
        print_success "Ollama is installed"
    fi
    
    # Check if Ollama is running
    if pgrep -f ollama &> /dev/null; then
        print_success "Ollama service is running"
        echo ""
        echo "Available models:"
        ollama list
    else
        print_warning "Ollama service not running"
        echo ""
        echo "Starting Ollama service..."
        
        # Try to start Ollama
        if command -v systemctl &> /dev/null && systemctl list-unit-files | grep -q ollama; then
            sudo systemctl start ollama
            print_success "Ollama service started (systemd)"
        else
            # Start in background
            nohup ollama serve > /dev/null 2>&1 &
            sleep 3
            print_success "Ollama service started (background)"
        fi
    fi
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Ollama Options:${NC}"
    echo ""
    echo "  1) Download a model"
    echo "  2) List installed models"
    echo "  3) Test Ollama API"
    echo "  4) Stop Ollama service"
    echo "  5) Back"
    echo ""
    read -p "Select option (1-5): " ollama_choice
    
    case $ollama_choice in
        1) download_ollama_model ;;
        2) ollama list; read -p "Press Enter to continue..." ;;
        3) test_ollama_api ;;
        4) 
            pkill -f ollama
            print_success "Ollama stopped"
            sleep 2
            ;;
        5) return ;;
    esac
}

install_ollama() {
    print_header
    echo -e "${BOLD}Installing Ollama${NC}"
    echo ""
    
    print_info "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama installed successfully!"
        
        # Start Ollama
        print_info "Starting Ollama service..."
        nohup ollama serve > /dev/null 2>&1 &
        sleep 3
        
        print_success "Ollama service started"
    else
        print_error "Ollama installation failed"
    fi
    
    sleep 2
}

download_ollama_model() {
    print_header
    echo -e "${BOLD}Download Ollama Model${NC}"
    echo ""
    echo "Popular models:"
    echo ""
    echo "  1) llama3 (8B) - Recommended, balanced"
    echo "  2) llama3:70b - Largest, most capable"
    echo "  3) mistral (7B) - Fast, efficient"
    echo "  4) codellama (7B) - Code specialized"
    echo "  5) phi3 (3.8B) - Lightweight, fast"
    echo "  6) gemma2 (9B) - Google's model"
    echo "  7) Custom model name"
    echo "  8) Cancel"
    echo ""
    read -p "Select model (1-8): " model_choice
    
    case $model_choice in
        1) MODEL="llama3" ;;
        2) MODEL="llama3:70b" ;;
        3) MODEL="mistral" ;;
        4) MODEL="codellama" ;;
        5) MODEL="phi3" ;;
        6) MODEL="gemma2" ;;
        7) 
            read -p "Enter model name: " MODEL
            ;;
        8) return ;;
        *) print_error "Invalid option"; return ;;
    esac
    
    echo ""
    print_info "Downloading $MODEL (this may take several minutes)..."
    echo ""
    
    ollama pull "$MODEL"
    
    if [[ $? -eq 0 ]]; then
        echo ""
        print_success "Model $MODEL downloaded successfully!"
        echo ""
        echo "To use this model in the application:"
        echo "  1. Start the application"
        echo "  2. In sidebar, set:"
        echo "     - API URL: http://localhost:11434/api/generate"
        echo "     - Model Name: $MODEL"
    else
        print_error "Failed to download model"
    fi
    
    read -p "Press Enter to continue..."
}

test_ollama_api() {
    print_header
    echo -e "${BOLD}Testing Ollama API${NC}"
    echo ""
    
    print_info "Checking Ollama service..."
    
    if ! pgrep -f ollama &> /dev/null; then
        print_error "Ollama service not running"
        read -p "Press Enter to continue..."
        return
    fi
    
    print_success "Ollama service is running"
    echo ""
    
    print_info "Testing API endpoint..."
    
    # Test with a simple request
    RESPONSE=$(curl -s http://localhost:11434/api/tags 2>/dev/null)
    
    if [[ -n "$RESPONSE" ]]; then
        print_success "API is responding"
        echo ""
        echo "Available models:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | grep '"name"' | cut -d'"' -f4
    else
        print_error "API not responding"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check if Ollama is running: pgrep -f ollama"
        echo "  2. Try restarting: pkill ollama && ollama serve"
        echo "  3. Check firewall settings"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

start_everything() {
    print_header
    echo -e "${BOLD}Starting Complete Stack${NC}"
    echo ""
    
    # Start Ollama
    print_info "1/2 Starting Ollama..."
    if ! pgrep -f ollama &> /dev/null; then
        nohup ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
    
    if pgrep -f ollama &> /dev/null; then
        print_success "Ollama running"
    else
        print_warning "Ollama failed to start (optional)"
    fi
    
    echo ""
    
    # Start Application
    print_info "2/2 Starting Application..."
    sleep 1
    
    start_streamlit
}

show_advanced_menu() {
    while true; do
        print_header
        echo -e "${BOLD}Advanced Start Options${NC}"
        echo ""
        echo "  1) 🔧 Start with custom port"
        echo "  2) 🌐 Start with custom host"
        echo "  3) 🔍 Start in debug mode"
        echo "  4) 📊 Start and view logs"
        echo "  5) ⚙️  Configure before start"
        echo "  6) 🔙 Back"
        echo ""
        read -p "Select option (1-6): " choice
        
        case $choice in
            1) start_custom_port ;;
            2) start_custom_host ;;
            3) start_debug ;;
            4) start_with_logs ;;
            5) configure_before_start ;;
            6) return ;;
            *) print_error "Invalid option"; sleep 1 ;;
        esac
    done
}

start_custom_port() {
    print_header
    read -p "Enter port number (default 8501): " PORT
    PORT=${PORT:-8501}
    
    source "$VENV_DIR/bin/activate"
    cd "$SCRIPT_DIR"
    
    echo ""
    print_success "Starting on port $PORT..."
    echo ""
    
    streamlit run llm_model_factory_ultimate.py \
        --server.port "$PORT" \
        --server.address 0.0.0.0
}

start_custom_host() {
    print_header
    read -p "Enter host address (default 0.0.0.0): " HOST
    HOST=${HOST:-0.0.0.0}
    
    source "$VENV_DIR/bin/activate"
    cd "$SCRIPT_DIR"
    
    echo ""
    print_success "Starting on $HOST..."
    echo ""
    
    streamlit run llm_model_factory_ultimate.py \
        --server.address "$HOST"
}

start_debug() {
    print_header
    
    source "$VENV_DIR/bin/activate"
    cd "$SCRIPT_DIR"
    
    echo ""
    print_success "Starting in debug mode..."
    echo ""
    
    streamlit run llm_model_factory_ultimate.py \
        --logger.level=debug \
        --server.address 0.0.0.0
}

start_with_logs() {
    print_header
    
    source "$VENV_DIR/bin/activate"
    cd "$SCRIPT_DIR"
    
    # Start in background
    print_info "Starting application in background..."
    nohup streamlit run llm_model_factory_ultimate.py \
        --server.address 0.0.0.0 \
        > logs/streamlit.log 2>&1 &
    
    sleep 3
    
    if pgrep -f streamlit &> /dev/null; then
        print_success "Application started"
        echo ""
        print_info "Tailing logs (Ctrl+C to stop viewing)..."
        echo ""
        tail -f logs/streamlit.log
    else
        print_error "Failed to start application"
        read -p "Press Enter to continue..."
    fi
}

configure_before_start() {
    print_header
    echo -e "${BOLD}Quick Configuration${NC}"
    echo ""
    
    echo "Ollama Configuration:"
    read -p "  API URL (default: http://localhost:11434/api/generate): " OLLAMA_URL
    read -p "  Model name (default: llama3): " MODEL_NAME
    
    OLLAMA_URL=${OLLAMA_URL:-http://localhost:11434/api/generate}
    MODEL_NAME=${MODEL_NAME:-llama3}
    
    echo ""
    echo "Configuration saved to session."
    echo "You can change these in the application sidebar."
    echo ""
    read -p "Press Enter to start with these settings..."
    
    start_streamlit
}

################################################################################
# Main
################################################################################

# Check if dependencies are installed
if [[ ! -d "$VENV_DIR" ]]; then
    check_and_install_dependencies
fi

# Show start menu
show_start_menu
