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
    # ------------------------------------------------------------
    # Normalization Layer
    # ------------------------------------------------------------
    def normalize(self) -> List[Dict[str, Any]]:
        """
        Convert the inherited inventory tree into a flattened list of host objects.
        """
        tree = self.load()
        output = []

        for family_name, family_node in tree.items():
            if not isinstance(family_node, dict):
                continue

            family_vars = family_node.get("vars", {})
            family_port = family_vars.get("port")

            # Iterate distros
            for distro_name, distro_node in family_node.items():
                if distro_name == "vars":
                    continue
                if not isinstance(distro_node, dict):
                    continue

                distro_vars = distro_node.get("vars", {})
                distro_port = distro_vars.get("port")

                # Extract package commands
                raw_cmds = distro_node.get("packages", {}) or {}
                exit_codes = raw_cmds.get("exit_codes", {})
                commands = {k: v for k, v in raw_cmds.items() if k != "exit_codes"}

                # Hosts block
                hosts_block = distro_node.get("hosts", {}) or {}

                for host_name, host_data in hosts_block.items():
                    if not isinstance(host_data, dict):
                        continue

                    # Skip disabled hosts
                    if not host_data.get("enabled", True):
                        continue

                    # Required: address
                    address = host_data.get("address")
                    if not address:
                        raise InventoryError(
                            f"Host '{host_name}' under {family_name}/{distro_name} is missing 'address'."
                        )

                    # Port inheritance: host → distro → family → default
                    host_port = (
                        host_data.get("port")
                        or distro_port
                        or family_port
                        or 22
                    )

                    # Merge commands: distro-level first, host-level overrides
                    merged_cmds = {}
                    merged_cmds.update(commands)
                    merged_cmds.update(host_data.get("packages", {}) or {})

                    # Build final host object
                    host_obj = {
                        "name": host_name,
                        "family": family_name,
                        "distro": distro_name,
                        "enabled": host_data.get("enabled", True),
                        "address": address,
                        "port": host_port,
                        "commands": merged_cmds,
                        "exit_codes": exit_codes,
                        "vm_host": host_data.get("vm_host"),
                    }

                    output.append(host_obj)

        return output
