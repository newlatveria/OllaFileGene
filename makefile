# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

.PHONY: setup run clean help

help:
	@echo "Ollama Workstation Master Commands:"
	@echo "  make setup     - Install Python dependencies (Streamlit, Requests, Bandit)"
	@echo "  make run       - Launch the complete Integrated Dashboard"
	@echo "  make clean     - Reset workspace, logs, and virtual environment"

setup:
	@echo "--- Initializing System Dependencies ---"
	@sudo apt update && sudo apt install -y python3-venv git
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install streamlit requests bandit
	mkdir -p workspace/logs
	@if [ ! -d ".git" ]; then git init; fi
	@echo "Setup complete. Launch with 'make run'"

run:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) setup; fi
	$(STREAMLIT) run app.py

clean:
	rm -rf $(VENV)
	rm -rf workspace/*
	@echo "Project workspace and environment reset."