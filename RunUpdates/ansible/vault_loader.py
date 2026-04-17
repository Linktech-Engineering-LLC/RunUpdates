# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
Modified: 2026-04-17
 File: RunUpdates/ansible/vault_loader.py
 Version: 1.0.0
 Description: Deterministic vault decryptor for RunUpdates.
"""

# System Libraries
from pathlib import Path
import subprocess
# Project Libraries
from ..core.constants import PROJECT_NAME

class VaultError(Exception):
    """Raised when vault decryption or file access fails."""
    pass

class VaultLoader:
    """
    Deterministic vault loader for RunUpdates.

    - Accepts a password source (literal string OR path)
    - Determines whether the password source is a file
    - Reads the password only if needed
    - Decrypts an Ansible vault file
    """

    def __init__(self, vault_file: str | Path, password_source: str):
        self.vault_file = Path(vault_file).expanduser()
        self.password_source = password_source  # literal OR path

    # ------------------------------------------------------------
    # Password Handling
    # ------------------------------------------------------------
    def resolve_password(self) -> str:
        """
        Determine whether password_source is a file or literal password.
        Read the file only if needed.
        """
        p = Path(self.password_source).expanduser()

        # If it's a file, read it
        if p.exists() and p.is_file():
            try:
                return p.read_text(encoding="utf-8").strip()
            except Exception as exc:
                raise VaultError(f"Failed to read password file: {p}") from exc

        # Otherwise treat as literal password
        return self.password_source.strip()

    # ------------------------------------------------------------
    # Vault Decryption
    # ------------------------------------------------------------
    def decrypt(self) -> str:
        """Decrypt the vault file and return plaintext."""
        if not self.vault_file.exists():
            raise VaultError(f"Vault file not found: {self.vault_file}")

        # Resolve password (literal or file)
        password = self.resolve_password()

        # Write password to a secure temp file for ansible-vault
        import tempfile

        with tempfile.NamedTemporaryFile("w", delete=True) as tmp:
            tmp.write(password)
            tmp.flush()

            cmd = [
                "ansible-vault",
                "view",
                "--vault-password-file",
                tmp.name,
                str(self.vault_file),
            ]

            try:
                return subprocess.check_output(cmd, text=True)
            except subprocess.CalledProcessError as exc:
                raise VaultError(f"Vault decryption failed: {exc}") from exc

    # ------------------------------------------------------------
    # Optional YAML Parsing
    # ------------------------------------------------------------
    def decrypt_yaml(self) -> dict:
        import yaml

        plaintext = self.decrypt()
        try:
            data = yaml.safe_load(plaintext) or {}
        except Exception as exc:
            raise VaultError("Vault decrypted but YAML parsing failed") from exc

        if not isinstance(data, dict):
            raise VaultError("Vault YAML must contain a top-level dictionary")
        data = data.get(PROJECT_NAME.lower(), {})
        return data
