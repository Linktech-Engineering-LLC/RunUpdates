# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
Modified: 2026-04-17
 File: RunUpdates/ansible/loader.py
 Version: 2.0.0
 Description: Deterministic Inventory Loader for RunUpdates (multi-family)
"""
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

    Inventory schema (v2):

    family:                # e.g., linux, windows, security
      distro:              # e.g., opensuse, redhat, ubuntu
        packages: {}       # command templates for this distro/family
        port: 22           # optional default port for this distro/family
        hosts:
          host-name:
            enabled: true
            address: [ 192.168.0.10 ]
            port: 2222
            vm_host: SomeHost
            virt_host: SomeHost
            packages: {}   # optional host-level overrides
    """

    def __init__(
        self,
        inventory: dict,
        family: str | None = None,
        distro: str | None = None,
        logger=None,
    ):
        """
        :param inventory: Parsed YAML inventory dict
        :param family:   Top-level family (e.g., 'linux', 'windows', 'security')
        :param distro:   Optional distro filter within the family
        :param logger:   Optional logger with .debug/.info/.warning/.error
        """
        self.inventory = inventory or {}
        self.family = family
        self.distro = distro
        self.logger = logger

        if not isinstance(self.inventory, dict):
            raise InventoryError("Invalid inventory: root must be a mapping")

        if self.family and self.family not in self.inventory:
            raise InventoryError(
                f"Family '{self.family}' not found in inventory "
                f"(available: {', '.join(self.inventory.keys())})"
            )

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def flatten(self) -> list[dict]:
        """
        Returns a list of host objects with:
        - name
        - family
        - distro
        - enabled
        - address
        - port
        - commands
        - vm_host (optional)
        """
        families = self._select_families()
        hosts: list[dict] = []

        for family in families:
            family_node = self.inventory.get(family, {})
            if not isinstance(family_node, dict):
                continue

            distros = self._select_distros(family_node)
            for distro in distros:
                distro_node = family_node.get(distro, {})
                if not isinstance(distro_node, dict):
                    continue

                distro_cmds = distro_node.get("packages", {}) or {}
                distro_port = distro_node.get("port")

                for host_name, host_data in (distro_node.get("hosts", {}) or {}).items():
                    host_obj = self._build_host(
                        family=family,
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
    # Family / distro selection
    # ----------------------------------------------------------------------
    def _select_families(self) -> list[str]:
        """
        If a family is specified, return just that.
        Otherwise, return all top-level families.
        """
        if self.family:
            return [self.family]

        return list(self.inventory.keys())

    def _select_distros(self, family_node: dict) -> list[str]:
        """
        If a distro is specified, validate it exists under this family.
        Otherwise, return all distros under the family.
        """
        if self.distro:
            if self.distro not in family_node:
                raise InventoryError(
                    f"Distro '{self.distro}' not found in family "
                    f"(available: {', '.join(family_node.keys())})"
                )
            return [self.distro]

        return list(family_node.keys())

    # ----------------------------------------------------------------------
    # Host builder
    # ----------------------------------------------------------------------
    def _build_host(
        self,
        family: str,
        distro: str,
        host_name: str,
        host_data: dict,
        distro_cmds: dict,
        distro_port: int | None,
    ) -> dict | None:
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
        port = host_data.get("port") or distro_port or DEFAULT_SSH_PORT

        # Command inheritance (distro-level, then host-level overrides)
        host_cmds = host_data.get("packages", {}) or {}
        commands = {**distro_cmds, **host_cmds}

        return {
            "name": host_name,
            "family": family,
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
    def _resolve_host_address(self, host_name: str, addresses: list[str]) -> str | None:
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


# ----------------------------------------------------------------------
# Optional: simple loader helper
# ----------------------------------------------------------------------
def load_inventory(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise InventoryError(f"Inventory file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
