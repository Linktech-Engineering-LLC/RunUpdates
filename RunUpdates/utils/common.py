# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-15
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

# Import RunUpdates-specific constants
from RunUpdates.core.constants import (
    INVENTORY_ENV,
    VAULT_PATH_ENV,
    VAULT_PASSWORD_ENV,
    DEFAULT_INVENTORY_PATH,
)


# ------------------------------------------------------------
# Timestamp helper (RunUpdates-specific formatting)
# ------------------------------------------------------------

def current_timestamp() -> str:
    """Return a timezone-aware timestamp in ISO format."""
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z%z")


# ------------------------------------------------------------
# Inventory resolution logic (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_inventory_path(args_inventory: str | None) -> str:
    """
    Determine the inventory path using RunUpdates rules.

    Priority:
      1. CLI argument (if provided)
      2. Environment variable RUNUPDATES_INVENTORY
      3. Default inventory path under RunUpdates/etc
    """
    # Case 1: CLI argument provided
    if args_inventory:
        return str(resolve_path(args_inventory))

    # Case 2: Environment variable
    env_value = os.getenv(INVENTORY_ENV)
    if env_value:
        return str(resolve_path(env_value))

    # Case 3: Default
    return str(resolve_path(DEFAULT_INVENTORY_PATH))


# ------------------------------------------------------------
# Vault path resolution (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_vault_path(args_vault: str | None) -> str | None:
    """
    Determine the vault path using RunUpdates rules.

    Priority:
      1. CLI argument
      2. Environment variable RUNUPDATES_VAULT_PATH
      3. None (caller must validate)
    """
    if args_vault:
        return str(resolve_path(args_vault))

    env_value = os.getenv(VAULT_PATH_ENV)
    if env_value:
        return str(resolve_path(env_value))

    return None


def resolve_vault_password_file(args_password_file: str | None) -> str | None:
    """
    Determine the vault password file path.

    Priority:
      1. CLI argument
      2. Environment variable RUNUPDATES_VAULT_PASSWORD_FILE
      3. None
    """
    if args_password_file:
        return str(resolve_path(args_password_file))

    env_value = os.getenv(VAULT_PASSWORD_ENV)
    if env_value:
        return str(resolve_path(env_value))

    return None
