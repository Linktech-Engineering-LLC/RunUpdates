# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-31
 File: RunUpdates/parser/ScriptParser.py
 Version: 1.0.1
 Description: 
            RunUpdates ScriptParser (CLI-driven)
            Uses PythonTools BaseScriptParser + InventoryBaseParser
            Defines only RunUpdates-specific switches and validation.
"""
import sys

from PythonTools.parser.BaseScriptParser import BaseScriptParser
from RunUpdates.core.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
    LINUX_VERSION,
)
from RunUpdates.utils.common import (
    resolve_paths,
)

DESCRIPTION = (
    f"{PROJECT_NAME} version {PROJECT_VERSION} "
    "Manages System Patches and/or Updates"
)
DEFAULT_SUBCOMMAND = "update"
SUBCOMMANDS = {"update", "inventory", "summary"}

def _auto_insert_default_subcommand():
    # If user asked for help, do NOT insert default subcommand
    if "-h" in sys.argv or "--help" in sys.argv:
        return
    # No args at all → insert default
    if len(sys.argv) == 1:
        sys.argv.insert(1, DEFAULT_SUBCOMMAND)
        return

    first = sys.argv[1]

    # If first arg is a known subcommand → do nothing
    if first in SUBCOMMANDS:
        return

    # If first arg is a flag → insert default subcommand
    if first.startswith("-"):
        sys.argv.insert(1, DEFAULT_SUBCOMMAND)
        return

    # Otherwise: user typed something unexpected → let argparse handle it


class ScriptParser(BaseScriptParser):
    """
    RunUpdates CLI parser.
    Defines subcommands:
      - inventory
      - update
      - summary
    """

    def __init__(self):
        super().__init__(
            prog=PROJECT_NAME,
            description=DESCRIPTION,
            version_string=f"{PROJECT_NAME} {PROJECT_VERSION} running on Linux {LINUX_VERSION}",
        )

        # IMPORTANT:
        # Use the BaseScriptParser parser as the parent for all subcommands.
        self.parent = self.global_parent
        self.VERSION_STRING = f"{PROJECT_NAME} {PROJECT_VERSION} running on Linux {LINUX_VERSION}"
        # Subcommands
        self._add_help_subcommand()
        self._add_inventory_subcommand()
        self._add_update_subcommand()
        self._add_summary_subcommand()

    def _add_help_subcommand(self):
        help_parser = self.subparsers.add_parser(
            "help",
            parents=[self.global_parent],
            add_help=False,
            help="Show help for a subcommand",
        )

        help_parser.add_argument(
            "topic",
            nargs="?",
            help="Subcommand to show help for (inventory, update, summary)"
        )

    # --------------------------------------------------------
    # inventory subcommand
    # --------------------------------------------------------
    def _add_inventory_subcommand(self):
        inv = self.subparsers.add_parser(
            "inventory",
            parents=[self.global_parent],
            add_help=True,
            help="Inspect inventory families, distros, hosts, and metadata",
        )

        grp = inv.add_argument_group("Inventory Listing Options")

        grp.add_argument("--list-families", action="store_true",
                         help="List all inventory families as JSON")

        grp.add_argument("--list-distros", action="store_true",
                         help="List all distros for the selected family as JSON")

        grp.add_argument("--list-hosts", action="store_true",
                         help="List all hosts for the selected family/distro as JSON")

        grp.add_argument("--list-inventory", action="store_true",
                         help="Dump the full inventory block for the selected family/distro as JSON")

        grp.add_argument("--show-metadata", action="store_true",
                         help="Show metadata (vars) for the selected family/distro")

        # Shared selection flags
        sel = inv.add_argument_group("Selection Options")
        sel.add_argument("--family", help="Target family")
        sel.add_argument("--distro", help="Target distro")
        sel.add_argument("--host", help="Target host")
        
        self.inventory_parser = inv

    # --------------------------------------------------------
    # update subcommand
    # --------------------------------------------------------
    def _add_update_subcommand(self):
        upd = self.subparsers.add_parser(
            "update",
            parents=[self.global_parent],
            add_help=True,
            help="Run updates on selected hosts",
        )

        sel = upd.add_argument_group("Target Selection")
        sel.add_argument("--family", choices=["linux"], default="linux")
        sel.add_argument("--distro")
        sel.add_argument("-H", "--host")

        execgrp = upd.add_argument_group("Execution Options")
        execgrp.add_argument("--force", action="store_true",
                             help="Force update even if checks fail")
        execgrp.add_argument("--mode",
                             choices=["sequential", "parallel", "distro-parallel"],
                             default="sequential",
                             help="Execution mode for orchestrator")

        self.update_parser = upd
    # --------------------------------------------------------
    # summary subcommand
    # --------------------------------------------------------
    def _add_summary_subcommand(self):
        summary = self.subparsers.add_parser(
            "summary",
            parents=[self.global_parent],
            add_help=True,
            help="Show run summary information",
        )

        grp = summary.add_argument_group("Summary Options")
        grp.add_argument("--latest", action="store_true",
                         help="Show the most recent run summary")
        grp.add_argument("--list", action="store_true",
                         help="List all run summaries")
        grp.add_argument("--host", metavar="HOSTNAME",
                         help="Show summary for a specific host")

        self.summary_parser = summary
    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------
    def validate(self):
        super()._validate()

    # --------------------------------------------------------
    # Parse wrapper
    # --------------------------------------------------------
    def parse(self):
        _auto_insert_default_subcommand()

        args = super().parse()

        # Unified resolver
        self.paths = resolve_paths(args)

        return args
    # --------------------------------------------------------
    # Help handling
    # --------------------------------------------------------
    def print_help(self, topic: str | None = None):
        """
        Print help for the whole program or a specific subcommand.
        """
        # BaseScriptParser exposes the underlying argparse parser as self.parser
        parser = self.parser

        if topic:
            # Try to find a matching subcommand
            subparsers_action = None
            for action in parser._actions:
                if isinstance(action, type(self.subparsers)):
                    subparsers_action = action
                    break

            if subparsers_action and topic in subparsers_action.choices:
                subparsers_action.choices[topic].print_help()
                return

        # Fallback: top-level help
        parser.print_help()

