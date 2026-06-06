# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-30
 File: RunUpdates/core/constants.py
 Version: 1.0.0
 Description: 
        RunUpdates-specific constants.
        This file defines ONLY the constants and environment variable names
        that belong to the RunUpdates project itself.
"""

from pathlib import Path
import platform
import sys

# ------------------------------------------------------------
# Project roots
# ------------------------------------------------------------
binary_path = Path(sys.argv[0]).resolve()

# If running from source, binary_path is RunUpdates/main.py
# If frozen, binary_path is RunUpdates/bin/RunUpdates

INSTALL_ROOT = binary_path.parent.parent
required_dirs = ["bin", "etc", "var"]

for d in required_dirs:
    if not (INSTALL_ROOT / d).exists():
        raise RuntimeError(f"Invalid install root: {INSTALL_ROOT}")


# Root of the RunUpdates package (…/RunUpdates/RunUpdates)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Root of the RunUpdates repository (…/RunUpdates)
PROJECT_ROOT = PACKAGE_ROOT.parent

PROJECT_NAME = "RunUpdates"
PROJECT_VERSION = "1.0.0"

# ------------------------------------------------------------
# System metadata
# ------------------------------------------------------------

PYTHON_VERSION = sys.version.split()[0]
LINUX_VERSION = platform.release()

# ------------------------------------------------------------
# Environment variable prefix
# ------------------------------------------------------------

ENV_PREFIX = PROJECT_NAME.upper().replace("-", "_").replace(" ", "_")

# ------------------------------------------------------------
# RunUpdates-specific environment variables
# ------------------------------------------------------------
CONFIG_ENV = f"{ENV_PREFIX}_CONFIG"
INVENTORY_ENV = f"{ENV_PREFIX}_INVENTORY"
LOG_DIR_ENV = f"{ENV_PREFIX}_LOG_DIR"
SCHEMA_ENV = f"{ENV_PREFIX}_SCHEMA"
VAULT_PATH_ENV = f"{ENV_PREFIX}_VAULT_PATH"
VAULT_PASSWORD_ENV = f"{ENV_PREFIX}_VAULT_PASSWORD_FILE"

# ------------------------------------------------------------
# Default paths (RunUpdates-specific)
# ------------------------------------------------------------

DEFAULT_CONFIG_DIR = INSTALL_ROOT / "etc"
DEFAULT_LOG_DIR = INSTALL_ROOT / "var" / "log"
DEFAULT_SUMMARY_DIR = PACKAGE_ROOT / "var" / "summary"
DEFAULT_INVENTORY_PATH = DEFAULT_CONFIG_DIR / "hosts.yml"
DEFAULT_RUN_PATH = INSTALL_ROOT / "var" / "run"
DEFAULT_BIN_PATH = INSTALL_ROOT / "bin"

PID_FILE = DEFAULT_RUN_PATH / f"{PROJECT_NAME.lower()}.pid"

# ------------------------------------------------------------
# CLI defaults
# ------------------------------------------------------------

DEFAULT_INVENTORY_FORMAT = "yaml"
DEFAULT_DISTRO = None

