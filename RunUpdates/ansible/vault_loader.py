# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
 Modified: 2026-04-16
 File: RunUpdates/ansible/vault_loader.py
 Version: 1.0.0
 Description: Deterministic vault decryptor for RunUpdates.
"""

# Standard library imports
"""
SPDX-License-Identifier: MIT
Copyright (c) 2026 Leon McClatchey,
Linktech Engineering LLC

vault_loader.py — Deterministic vault decryptor for RunUpdates.
"""

from pathlib import Path
import subprocess

class VaultError(Exception):
    """Raised when vault decryption or file access fails."""
    pass


class VaultLoader:
    """
    Minimal, deterministic vault loader for RunUpdates.

    - Reads a vault password file
    - Decrypts an Ansible vault file
    - Returns plaintext or parsed YAML (optional)
    """

    def __init__(self, vault_file: str | Path, password_file: str | Path):
        self.vault_file = Path(vault_file).expanduser()
        self.password_file = Path(password_file).expanduser()

    # ------------------------------------------------------------
    # Password Handling
    # ------------------------------------------------------------
    def read_password(self) -> str:
        """Read the vault password from the password file."""
        if not self.password_file.exists():
            raise VaultError(f"Password file not found: {self.password_file}")

        try:
            return self.password_file.read_text(encoding="utf-8").strip()
        except Exception as exc:
            raise VaultError(f"Failed to read password file: {self.password_file}") from exc

    # ------------------------------------------------------------
    # Vault Decryption
    # ------------------------------------------------------------
    def decrypt(self) -> str:
        """Decrypt the vault file and return plaintext."""
        if not self.vault_file.exists():
            raise VaultError(f"Vault file not found: {self.vault_file}")

        cmd = [
            "ansible-vault",
            "view",
            "--vault-password-file",
            str(self.password_file),
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
        """Decrypt and parse YAML content."""
        import yaml

        plaintext = self.decrypt()
        try:
            data = yaml.safe_load(plaintext) or {}
        except Exception as exc:
            raise VaultError("Vault decrypted but YAML parsing failed") from exc

        if not isinstance(data, dict):
            raise VaultError("Vault YAML must contain a top-level dictionary")

        return data