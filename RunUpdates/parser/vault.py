# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-17
 File: RunUpdates/utils/vault.py
 Version: 1.0.0
 Description: Description of this module
"""

# System Libraries
import os
from pathlib import Path
# Project Libraries
from ..core.constants import (
    VAULT_PASSWORD_FILE_ENV,
    VAULT_PATH_ENV,
)

class VaultPasswordError(Exception):
    pass
class VaultPathError(Exception):
    pass

def resolve_vault_password(cli_value: str | None, logger=None):
    """
    Determine whether a vault password source was supplied.

    This function:
    - does NOT read files
    - does NOT validate paths
    - does NOT interpret the password
    - only checks CLI first, then environment
    - returns the raw value (string or path)

    Returns:
        str | None
    """

    # 1. CLI takes precedence
    if cli_value:
        if logger:
            logger.debug("Vault password source supplied via CLI")
        return cli_value

    # 2. Environment fallback
    env_value = os.getenv(VAULT_PASSWORD_FILE_ENV)
    if env_value:
        if logger:
            logger.debug("Vault password source supplied via environment")
        return env_value

    # 3. No password source
    if logger:
        logger.debug("No vault password source supplied")
    return None

def resolve_vault_path(cli_vault_path: str | None) -> str:
    """
    Priority:
      1. CLI argument (explicit override)
      2. Environment variable (if CLI not provided)
      3. Error (vault path is required)
    """

    env_value = os.environ.get(VAULT_PATH_ENV)

    # 1. CLI override
    if cli_vault_path:
        path = Path(cli_vault_path).expanduser()
        if not path.exists():
            raise VaultPathError(f"Vault path not found: {path}")
        return str(path)

    # 2. Environment variable
    if env_value:
        path = Path(env_value).expanduser()
        if not path.exists():
            raise VaultPathError(
                f"Vault path from {VAULT_PATH_ENV} does not exist: {path}"
            )
        return str(path)

    # 3. No vault path provided
    raise VaultPathError(
        f"No vault path provided. Set {VAULT_PATH_ENV} or use --vault-path."
    )
