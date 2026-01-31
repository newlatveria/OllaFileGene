# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

.PHONY: setup run clean help

help:
	@echo "Ollama Workstation Commands:"
	@echo "  make setup     - Create venv and install Streamlit/Requests/Bandit"
	@echo "  make run       - Start the Secure GUI Dashboard"
	@echo "  make clean     - Remove venv and temporary workspace files"

setup:
	@echo "--- Checking Dependencies ---"
	@dpkg -s python3-venv >/dev/null 2>&1 || (echo "Error: python3-venv is missing. Run: sudo apt install python3-venv" && exit 1)
	@echo "--- Initializing Linux Environment ---"
	rm -rf $(VENV)
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install streamlit requests bandit
	mkdir -p workspace
	@if [ ! -d ".git" ]; then git init; fi
	@echo "Setup complete. Launch with 'make run'"

run:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) setup; fi
	$(STREAMLIT) run app.py

clean:
	rm -rf $(VENV)
	rm -rf workspace/*
	find . -type d -name "__pycache__" -exec rm -rf {} +