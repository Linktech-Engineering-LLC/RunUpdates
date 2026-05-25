# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
 Modified: 2026-05-22
 File: RunUpdates/ansible/loader.py
 Version: 2.0.0
 Description: Deterministic Inventory Loader for RunUpdates (multi-family)
"""
# System Libraries
from __future__ import annotations
from typing import Any, Dict, List, Optional

from PythonTools.ansible.loader import GenericInventoryLoader, InventoryError

class RunUpdatesInventoryLoader(GenericInventoryLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tree = self.load()
        self.index = self.build_index(tree)
    # ------------------------------------------------------------
    # Normalization Layer
    # ------------------------------------------------------------
    def normalize(
        self,
        family: Optional[str] = None,
        distro: Optional[str] = None,
        host: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Return a flattened list of fully-resolved host objects,
        filtered by family, distro, and/or host using the index.
        """

        output: List[Dict[str, Any]] = []

        # ------------------------------------------------------------
        # 1. Host-specific lookup (fast path)
        # ------------------------------------------------------------
        if host:
            if host not in self.index["hosts"]:
                raise InventoryError(f"Host '{host}' not found in inventory")

            fam, dist, host_node = self.index["hosts"][host]

            # Validate family/distro constraints if provided
            if family and fam != family:
                raise InventoryError(
                    f"Host '{host}' belongs to family '{fam}', not '{family}'"
                )

            if distro and dist != distro:
                raise InventoryError(
                    f"Host '{host}' belongs to distro '{dist}', not '{distro}'"
                )

            # Build and return a single host object
            return [self._build_host_obj(fam, dist, host, host_node)]

        # ------------------------------------------------------------
        # 2. Family + Distro lookup
        # ------------------------------------------------------------
        if family and distro:
            key = (family, distro)
            if key not in self.index["distros"]:
                raise InventoryError(f"Distro '{family}/{distro}' not found")

            dist_node = self.index["distros"][key]
            hosts_block = dist_node.get("hosts", {}) or {}

            for host_name, host_node in hosts_block.items():
                if host_node.get("enabled", True):
                    output.append(
                        self._build_host_obj(family, distro, host_name, host_node)
                    )

            return output

        # ------------------------------------------------------------
        # 3. Family-only lookup
        # ------------------------------------------------------------
        if family:
            if family not in self.index["families"]:
                raise InventoryError(f"Family '{family}' not found")

            for (fam, dist), dist_node in self.index["distros"].items():
                if fam != family:
                    continue

                hosts_block = dist_node.get("hosts", {}) or {}
                for host_name, host_node in hosts_block.items():
                    if host_node.get("enabled", True):
                        output.append(
                            self._build_host_obj(fam, dist, host_name, host_node)
                        )

            return output

        # ------------------------------------------------------------
        # 4. No filters → return ALL hosts (full inventory)
        # ------------------------------------------------------------
        for host_name, (fam, dist, host_node) in self.index["hosts"].items():
            if host_node.get("enabled", True):
                output.append(
                    self._build_host_obj(fam, dist, host_name, host_node)
                )

        return output

    def build_index(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        index = {
            "families": {},
            "distros": {},
            "hosts": {},
        }

        for family_name, family_node in tree.items():
            if not isinstance(family_node, dict):
                continue

            # Index family
            index["families"][family_name] = family_node

            for distro_name, distro_node in family_node.items():
                if distro_name == "vars":
                    continue
                if not isinstance(distro_node, dict):
                    continue

                # Index distro
                index["distros"][(family_name, distro_name)] = distro_node

                hosts_block = distro_node.get("hosts", {}) or {}
                for host_name, host_node in hosts_block.items():
                    if not isinstance(host_node, dict):
                        continue

                    # Index host → (family, distro, host_node)
                    index["hosts"][host_name] = (
                        family_name,
                        distro_name,
                        host_node,
                    )

        return index

    def _build_host_obj(
        self,
        family: str,
        distro: str,
        host_name: str,
        host_node: Dict[str, Any]
    ) -> Dict[str, Any]:

        # Family-level vars
        family_node = self.index["families"].get(family, {})
        family_vars = family_node.get("vars", {})
        family_port = family_vars.get("port")

        # Distro-level vars
        distro_node = self.index["distros"][(family, distro)]
        distro_vars = distro_node.get("vars", {})
        distro_port = distro_vars.get("port")

        # Systemd + lifecycle
        systemd = distro_node.get("systemd", False)
        systemd_mode = distro_node.get("systemd_mode", "wait")
        lifecycle = distro_node.get("lifecycle", [])

        # Commands + exit codes
        commands = distro_node.get("commands", {}) or {}
        exit_codes = distro_node.get("exit_codes", {}) or {}

        # Host-level overrides
        host_port = (
            host_node.get("port")
            or distro_port
            or family_port
            or 22
        )

        # Merge commands: distro first, host overrides last
        merged_cmds = {}
        merged_cmds.update(commands)
        merged_cmds.update(host_node.get("commands", {}) or {})

        # Required: address
        address = host_node.get("address")
        if not address:
            raise InventoryError(
                f"Host '{host_name}' under {family}/{distro} is missing 'address'."
            )

        return {
            "name": host_name,
            "family": family,
            "distro": distro,
            "enabled": host_node.get("enabled", True),
            "address": address,
            "port": host_port,
            "commands": merged_cmds,
            "exit_codes": exit_codes,
            "lifecycle": lifecycle,
            "systemd": systemd,
            "systemd_mode": systemd_mode,
            "vm_host": host_node.get("vm_host"),
        }
