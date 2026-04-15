# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-15
 File: RunUpdates/parser/ScriptParser.py
 Version: 1.0.0
 Description: NMS_Tools-style command-line parser for RunUpdates (CLI-driven)
"""
# System Libraries
import argparse
import os
import sys
from pathlib import Path
# Project Libraries
from ..core.constants import (
    PROJECT_NAME, 
    PROJECT_VERSION, 
    LINUX_VERSION, 
    PYTHON_VERSION,
    VAULT_PATH_ENV,
)
from ..utils.common import (
    DEFAULT_INVENTORY_PATH,
    DEFAULT_LOG_DIR,
    resolve_inventory_path
)

# ------------------------------------------------------------
# Project metadata
# ------------------------------------------------------------
DESCRIPTION = (
    f"{PROJECT_NAME} version {PROJECT_VERSION} "
    "Manages System Patches and/or Updates"
)
# ------------------------------------------------------------
# Formatter + Error Classes (NMS_Tools style)
# ------------------------------------------------------------
class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    def _get_help_string(self, action):
        help_text = action.help or ""
        if "%(default)" in help_text:
            return help_text
        if action.default in (None, False):
            return help_text
        return f"{help_text} (default: {action.default})"
class CheckArgError(Exception):
    pass
class CheckArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"ERROR: {message}\n")
        self.print_help()
        sys.exit(1)
# ------------------------------------------------------------
# ScriptParser (CLI-driven)
# ------------------------------------------------------------
class ScriptParser:
    """
    CLI-driven parser for RunUpdates.
    No flags. No bitmask. Pure input collection + validation.
    """

    def __init__(self):
        self.parser = CheckArgumentParser(
            prog=PROJECT_NAME,
            description=DESCRIPTION,
            formatter_class=CustomFormatter,
            add_help=True,
        )

        self._add_core_args()
        self._add_logging_args()
        self._add_inventory_args()
        self._add_vault_args()
        self._add_update_args()
    # --------------------------------------------------------
    # Core Options
    # --------------------------------------------------------
    def _add_core_args(self):
        core = self.parser.add_argument_group("Core Options")

        core.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        core.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Simulate updates without applying changes"
        )

        core.add_argument(
            "-V", "--version",
            action="version",
            version=f"{PROJECT_NAME} {PROJECT_VERSION} running on Linux {LINUX_VERSION}"
        )
    # --------------------------------------------------------
    # Inventory Options
    # --------------------------------------------------------
    def _add_inventory_args(self):
        inv = self.parser.add_argument_group("Inventory Options")

        inv.add_argument(
            "-i", "--inventory",
            required=False,
            default=DEFAULT_INVENTORY_PATH,
            help="Path to inventory YAML file"
        )
    # --------------------------------------------------------
    # Logging Options
    # --------------------------------------------------------
    def _add_logging_args(self):
        log = self.parser.add_argument_group("Logging Options")
        log.add_argument(
            "-l", "--log-dir",
            dest="log_dir",
            default=DEFAULT_LOG_DIR,
            help="Folder containing the log file"
        )
        log.add_argument(
            "--log-max-mb",
            dest="log_max_mb",
            type=int,
            default=50,
            help="Maximum size of logs in MB before rotation"           
        )
        log.add_argument(
            "--compress-archive",
            dest="compress_archive",
            action="store_true",
            help="Compress rotated Log"
        )
        log.add_argument(
            "--delete-log",
            dest="delete_log",
            action="store_true",
            help="Remove rotated log"
        )
    # --------------------------------------------------------
    # Vault Options
    # --------------------------------------------------------
    def _add_vault_args(self):
        vault = self.parser.add_argument_group("Vault Options")

        vault.add_argument(
            "--vault-path",
            dest="vault_path",
            required=False,
            help="Path to vault file containing credentials"
        )

        vault.add_argument(
            "--vault-password",
            dest="vault_password",
            help="Direct vault password (least secure)"
        )

        vault.add_argument(
            "--vault-password-file",
            dest="vault_password_file",
            help="Path to file containing vault password"
        )
    # --------------------------------------------------------
    # Update Options
    # --------------------------------------------------------
    def _add_update_args(self):
        upd = self.parser.add_argument_group("Update Options")

        upd.add_argument(
            "--distro",
            required=False,
            help="Target Linux distribution (ubuntu, debian, rocky, etc.)"
        )
        
        upd.add_argument(
            "-H", "--host",
            required=False,
            help="Target Host to be updateded"
        )

        upd.add_argument(
            "--force",
            action="store_true",
            help="Force update even if checks fail"
        )
    # --------------------------------------------------------
    # Parse + Validate
    # --------------------------------------------------------
    def parse(self):
        self.args = self.parser.parse_args()
        self._validate()
        self.args.log_dir = os.path.expanduser(self.args.log_dir)
        self.args.inventory = os.path.expanduser(resolve_inventory_path(self.args.inventory))
        return self.args

    def _validate(self):
        
        if not self.args.vault_path and not VAULT_PATH_ENV in os.environ:
            raise CheckArgError("Missing required --vault-path")

        # Additional validation will be added later

    # --------------------------------------------------------
    # Accessor
    # --------------------------------------------------------
    def get_args(self):
        return self.args

