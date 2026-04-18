# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-18
 File: RunUpdates/operations/listops.py
 Version: 1.0.0
 Description: JSON-based inventory introspection for RunUpdates
"""
# System Libraries
import json
from typing import Any


class ListOperations:
    """
    JSON-based inventory introspection for RunUpdates.
    Supports:
      --list-families
      --list-distros
      --list-hosts
      --list-inventory
    """

    def __init__(self, inventory: dict, processor, logger=None):
        self.inventory = inventory or {}
        self.processor = processor
        self.logger = logger

    # --------------------------------------------------------------
    # JSON helper
    # --------------------------------------------------------------
    def _dump(self, obj: Any) -> str:
        return json.dumps(obj, indent=2)

    # --------------------------------------------------------------
    # Families
    # --------------------------------------------------------------
    def list_families(self) -> str:
        families = list(self.inventory.keys())
        if self.logger:
            self.logger.debug(f"Families: {families}")
        return self._dump(families)

    # --------------------------------------------------------------
    # Distros
    # --------------------------------------------------------------
    def list_distros(self, family: str | None) -> str:
        if family:
            if family not in self.inventory:
                raise ValueError(f"Family '{family}' not found")
            distros = list(self.inventory[family].keys())
            return self._dump(distros)

        # No family specified → list all distros grouped by family
        result = {
            fam: list(node.keys())
            for fam, node in self.inventory.items()
            if isinstance(node, dict)
        }
        return self._dump(result)

    # --------------------------------------------------------------
    # Hosts
    # --------------------------------------------------------------
    def list_hosts(self, family: str | None, distro: str | None) -> str:
        # Case 1: family + distro → list hosts under that distro
        if family and distro:
            fam_node = self.inventory.get(family)
            if not fam_node:
                raise ValueError(f"Family '{family}' not found")

            dist_node = fam_node.get(distro)
            if not dist_node:
                raise ValueError(f"Distro '{distro}' not found under '{family}'")

            hosts = list((dist_node.get("hosts") or {}).keys())
            return self._dump(hosts)

        # Case 2: family only → list all hosts under all distros in that family
        if family:
            fam_node = self.inventory.get(family)
            if not fam_node:
                raise ValueError(f"Family '{family}' not found")

            result = []
            for dist, dist_node in fam_node.items():
                hosts = (dist_node.get("hosts") or {}).keys()
                for h in hosts:
                    result.append(f"{family}.{dist}.{h}")

            return self._dump(result)

        # Case 3: no family/distro → list ALL hosts fully-qualified
        result = []
        for fam, fam_node in self.inventory.items():
            for dist, dist_node in fam_node.items():
                hosts = (dist_node.get("hosts") or {}).keys()
                for h in hosts:
                    result.append(f"{fam}.{dist}.{h}")

        return self._dump(result)

    # --------------------------------------------------------------
    # Full inventory dump
    # --------------------------------------------------------------
    def list_inventory(self) -> str:
        """Dump the entire inventory as JSON."""
        return self._dump(self.inventory)
