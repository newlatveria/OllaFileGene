#!/bin/bash

################################################################################
# Secure LLM Model Factory - Installation Test & Validation Script
# Version: 2.0.0
# Tests all components and validates the installation
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_LOG="$SCRIPT_DIR/logs/test_results.log"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

mkdir -p "$SCRIPT_DIR/logs"

################################################################################
# Test Framework
################################################################################

start_test() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}Testing: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    ((TOTAL_TESTS++))
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED_TESTS++))
    echo "[$(date)] PASS: $1" >> "$TEST_LOG"
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED_TESTS++))
    echo "[$(date)] FAIL: $1" >> "$TEST_LOG"
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
    echo "[$(date)] WARN: $1" >> "$TEST_LOG"
}

info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

################################################################################
# Test Functions
################################################################################

test_file_structure() {
    start_test "File Structure"
    
    # Required files
    FILES=(
        "llm_model_factory_secure.py"
        "requirements.txt"
        "README.md"
        "SECURITY.md"
        "INSTALLATION.md"
        "menu.sh"
    )
    
    for file in "${FILES[@]}"; do
        if [[ -f "$SCRIPT_DIR/$file" ]]; then
            pass "Found required file: $file"
        else
            fail "Missing required file: $file"
        fi
    done
    
    # Required directories
    DIRS=(
        "workspace"
        "sandbox"
        "logs"
        "config"
    )
    
    for dir in "${DIRS[@]}"; do
        if [[ -d "$SCRIPT_DIR/$dir" ]]; then
            pass "Found required directory: $dir"
        else
            warn "Missing directory: $dir (will be created)"
            mkdir -p "$SCRIPT_DIR/$dir"
        fi
    done
}

test_python_environment() {
    start_test "Python Environment"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        
        if [[ $MAJOR -eq 3 && $MINOR -ge 8 ]]; then
            pass "Python version: $PYTHON_VERSION (>= 3.8)"
        else
            fail "Python version: $PYTHON_VERSION (< 3.8)"
        fi
    else
        fail "Python 3 not found"
    fi
    
    # Check virtual environment
    if [[ -d "$SCRIPT_DIR/venv" ]]; then
        pass "Virtual environment exists"
        
        # Check if activated
        if [[ -n "$VIRTUAL_ENV" ]]; then
            pass "Virtual environment is active"
        else
            warn "Virtual environment not activated"
        fi
        
        # Check installed packages
        if [[ -f "$SCRIPT_DIR/venv/bin/pip" ]]; then
            STREAMLIT_VERSION=$("$SCRIPT_DIR/venv/bin/pip" show streamlit 2>/dev/null | grep Version | awk '{print $2}')
            if [[ -n "$STREAMLIT_VERSION" ]]; then
                pass "Streamlit installed: $STREAMLIT_VERSION"
            else
                fail "Streamlit not installed in venv"
            fi
            
            REQUESTS_VERSION=$("$SCRIPT_DIR/venv/bin/pip" show requests 2>/dev/null | grep Version | awk '{print $2}')
            if [[ -n "$REQUESTS_VERSION" ]]; then
                pass "Requests installed: $REQUESTS_VERSION"
            else
                fail "Requests not installed in venv"
            fi
        fi
    else
        warn "Virtual environment not found (run installation)"
    fi
}

test_permissions() {
    start_test "File Permissions"
    
    # Check script executability
    if [[ -x "$SCRIPT_DIR/menu.sh" ]]; then
        pass "menu.sh is executable"
    else
        fail "menu.sh is not executable (run: chmod +x menu.sh)"
    fi
    
    # Check config directory permissions
    if [[ -d "$SCRIPT_DIR/config" ]]; then
        CONFIG_PERM=$(stat -c %a "$SCRIPT_DIR/config" 2>/dev/null || stat -f %A "$SCRIPT_DIR/config" 2>/dev/null)
        if [[ "$CONFIG_PERM" == "700" ]]; then
            pass "Config directory permissions: 700 (secure)"
        else
            warn "Config directory permissions: $CONFIG_PERM (should be 700)"
        fi
    fi
    
    # Check app file readability
    if [[ -r "$SCRIPT_DIR/llm_model_factory_secure.py" ]]; then
        pass "Application file is readable"
    else
        fail "Application file is not readable"
    fi
}

test_security_config() {
    start_test "Security Configuration"
    
    APP_FILE="$SCRIPT_DIR/llm_model_factory_secure.py"
    
    if [[ -f "$APP_FILE" ]]; then
        # Check for security classes
        if grep -q "class SecurityValidator" "$APP_FILE"; then
            pass "SecurityValidator class found"
        else
            fail "SecurityValidator class not found"
        fi
        
        if grep -q "class AuthManager" "$APP_FILE"; then
            pass "AuthManager class found"
        else
            fail "AuthManager class not found"
        fi
        
        if grep -q "class SandboxExecutor" "$APP_FILE"; then
            pass "SandboxExecutor class found"
        else
            fail "SandboxExecutor class not found"
        fi
        
        if grep -q "class RateLimiter" "$APP_FILE"; then
            pass "RateLimiter class found"
        else
            fail "RateLimiter class not found"
        fi
        
        # Check for blocked patterns
        if grep -q "BLOCKED_PATTERNS" "$APP_FILE"; then
            pass "Security patterns configured"
        else
            fail "Security patterns not found"
        fi
        
        # Check for audit logging
        if grep -q "audit_log" "$APP_FILE"; then
            pass "Audit logging implemented"
        else
            fail "Audit logging not implemented"
        fi
    else
        fail "Application file not found"
    fi
}

test_default_credentials() {
    start_test "Default Credentials"
    
    USERS_FILE="$SCRIPT_DIR/config/users.json"
    
    if [[ -f "$USERS_FILE" ]]; then
        if grep -q "admin123" "$USERS_FILE"; then
            warn "Default admin password detected! Change immediately!"
        else
            pass "Default password has been changed"
        fi
    else
        info "User database not yet created (normal for fresh install)"
    fi
}

test_docker_setup() {
    start_test "Docker Configuration"
    
    if command -v docker &> /dev/null; then
        pass "Docker is installed"
        
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        info "Docker version: $DOCKER_VERSION"
        
        # Check Dockerfile
        if [[ -f "$SCRIPT_DIR/Dockerfile" ]]; then
            pass "Dockerfile exists"
            
            # Validate Dockerfile
            if grep -q "FROM python:" "$SCRIPT_DIR/Dockerfile"; then
                pass "Dockerfile has valid base image"
            else
                fail "Dockerfile missing base image"
            fi
        else
            fail "Dockerfile not found"
        fi
        
        # Check docker-compose
        if [[ -f "$SCRIPT_DIR/docker-compose.yml" ]]; then
            pass "docker-compose.yml exists"
            
            # Check for security settings
            if grep -q "no-new-privileges" "$SCRIPT_DIR/docker-compose.yml"; then
                pass "Docker security hardening enabled"
            else
                warn "Docker security hardening not configured"
            fi
        else
            fail "docker-compose.yml not found"
        fi
        
    else
        info "Docker not installed (optional)"
    fi
    
    if command -v docker-compose &> /dev/null; then
        pass "Docker Compose is installed"
    else
        info "Docker Compose not installed (optional)"
    fi
}

test_ollama() {
    start_test "Ollama Configuration"
    
    if command -v ollama &> /dev/null; then
        pass "Ollama is installed"
        
        # Check if Ollama is running
        if pgrep -f ollama > /dev/null; then
            pass "Ollama service is running"
            
            # List models
            MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
            if [[ $MODELS -gt 0 ]]; then
                pass "Ollama has $MODELS model(s) installed"
            else
                warn "No Ollama models installed"
            fi
        else
            warn "Ollama installed but not running"
        fi
    else
        info "Ollama not installed (optional)"
    fi
}

test_network_ports() {
    start_test "Network Ports"
    
    # Check if port 8501 is available or in use
    if netstat -tuln 2>/dev/null | grep -q ":8501 "; then
        warn "Port 8501 is in use (application may be running)"
    else
        pass "Port 8501 is available"
    fi
    
    # Check if port 11434 is available (Ollama)
    if netstat -tuln 2>/dev/null | grep -q ":11434 "; then
        info "Port 11434 is in use (Ollama running)"
    else
        info "Port 11434 is available"
    fi
}

test_systemd_service() {
    start_test "Systemd Service"
    
    SERVICE_FILE="/etc/systemd/system/llm-factory.service"
    
    if [[ -f "$SERVICE_FILE" ]]; then
        pass "Systemd service file exists"
        
        # Check if service is enabled
        if systemctl is-enabled llm-factory &>/dev/null; then
            pass "Service is enabled"
        else
            warn "Service exists but not enabled"
        fi
        
        # Check if service is active
        if systemctl is-active llm-factory &>/dev/null; then
            pass "Service is active"
        else
            info "Service is not active"
        fi
    else
        info "Systemd service not installed (optional)"
    fi
}

test_nginx() {
    start_test "Nginx Configuration"
    
    if command -v nginx &> /dev/null; then
        pass "Nginx is installed"
        
        NGINX_CONF="/etc/nginx/sites-available/llm-factory"
        
        if [[ -f "$NGINX_CONF" ]]; then
            pass "Nginx configuration exists"
            
            # Test Nginx config
            if nginx -t &>/dev/null; then
                pass "Nginx configuration is valid"
            else
                fail "Nginx configuration has errors"
            fi
            
            # Check if site is enabled
            if [[ -L "/etc/nginx/sites-enabled/llm-factory" ]]; then
                pass "Site is enabled"
            else
                warn "Site not enabled"
            fi
        else
            info "Nginx not configured for this application"
        fi
    else
        info "Nginx not installed (optional)"
    fi
}

test_ssl() {
    start_test "SSL Configuration"
    
    if command -v certbot &> /dev/null; then
        pass "Certbot is installed"
        
        # List certificates
        CERTS=$(certbot certificates 2>/dev/null | grep "Domains:" | wc -l)
        if [[ $CERTS -gt 0 ]]; then
            pass "SSL certificate(s) installed: $CERTS"
        else
            info "No SSL certificates found"
        fi
    else
        info "Certbot not installed (optional)"
    fi
}

test_backup_config() {
    start_test "Backup Configuration"
    
    BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"
    
    if [[ -f "$BACKUP_SCRIPT" ]]; then
        pass "Backup script exists"
        
        if [[ -x "$BACKUP_SCRIPT" ]]; then
            pass "Backup script is executable"
        else
            warn "Backup script not executable"
        fi
        
        # Check if in crontab
        if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
            pass "Backup scheduled in crontab"
        else
            warn "Backup not scheduled in crontab"
        fi
    else
        warn "Backup script not configured"
    fi
}

test_firewall() {
    start_test "Firewall Configuration"
    
    if command -v ufw &> /dev/null; then
        pass "UFW is installed"
        
        if ufw status | grep -q "Status: active"; then
            pass "Firewall is active"
            
            # Check rules
            if ufw status | grep -q "22.*ALLOW"; then
                pass "SSH port (22) is allowed"
            else
                warn "SSH port not explicitly allowed"
            fi
            
            if ufw status | grep -q "80.*ALLOW"; then
                info "HTTP port (80) is allowed"
            fi
            
            if ufw status | grep -q "443.*ALLOW"; then
                info "HTTPS port (443) is allowed"
            fi
            
            if ufw status | grep -q "8501.*DENY"; then
                pass "Direct Streamlit access (8501) is blocked"
            else
                warn "Streamlit port not explicitly blocked"
            fi
        else
            warn "Firewall is installed but not active"
        fi
    else
        info "UFW not installed (optional)"
    fi
}

test_logs() {
    start_test "Logging System"
    
    # Check log directory
    if [[ -d "$SCRIPT_DIR/logs" ]]; then
        pass "Log directory exists"
        
        # Check for log files
        if [[ -f "$SCRIPT_DIR/logs/audit.log" ]]; then
            AUDIT_LINES=$(wc -l < "$SCRIPT_DIR/logs/audit.log")
            info "Audit log has $AUDIT_LINES entries"
        else
            info "Audit log not yet created (normal for fresh install)"
        fi
        
        if [[ -f "$SCRIPT_DIR/logs/app.log" ]]; then
            APP_LINES=$(wc -l < "$SCRIPT_DIR/logs/app.log")
            info "Application log has $APP_LINES entries"
        else
            info "Application log not yet created"
        fi
        
        # Check log permissions
        LOG_PERM=$(stat -c %a "$SCRIPT_DIR/logs" 2>/dev/null || stat -f %A "$SCRIPT_DIR/logs" 2>/dev/null)
        if [[ "$LOG_PERM" == "755" ]] || [[ "$LOG_PERM" == "700" ]]; then
            pass "Log directory has secure permissions: $LOG_PERM"
        else
            warn "Log directory permissions: $LOG_PERM"
        fi
    else
        fail "Log directory not found"
    fi
}

test_documentation() {
    start_test "Documentation"
    
    DOCS=(
        "README.md"
        "SECURITY.md"
        "INSTALLATION.md"
        "COMPARISON.md"
    )
    
    for doc in "${DOCS[@]}"; do
        if [[ -f "$SCRIPT_DIR/$doc" ]]; then
            SIZE=$(wc -l < "$SCRIPT_DIR/$doc")
            pass "Found $doc ($SIZE lines)"
        else
            warn "Missing documentation: $doc"
        fi
    done
}

test_application_syntax() {
    start_test "Application Syntax Check"
    
    APP_FILE="$SCRIPT_DIR/llm_model_factory_secure.py"
    
    if [[ -f "$APP_FILE" ]]; then
        # Check Python syntax
        if python3 -m py_compile "$APP_FILE" 2>/dev/null; then
            pass "Python syntax is valid"
        else
            fail "Python syntax errors detected"
        fi
        
        # Check for common issues
        if grep -q "TODO" "$APP_FILE"; then
            warn "Found TODO items in code"
        fi
        
        if grep -q "FIXME" "$APP_FILE"; then
            warn "Found FIXME items in code"
        fi
        
        # Check for hardcoded credentials
        if grep -qi "password.*=.*['\"]" "$APP_FILE" | grep -v "hash" | grep -q .; then
            warn "Possible hardcoded credentials found"
        fi
    fi
}

################################################################################
# Run All Tests
################################################################################

run_all_tests() {
    echo -e "${BOLD}${BLUE}"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "          🔐 Secure LLM Model Factory - Test Suite"
    echo "═══════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    echo "Starting tests at $(date)"
    echo ""
    
    # Clear log
    > "$TEST_LOG"
    
    # Run all tests
    test_file_structure
    test_python_environment
    test_permissions
    test_security_config
    test_default_credentials
    test_docker_setup
    test_ollama
    test_network_ports
    test_systemd_service
    test_nginx
    test_ssl
    test_backup_config
    test_firewall
    test_logs
    test_documentation
    test_application_syntax
    
    # Summary
    echo ""
    echo -e "${BOLD}${BLUE}"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                         Test Summary"
    echo "═══════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    
    echo -e "Total Tests:    ${BOLD}$TOTAL_TESTS${NC}"
    echo -e "Passed:         ${GREEN}${BOLD}$PASSED_TESTS${NC}"
    echo -e "Failed:         ${RED}${BOLD}$FAILED_TESTS${NC}"
    echo -e "Warnings:       ${YELLOW}${BOLD}$WARNINGS${NC}"
    echo ""
    
    # Calculate percentage
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        PASS_PCT=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo -e "Success Rate:   ${BOLD}$PASS_PCT%${NC}"
    fi
    
    echo ""
    echo "Detailed results saved to: $TEST_LOG"
    echo ""
    
    # Final verdict
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ All critical tests passed!${NC}"
        if [[ $WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}⚠ Review warnings for optimization opportunities${NC}"
        fi
        return 0
    else
        echo -e "${RED}${BOLD}✗ Some tests failed. Review errors above.${NC}"
        return 1
    fi
}

################################################################################
# Main
################################################################################

run_all_tests
