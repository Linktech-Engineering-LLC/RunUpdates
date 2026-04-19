# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
 Modified: 2026-04-19
 File: RunUpdates/ansible/loader.py
 Version: 2.0.0
 Description: Deterministic Inventory Loader for RunUpdates (multi-family)
"""
# System Libraries
from __future__ import annotations

import yaml

from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SSH_PORT = 22


class InventoryError(Exception):
    pass


class InventoryProcessor:
    """
    Multi-family inventory processor for RunUpdates.

    Supports:
    - Required: family (defaults to linux)
    - Optional: distro
    - Optional: host
    - Port inheritance: host → distro → family → default
    """

    def __init__(self, logger):
        self.logger = logger

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def flatten(
        self,
        inventory: Dict[str, Any],
        family: str,
        distro: Optional[str],
        host: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        # Validate family
        if family not in inventory:
            raise InventoryError(f"Family '{family}' not found in inventory.")

        family_node = inventory[family]
        if not isinstance(family_node, dict):
            raise InventoryError(f"Family '{family}' is not a valid mapping.")

        family_port = family_node.get("port")

        # Determine which distros to process
        if distro:
            if distro not in family_node:
                raise InventoryError(
                    f"Distro '{distro}' not found under family '{family}'."
                )
            distros = [distro]
        else:
            # Process ALL distros under the family
            distros = [
                d for d in family_node.keys()
                if isinstance(family_node.get(d), dict)
            ]

        flattened: List[Dict[str, Any]] = []

        for distro_name in distros:
            distro_node = family_node[distro_name]

            distro_cmds = distro_node.get("packages", {}) or {}
            distro_port = distro_node.get("port")
            hosts_block = distro_node.get("hosts", {}) or {}

            # Determine which hosts to process
            if host:
                if host not in hosts_block:
                    raise InventoryError(
                        f"Host '{host}' not found under {family}/{distro_name}."
                    )
                host_list = [host]
            else:
                host_list = list(hosts_block.keys())

            for host_name in host_list:
                host_data = hosts_block.get(host_name, {}) or {}

                host_obj = self._build_host(
                    family=family,
                    distro=distro_name,
                    host_name=host_name,
                    host_data=host_data,
                    distro_cmds=distro_cmds,
                    host_port=host_data.get("port"),
                    distro_port=distro_port,
                    family_port=family_port,
                )

                if host_obj:
                    flattened.append(host_obj)

        return flattened

    # ------------------------------------------------------------------
    # Host builder
    # ------------------------------------------------------------------
    def _build_host(
        self,
        family: str,
        distro: str,
        host_name: str,
        host_data: Dict[str, Any],
        distro_cmds: Dict[str, Any],
        host_port: Optional[int],
        distro_port: Optional[int],
        family_port: Optional[int],
    ) -> Optional[Dict[str, Any]]:

        enabled = host_data.get("enabled", True)
        if not enabled:
            return None

        # Merge commands: distro-level first, host-level overrides
        commands = {}
        commands.update(distro_cmds)
        commands.update(host_data.get("packages", {}) or {})

        # Port inheritance: host → distro → family → default
        port = (
            host_port
            or distro_port
            or family_port
            or DEFAULT_SSH_PORT
        )

        # Required: address
        address = host_data.get("address")
        if not address:
            raise InventoryError(
                f"Host '{host_name}' under {family}/{distro} is missing 'address'."
            )

        return {
            "name": host_name,
            "family": family,
            "distro": distro,
            "enabled": enabled,
            "address": address,
            "port": port,
            "commands": commands,
            "vm_host": host_data.get("vm_host"),
        }


# ----------------------------------------------------------------------
# Optional: simple loader helper
# ----------------------------------------------------------------------
def load_inventory(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise InventoryError(f"Inventory file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
