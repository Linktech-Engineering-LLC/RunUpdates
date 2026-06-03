# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-30
 Modified: 2026-05-30
 File: RunUpdates/utils/validation.py
 Version: 1.0.0
 Description: Description of this module
"""


from PythonTools.ansible.helpers import InventoryLoadError


def validate_family_distro_host(inventory_data, family=None, distro=None, host=None):
    """
    Validate that the requested family/distro/host combination exists in the raw inventory.
    This runs BEFORE schema normalization and BEFORE filtering.

    inventory_data structure (raw YAML):
    {
        "families": {
            "linux": {
                "distros": {
                    "ubuntu": {
                        "hosts": {
                            "host1": {...},
                            "host2": {...}
                        }
                    }
                }
            }
        }
    }
    """

    if not inventory_data:
        raise InventoryLoadError("Inventory is empty or failed to load")

    families = inventory_data.get("families", {})
    if not families:
        raise InventoryLoadError("Inventory contains no families")

    # ------------------------------------------------------------
    # Validate family
    # ------------------------------------------------------------
    if family:
        if family not in families:
            raise InventoryLoadError(
                f"Family '{family}' not found in inventory. "
                f"Available families: {', '.join(sorted(families.keys()))}"
            )

    # If no family specified, nothing else can be validated
    if not family:
        return

    distros = families[family].get("distros", {})
    if not distros:
        raise InventoryLoadError(
            f"Family '{family}' contains no distros"
        )

    # ------------------------------------------------------------
    # Validate distro
    # ------------------------------------------------------------
    if distro:
        if distro not in distros:
            raise InventoryLoadError(
                f"Distro '{distro}' not found under family '{family}'. "
                f"Available distros: {', '.join(sorted(distros.keys()))}"
            )

    # If no distro specified, stop here
    if not distro:
        return

    hosts = distros[distro].get("hosts", {})
    if not hosts:
        raise InventoryLoadError(
            f"Distro '{distro}' under family '{family}' contains no hosts"
        )

    # ------------------------------------------------------------
    # Validate host
    # ------------------------------------------------------------
    if host:
        if host not in hosts:
            raise InventoryLoadError(
                f"Host '{host}' not found under {family}/{distro}. "
                f"Available hosts: {', '.join(sorted(hosts.keys()))}"
            )

        # Disabled host check
        host_data = hosts[host]
        if host_data.get("disabled", False):
            raise InventoryLoadError(
                f"Host '{host}' is marked as disabled in the inventory"
            )
