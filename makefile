# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

.PHONY: setup run clean help git-sync

help:
	@echo "Ollama Workstation Master Commands:"
	@echo "  make setup     - Install all libraries (Streamlit, psutil, GPUtil, etc.)"
	@echo "  make run       - Launch the Integrated Dashboard"
	@echo "  make clean     - Reset workspace and delete virtual environment"
	@echo "  make git-sync  - Save and push all code/sessions to Git"

setup:
	@echo "--- Installing Intel Arc & System Monitoring Tools ---"
	@sudo apt update && sudo apt install -y python3-venv git intel-gpu-tools
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install streamlit requests bandit psutil black pylint pytest py-cpuinfo
	# We add specific support for non-NVIDIA monitoring
	@echo "Setup complete."

run:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) setup; fi
	$(STREAMLIT) run app.py

git-sync:
	git add .
	git commit -m "Automated System Sync: $$(date)"
	git push origin main

clean:
	rm -rf $(VENV)
	rm -rf workspace/logs/*
	@echo "Environment reset."