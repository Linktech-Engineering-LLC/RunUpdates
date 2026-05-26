# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-05-25
 File: RunUpdates/operations/listops.py
 Version: 1.0.0
 Description: JSON-based inventory introspection for RunUpdates
"""
# System Libraries
import json
from typing import Any, Optional

RESERVED_KEYS = {"vars", "defaults", "global"}

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
            distros = [
                d for d in self.inventory[family].keys()
                if d not in RESERVED_KEYS
            ]
            return self._dump(distros)

        # No family specified → list all distros grouped by family
        result = {
            fam: [
                d for d in node.keys()
                if d not in RESERVED_KEYS
            ]
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
                if dist in RESERVED_KEYS:
                    continue
                hosts = (dist_node.get("hosts") or {}).keys()
                for h in hosts:
                    result.append(f"{family}.{dist}.{h}")

            return self._dump(result)

        # Case 3: no family/distro → list ALL hosts fully-qualified
        result = []
        for fam, fam_node in self.inventory.items():
            for dist, dist_node in fam_node.items():
                if dist in RESERVED_KEYS:
                    continue
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

    def show_metadata(
        self,
        family: Optional[str],
        distro: Optional[str],
        host: Optional[str]
    ) -> str:
        result = {}

        # No family → show metadata for all families
        if not family:
            for fam, fam_node in self.inventory.items():
                if "vars" in fam_node:
                    result[fam] = {"vars": fam_node["vars"]}
            return self._dump(result)

        # Family only → show family-level metadata
        fam_node = self.inventory.get(family)
        if not fam_node:
            raise ValueError(f"Family '{family}' not found")

        result["vars"] = fam_node.get("vars", {})

        # Family + distro → include distro-level metadata if present
        if distro:
            dist_node = fam_node.get(distro)
            if not dist_node:
                raise ValueError(f"Distro '{distro}' not found under '{family}'")

            if "vars" in dist_node:
                result["distro_vars"] = dist_node["vars"]

        return self._dump(result)
