# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-25
 File: tests/ansible/test_build_host_obj.py
 Version: 1.0.0
 Description: Description of this module
"""

import pytest
from RunUpdates.ansible.loader import RunUpdatesInventoryLoader, InventoryError

@pytest.fixture
def loader(tmp_path):
    # Minimal inventory with inheritance structure
    inv = tmp_path / "inventory.yml"
    inv.write_text("""
linux:
  vars:
    port: 1111

  debian:
    vars:
      port: 2222
      commands:
        update: "apt update"
        upgrade: "apt upgrade"
      exit_codes:
        ok: 0
        changed: 100
      lifecycle:
        - pre
        - post
      systemd: true
      systemd_mode: wait
    hosts:
      deb-01:
        address: 10.0.0.1
        commands:
          upgrade: "apt full-upgrade"
        vm_host: hypervisor-01
""")

    # Minimal schema matching the above structure
    schema = tmp_path / "schema.yml"
    schema.write_text("""
root:
  type: dict
  required: true
  children:
    linux:
      type: dict
      required: false
      children:
        vars:
          type: dict
          required: false
        debian:
          type: dict
          required: false
          children:
            vars:
              type: dict
              required: false
            commands:
              type: dict
              required: false
            exit_codes:
              type: dict
              required: false
            lifecycle:
              type: list
              required: false
            systemd:
              type: bool
              required: false
            systemd_mode:
              type: str
              required: false
            hosts:
              type: dict
              required: false
""")

    return RunUpdatesInventoryLoader(
        inventory_path=str(inv),
        schema_path=str(schema)
    )


def test_build_host_obj_inheritance(loader):
    fam, dist, node = loader.index["hosts"]["deb-01"]
    host = loader._build_host_obj(fam, dist, "deb-01", node)

    # Basic identity
    assert host["name"] == "deb-01"
    assert host["family"] == "linux"
    assert host["distro"] == "debian"

    # Address required
    assert host["address"] == "10.0.0.1"

    # Port inheritance: host → distro → family → default
    assert host["port"] == 2222  # distro-level port overrides family

    # Command merging: distro first, host overrides last
    assert host["commands"]["update"] == "apt update"
    assert host["commands"]["upgrade"] == "apt full-upgrade"  # host override

    # Exit codes inherited from distro
    assert host["exit_codes"]["ok"] == 0
    assert host["exit_codes"]["changed"] == 100

    # Lifecycle inherited
    assert host["lifecycle"] == ["pre", "post"]

    # Systemd flags inherited
    assert host["systemd"] is True
    assert host["systemd_mode"] == "wait"

    # vm_host passthrough
    assert host["vm_host"] == "hypervisor-01"


def test_missing_address_raises(loader):
    fam, dist, node = loader.index["hosts"]["deb-01"]

    # Remove address to trigger validation
    bad_node = dict(node)
    bad_node.pop("address")

    with pytest.raises(InventoryError):
        loader._build_host_obj(fam, dist, "deb-01", bad_node)
