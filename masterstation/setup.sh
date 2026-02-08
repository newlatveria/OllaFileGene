#!/usr/bin/env bash

set -e  # stop on error

PROJECT_NAME="MasterStation"
VENV="venv"
APP="app.py"
ENV_FILE=".env"
REQ_FILE="requirements.txt"

echo "======================================"
echo "  $PROJECT_NAME Bootstrap Script"
echo "======================================"

# ---------- Check Python ----------
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "Python found: $(python3 --version)"

# ---------- Create venv ----------
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV
else
    echo "Virtual environment already exists."
fi

# ---------- Activate venv ----------
source $VENV/bin/activate

# ---------- Upgrade pip ----------
echo "Upgrading pip..."
pip install --upgrade pip

# ---------- Create requirements.txt if missing ----------
if [ ! -f "$REQ_FILE" ]; then
    echo "Creating default requirements.txt..."
    cat <<EOF > $REQ_FILE
streamlit
psutil
py-cpuinfo
requests
black
pylint
bandit
python-dotenv
EOF
fi

# ---------- Install dependencies ----------
echo "Installing dependencies..."
pip install -r $REQ_FILE

# ---------- Create .env if missing ----------
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating default .env..."
    cat <<EOF > $ENV_FILE
OLLAMA_DEFAULT_URL=http://localhost:11434
DEFAULT_MODEL=llama3
STREAMLIT_SERVER_PORT=8501
EOF
fi

# ---------- Verify app exists ----------
if [ ! -f "$APP" ]; then
    echo "Error: $APP not found in current directory."
    exit 1
fi

# ---------- Final System Check ----------
echo ""
echo "Environment Ready."
echo "Launching MasterStation..."
echo ""

streamlit run $APP

