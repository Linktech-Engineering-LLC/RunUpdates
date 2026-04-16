# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
 Modified: 2026-04-16
 File: RunUpdates/ansible/loader.py
 Version: 1.0.0
 Description: Deterministic Inventory Loader for RunUpdates
"""
# System Libraries
from pathlib import Path
import socket
import yaml

DEFAULT_SSH_PORT = 22


class InventoryError(Exception):
    pass


class InventoryProcessor:
    """
    Processes a RunUpdates inventory (hosts.yml) into a flattened,
    execution-ready list of host objects with inherited settings.
    """

    def __init__(self, inventory: dict, distro: str | None = None, logger=None):
        self.inventory = inventory
        self.distro = distro
        self.logger = logger

        # Validate top-level structure
        if "all" not in inventory or "children" not in inventory["all"]:
            raise InventoryError("Invalid inventory: missing all.children")

        self.root = inventory["all"]["children"]

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def flatten(self) -> list[dict]:
        """
        Returns a list of host objects with:
        - name
        - distro
        - enabled
        - address (list)
        - port
        - commands
        - vm_host (optional)
        """
        distros = self._select_distros()
        hosts = []

        for distro in distros:
            distro_node = self.root["linux"].get(distro)
            if not distro_node:
                continue

            distro_cmds = distro_node.get("packages", {})
            distro_port = distro_node.get("port")

            for host_name, host_data in distro_node.get("hosts", {}).items():
                host_obj = self._build_host(
                    distro=distro,
                    host_name=host_name,
                    host_data=host_data or {},
                    distro_cmds=distro_cmds,
                    distro_port=distro_port,
                )
                if host_obj:
                    hosts.append(host_obj)

        return hosts

    # ----------------------------------------------------------------------
    # Distro selection
    # ----------------------------------------------------------------------
    def _select_distros(self) -> list[str]:
        linux = self.root.get("linux", {})

        if self.distro:
            if self.distro not in linux:
                raise InventoryError(f"Distro '{self.distro}' not found in inventory")
            return [self.distro]

        return list(linux.keys())

    # ----------------------------------------------------------------------
    # Host builder
    # ----------------------------------------------------------------------
    def _build_host(self, distro, host_name, host_data, distro_cmds, distro_port):
        # Enabled flag
        enabled = host_data.get("enabled", True)
        if not enabled:
            return None

        # Address resolution
        addresses = host_data.get("address", [])
        if not isinstance(addresses, list):
            addresses = [addresses]

        resolved_address = self._resolve_host_address(host_name, addresses)

        # Port inheritance
        port = (
            host_data.get("port")
            or distro_port
            or DEFAULT_SSH_PORT
        )

        # Command inheritance
        host_cmds = host_data.get("packages", {})
        commands = {**distro_cmds, **host_cmds}

        return {
            "name": host_name,
            "distro": distro,
            "enabled": True,
            "address": resolved_address,
            "port": port,
            "commands": commands,
            "vm_host": host_data.get("vm_host") or host_data.get("virt_host"),
        }

    # ----------------------------------------------------------------------
    # Host address resolution
    # ----------------------------------------------------------------------
    def _resolve_host_address(self, host_name, addresses):
        """
        Resolution rules:
        1. Try hostname lookup
        2. Try each address in the list
        3. If none work, return the first address (best-effort)
        """
        # 1. Try hostname
        try:
            socket.gethostbyname(host_name)
            return host_name
        except Exception:
            pass

        # 2. Try each address
        for addr in addresses:
            try:
                socket.gethostbyname(addr)
                return addr
            except Exception:
                continue

        # 3. Best-effort fallback
        return addresses[0] if addresses else None
