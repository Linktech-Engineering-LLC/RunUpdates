# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-27
 File: RunUpdates/parser/ScriptParser.py
 Version: 1.0.1
 Description: 
            RunUpdates ScriptParser (CLI-driven)
            Uses PythonTools BaseScriptParser + InventoryBaseParser
            Defines only RunUpdates-specific switches and validation.
"""

from pathlib import Path
import os

from PythonTools.parser.InventoryBaseParser import InventoryBaseParser
from PythonTools.parser.errors import CheckArgError
from PythonTools.logging.helpers import resolve_paths

# RunUpdates-specific constants
from RunUpdates.core.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    LINUX_VERSION,
    INVENTORY_ENV,
    VAULT_PATH_ENV,
    VAULT_PASSWORD_ENV,
    DEFAULT_INVENTORY_PATH,
    DEFAULT_LOG_DIR,
)

# RunUpdates-specific helpers
from RunUpdates.utils.common import (
    resolve_inventory_path,
    resolve_vault_path,
    resolve_vault_password_file,
    validate_family_distro_host,
)


DESCRIPTION = (
    f"{PROJECT_NAME} version {PROJECT_VERSION} "
    "Manages System Patches and/or Updates"
)


class ScriptParser(InventoryBaseParser):
    """
    RunUpdates CLI parser.
    Inherits:
      - core switches
      - logging switches
      - vault switches
      - inventory loading
    Adds:
      - family/distro/host switches
      - update switches
      - RunUpdates-specific validation
    """

    def __init__(self):
        self.paths = resolve_paths(__file__)
        super().__init__(
            prog=PROJECT_NAME,
            description=DESCRIPTION,
            version_string=f"{PROJECT_NAME} {PROJECT_VERSION} running on Linux {LINUX_VERSION}",
            default_log_dir=self.paths["LOG_DIR"],
            default_config_dir=self.paths["CONFIG_DIR"],
            default_schema_dir=self.paths["SCHEMA_DIR"]
        )
        self._defaults = self.paths
        self.subparsers = self.parser.add_subparsers(dest="command")

        self._add_runupdates_inventory_args()
        self._add_update_args()
        self._add_summary_args()

    # --------------------------------------------------------
    # RunUpdates Inventory Options
    # --------------------------------------------------------
    def _add_runupdates_inventory_args(self):
        inv = self.parser.add_argument_group("RunUpdates Inventory Options")

        group = inv.add_mutually_exclusive_group()

        group.add_argument("--list-families", action="store_true",
                           help="List all inventory families as JSON")

        group.add_argument("--list-distros", action="store_true",
                           help="List all distros for the selected family as JSON")

        group.add_argument("--list-hosts", action="store_true",
                           help="List all hosts for the selected family/distro as JSON")

        group.add_argument("--list-inventory", action="store_true",
                           help="Dump the full inventory block for the selected family/distro as JSON")
        group.add_argument(
            "--show-metadata",
            action="store_true",
            help="Show metadata (vars) for the selected family/distro"
        )

    # -------------------------------------------------------
    # Summary Options
    # -------------------------------------------------------
    def _add_summary_args(self):
        summary = self.subparsers.add_parser("summary", help="Show run summary information")
        summary.add_argument("--latest", action="store_true", help="Show the most recent run summary")
        summary.add_argument("--list", action="store_true", help="List all run summaries")
        summary.add_argument("--host", metavar="HOSTNAME", help="Show summary for a specific host")

    # --------------------------------------------------------
    # Update Options
    # --------------------------------------------------------
    def _add_update_args(self):
        upd = self.parser.add_argument_group("Update Options")

        upd.add_argument(
            "--family",
            choices=["linux"],
            default="linux",
            help="Target operating system family",
        )

        upd.add_argument(
            "--distro",
            required=False,
            help="Target Linux distribution",
        )

        upd.add_argument(
            "-H", "--host",
            required=False,
            help="Target host to update",
        )

        upd.add_argument(
            "--force",
            action="store_true",
            help="Force update even if checks fail",
        )
        upd.add_argument(
            "--mode",
            choices=["sequential", "parallel", "distro-parallel"],
            default="sequential",
            help="Execution mode for orchestrator (default: sequential)"            
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------
    def _validate(self):
        super()._validate()

        args = self.args

        # Resolve vault paths using RunUpdates logic
        args.vault_path = resolve_vault_path(args.vault_path)
        args.vault_password_file = resolve_vault_password_file(args.vault_password_file)

        # Vault path required
        if not args.vault_path and VAULT_PATH_ENV not in os.environ:
            raise CheckArgError(
                f"Missing required --vault-path or ${VAULT_PATH_ENV}"
            )

        # Vault password file required
        if not args.vault_password_file and VAULT_PASSWORD_ENV not in os.environ:
            raise CheckArgError(
                f"Missing required --vault-password-file or ${VAULT_PASSWORD_ENV}"
            )

        # Inventory resolution (RunUpdates-specific)
        args.inventory = resolve_inventory_path(args.inventory)

        if not Path(args.inventory).exists():
            raise CheckArgError(f"Inventory file not found: {args.inventory}")

        # Validate family/distro/host relationships
        validate_family_distro_host(
            inventory_data=self.inventory_data,
            family=args.family,
            distro=args.distro,
            host=args.host,
        )
    def parse(self):
        # 1. Pre-resolve inventory BEFORE parent parse
        #    so InventoryBaseParser sees a valid path
        pre_resolved_inventory = resolve_inventory_path(None)

        # 2. Call parent parse (InventoryBaseParser.parse)
        args = super().parse()

        # ------------------------------------------------------------
        # 3. Merge CLI overrides with environment defaults
        # ------------------------------------------------------------
        # LOG_DIR
        args.LOG_DIR = Path(args.log_dir or self._defaults["LOG_DIR"])

        # CONFIG_DIR
        args.CONFIG_DIR = Path(args.config_dir or self._defaults["CONFIG_DIR"])

        # SCHEMA_DIR
        args.SCHEMA_DIR = Path(args.schema_dir or self._defaults["SCHEMA_DIR"])

        # ------------------------------------------------------------
        # 4. Inventory resolution (your existing logic)
        # ------------------------------------------------------------
        if not args.inventory:
            args.inventory = pre_resolved_inventory

            # Now that inventory is known, load it
            self.inventory_path = Path(args.inventory).expanduser()
            self.inventory_data = self._load_inventory_yaml()

        # ------------------------------------------------------------
        # 5. Run RunUpdates-specific validation
        # ------------------------------------------------------------
        self._validate()

        # ------------------------------------------------------------
        # 6. Pass through project metadata
        # ------------------------------------------------------------
        args.PROJECT_NAME = self._defaults["PROJECT_NAME"]
        args.ENVIRONMENT = self._defaults["ENVIRONMENT"]

        return args

    # --------------------------------------------------------
    # Accessor
    # --------------------------------------------------------
    def get_args(self):
        return self.args
