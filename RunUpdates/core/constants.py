# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-15
 File: RunUpdates/core/constants.py
 Version: 1.0.0
 Description: Description of this module
"""
# System Libraries
import platform
import sys
from pathlib import Path
# Project Libraries
from ..utils.common import read_project_file

# ------------------------------------------------------------
# Project metadata
# ------------------------------------------------------------
PROJECT_NAME = str(read_project_file("project.name"))
PROJECT_VERSION = str(read_project_file("project.version"))
LINUX_VERSION = platform.release()
PYTHON_VERSION = sys.version.split()[0]

# ------------------------------------------------------------
# Environment variable prefix
# ------------------------------------------------------------
ENV_PREFIX = PROJECT_NAME.upper().replace("-", "_").replace(" ", "_")
# ------------------------------------------------------------
# Ansible environment variables
# ------------------------------------------------------------
INVENTORY_PATH=f"{ENV_PREFIX}_INVENTORY"
VAULT_PASSWORD_ENV = f"{ENV_PREFIX}_VAULT_PASSWORD"
VAULT_PATH_ENV = f"{ENV_PREFIX}_VAULT_PATH"
VAULT_PASSWORD_FILE_ENV = f"{ENV_PREFIX}_VAULT_PASSWORD_FILE"

# ------------------------------------------------------------
# CLI defaults
# ------------------------------------------------------------
DEFAULT_INVENTORY_FORMAT = "yaml"
DEFAULT_DISTRO = None
