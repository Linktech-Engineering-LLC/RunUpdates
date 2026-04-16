# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-04-13
 File: RunUpdates/utils/vault.py
 Version: 1.0.0
 Description: Description of this module
"""

# System Libraries
import os
from pathlib import Path
# Project Libraries
from ..core.constants import (
    VAULT_PASSWORD_ENV,
    VAULT_PASSWORD_FILE_ENV,
    VAULT_PATH_ENV,
)

class VaultPasswordError(Exception):
    pass
class VaultPathError(Exception):
    pass

def resolve_vault_password(
    cli_password_file: str | None,
    cli_direct_password: str | None,
) -> str:
    """
    Resolve vault password using priority:
      1. Environment variable containing the password
      2. Environment variable pointing to a password file
      3. CLI-provided password file
      4. CLI-provided direct password
    """

    # 1. ENVIRONMENT VARIABLE CONTAINING PASSWORD
    if VAULT_PASSWORD_ENV in os.environ:
        value = os.environ[VAULT_PASSWORD_ENV].strip()
        if value:
            return value

    # 2. ENVIRONMENT VARIABLE POINTING TO PASSWORD FILE
    if VAULT_PASSWORD_FILE_ENV in os.environ:
        path = Path(os.environ[VAULT_PASSWORD_FILE_ENV]).expanduser()
        if not path.exists():
            raise VaultPasswordError(
                f"Password file from {VAULT_PASSWORD_FILE_ENV} not found: {path}"
            )
        value = path.read_text().strip()
        if value:
            return value

    # 3. CLI-PROVIDED PASSWORD FILE
    if cli_password_file:
        path = Path(cli_password_file).expanduser()
        if not path.exists():
            raise VaultPasswordError(f"Password file not found: {cli_password_file}")
        value = path.read_text().strip()
        if value:
            return value

    # 4. CLI-PROVIDED DIRECT PASSWORD
    if cli_direct_password:
        return cli_direct_password.strip()

    raise VaultPasswordError(
        "No vault password provided. "
        f"Set {VAULT_PASSWORD_ENV}, {VAULT_PASSWORD_FILE_ENV}, "
        "use --vault-password-file, or --vault-password."
    )
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
