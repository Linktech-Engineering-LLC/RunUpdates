# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
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
    Resolve vault file path using priority:
      1. Environment variable (RUNUPDATES_VAULT_PATH)
      2. CLI-provided --vault-path
    """

    # 1. ENVIRONMENT VARIABLE
    if VAULT_PATH_ENV in os.environ:
        path = Path(os.environ[VAULT_PATH_ENV]).expanduser()
        if path.exists():
            return str(path)
        raise VaultPasswordError(
            f"Vault path from {VAULT_PATH_ENV} does not exist: {path}"
        )

    # 2. CLI ARGUMENT
    if cli_vault_path:
        path = Path(cli_vault_path).expanduser()
        if path.exists():
            return str(path)
        raise VaultPasswordError(
            f"Vault path not found: {cli_vault_path}"
        )

    # 3. ERROR
    raise VaultPasswordError(
        f"No vault path provided. "
        f"Set {VAULT_PATH_ENV} or use --vault-path."
    )
