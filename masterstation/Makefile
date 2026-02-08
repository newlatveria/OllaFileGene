# ---- MasterStation Makefile ----

APP=app.py
VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
STREAMLIT=$(VENV)/bin/streamlit

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup        Create virtual environment"
	@echo "  make install      Install dependencies"
	@echo "  make run          Run Streamlit app"
	@echo "  make lint         Run pylint"
	@echo "  make format       Format with black"
	@echo "  make security     Run bandit security scan"
	@echo "  make clean        Remove venv and caches"

# Create virtual environment
setup:
	python3 -m venv $(VENV)

# Install dependencies
install: setup
	$(PIP) install --upgrade pip
	$(PIP) install streamlit psutil py-cpuinfo requests black pylint bandit

# Run the app
run:
	@if [ ! -d "$(VENV)" ]; then make install; fi
	$(STREAMLIT) run $(APP)

# Code quality
lint:
	$(PYTHON) -m pylint .

format:
	$(PYTHON) -m black .

security:
	$(PYTHON) -m bandit -r .

# Clean environment
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
