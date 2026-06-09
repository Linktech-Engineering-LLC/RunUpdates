# ------------------------------------------------------------
# RunUpdates Makefile
# ------------------------------------------------------------

PYTHON := python3
BUILD_SCRIPT := scripts/build.py
INSTALL_SCRIPT := scripts/install.sh
PROJECT := RunUpdates
PREFIX ?= /opt/RunUpdates
VENV := .venv

# ------------------------------------------------------------
# Build the frozen binary
# ------------------------------------------------------------
build:
    $(PYTHON) $(BUILD_SCRIPT) .

# ------------------------------------------------------------
# Install to system prefix
# ------------------------------------------------------------
install:
    @echo "Installing $(PROJECT) to $(PREFIX)"
    @chmod +x $(INSTALL_SCRIPT)
    $(INSTALL_SCRIPT) --prefix $(PREFIX)

# ------------------------------------------------------------
# Uninstall
# ------------------------------------------------------------
uninstall:
    @echo "Removing $(PREFIX)"
    rm -rf $(PREFIX)
    systemctl --user disable runupdates.service || true
    systemctl --user disable runupdates.timer || true
    systemctl --user daemon-reload

# ------------------------------------------------------------
# Clean build artifacts
# ------------------------------------------------------------
clean:
    rm -rf build dist release
    find . -name "__pycache__" -type d -exec rm -rf {} +
    rm -rf ~/.cache/pyinstaller

# ------------------------------------------------------------
# Full rebuild
# ------------------------------------------------------------
rebuild: clean build

# ------------------------------------------------------------
# Release build (version bump optional)
# ------------------------------------------------------------
release:
    $(PYTHON) $(BUILD_SCRIPT) --release .

# ------------------------------------------------------------
# Create and initialize the virtual environment
# ------------------------------------------------------------
venv:
    @if [ ! -d "$(VENV)" ]; then \
        echo "Creating virtual environment in $(VENV)"; \
        $(PYTHON) -m venv $(VENV); \
    fi
    @echo "Activating virtual environment and installing dependencies"
    @. $(VENV)/bin/activate && \
        pip install --upgrade pip && \
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
        if [ -f pyproject.toml ]; then pip install .; fi && \
        pip install pyinstaller
    @echo "Virtual environment ready in $(VENV)"
