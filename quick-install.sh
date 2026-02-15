#!/bin/bash
################################################################################
# One-Line Installer for Secure LLM Model Factory
# Usage: curl -fsSL https://your-domain.com/quick-install.sh | bash
# Or: ./quick-install.sh
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}     🚀 Secure LLM Model Factory - Quick Install${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if files exist (local install)
if [[ -f "llm_model_factory_secure.py" ]]; then
    echo -e "${GREEN}✓ Files found locally${NC}"
    INSTALL_DIR="$(pwd)"
else
    echo -e "${YELLOW}⚠ Files not found. Assuming fresh directory.${NC}"
    INSTALL_DIR="$(pwd)"
fi

cd "$INSTALL_DIR"

# Step 1: Check Python
echo -e "\n${BLUE}[1/6]${NC} Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${YELLOW}✗ Python 3 not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
fi

# Step 2: Create virtual environment
echo -e "\n${BLUE}[2/6]${NC} Creating virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Step 3: Install dependencies
echo -e "\n${BLUE}[3/6]${NC} Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install streamlit requests -q
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 4: Create directory structure
echo -e "\n${BLUE}[4/6]${NC} Creating directories..."
mkdir -p workspace sandbox logs config
chmod 700 config
echo -e "${GREEN}✓ Directories created${NC}"

# Step 5: Set permissions
echo -e "\n${BLUE}[5/6]${NC} Setting permissions..."
if [[ -f "menu.sh" ]]; then
    chmod +x menu.sh
fi
if [[ -f "test.sh" ]]; then
    chmod +x test.sh
fi
echo -e "${GREEN}✓ Permissions set${NC}"

# Step 6: Show completion message
echo -e "\n${BLUE}[6/6]${NC} Installation complete!"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    ✓ Installation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo ""
echo "  1. Activate virtual environment:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "  2. Start the application:"
echo -e "     ${YELLOW}streamlit run llm_model_factory_secure.py${NC}"
echo ""
echo "  3. Or use the interactive menu:"
echo -e "     ${YELLOW}./menu.sh${NC}"
echo ""
echo -e "${BLUE}Default Login:${NC}"
echo -e "     Username: ${YELLOW}admin${NC}"
echo -e "     Password: ${YELLOW}admin123${NC}"
echo -e "     ${GREEN}(Change immediately after first login!)${NC}"
echo ""
echo -e "${BLUE}Access:${NC}"
echo -e "     ${YELLOW}http://localhost:8501${NC}"
echo ""
echo "For advanced options, run: ./menu.sh"
echo ""
