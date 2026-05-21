# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-17
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
import tomllib

# ------------------------------------------------------------
# Project roots
# ------------------------------------------------------------

# Root of the RunUpdates package (…/RunUpdates/RunUpdates)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Root of the RunUpdates repository (…/RunUpdates)
PROJECT_ROOT = PACKAGE_ROOT.parent

# ------------------------------------------------------------
# Project metadata (from RunUpdates/pyproject.toml)
# ------------------------------------------------------------

def _read_project_file(key: str):
    """Read a dotted key from RunUpdates' own pyproject.toml."""
    project_path = PROJECT_ROOT / "pyproject.toml"
    with project_path.open("rb") as f:
        data = tomllib.load(f)

    value = data
    for part in key.split("."):
        value = value[part]
    return value

PROJECT_NAME = str(_read_project_file("project.name"))
PROJECT_VERSION = str(_read_project_file("project.version"))

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

INVENTORY_ENV = f"{ENV_PREFIX}_INVENTORY"
VAULT_PATH_ENV = f"{ENV_PREFIX}_VAULT_PATH"
VAULT_PASSWORD_ENV = f"{ENV_PREFIX}_VAULT_PASSWORD_FILE"

# ------------------------------------------------------------
# Default paths (RunUpdates-specific)
# ------------------------------------------------------------

DEFAULT_ETC_DIR = PACKAGE_ROOT / "etc"
DEFAULT_LOG_DIR = PACKAGE_ROOT / "var" / "log"
DEFAULT_INVENTORY_PATH = DEFAULT_ETC_DIR / "hosts.yml"

# ------------------------------------------------------------
# CLI defaults
# ------------------------------------------------------------

DEFAULT_INVENTORY_FORMAT = "yaml"
DEFAULT_DISTRO = None
