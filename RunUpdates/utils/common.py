# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-22
 File: RunUpdates/utils/common.py
 Version: 1.0.0
 Description: Description of this module
        RunUpdates-specific utility functions.
        This module contains ONLY logic that belongs to the RunUpdates project.
        Generic helpers live in PythonTools.utils.common.
"""

import os
from pathlib import Path
from datetime import datetime

# Import generic helpers from PythonTools
from PythonTools.utils.common import (
    load_yaml,
    load_json,
    string_to_dictionary,
    dict_to_string,
    coerce_bool,
    parse_size,
    resolve_path,
)
from PythonTools.ansible.helpers import resolve_with_priority

# Import RunUpdates-specific constants
from RunUpdates.core.constants import (
    INVENTORY_ENV,
    VAULT_PATH_ENV,
    VAULT_PASSWORD_ENV,
    DEFAULT_INVENTORY_PATH,
)

# ------------------------------------------------------------
# Inventory resolution logic (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_inventory_path(args_inventory: str | None) -> str:
    env_value = os.getenv(INVENTORY_ENV)
    path = resolve_with_priority(args_inventory, env_value, DEFAULT_INVENTORY_PATH)
    return str(path)


# ------------------------------------------------------------
# Vault path resolution (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_vault_path(args_vault: str | None) -> str | None:
    env_value = os.getenv(VAULT_PATH_ENV)
    path = resolve_with_priority(args_vault, env_value, default=None)
    return str(path) if path else None

def resolve_vault_password_file(args_password_file: str | None) -> str | None:
    env_value = os.getenv(VAULT_PASSWORD_ENV)
    path = resolve_with_priority(args_password_file, env_value, default=None)
    return str(path) if path else None
