# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-25
 File: tests/ansible/test_loader_indexing.py
 Version: 1.0.0
 Description: Description of this module
"""



import pytest
from RunUpdates.ansible.loader import RunUpdatesInventoryLoader, InventoryError

@pytest.fixture
def loader(tmp_path):
    # Create inventory
    inv = tmp_path / "inventory.yml"
    inv.write_text("""
linux:
  vars:
    port: 2222

  debian:
    vars:
      port: 2200
    hosts:
      deb-01:
        address: 10.0.0.1
      deb-02:
        address: 10.0.0.2

  opensuse:
    hosts:
      suse-01:
        address: 10.0.1.1
""")

    # Create minimal valid schema
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
            hosts:
              type: dict
              required: false
        opensuse:
          type: dict
          required: false
          children:
            hosts:
              type: dict
              required: false
""")

    return RunUpdatesInventoryLoader(
        inventory_path=str(inv),
        schema_path=str(schema)
    )


# ------------------------------------------------------------
# INDEX TESTS
# ------------------------------------------------------------

def test_index_families(loader):
    assert "linux" in loader.index["families"]


def test_index_distros(loader):
    assert ("linux", "debian") in loader.index["distros"]
    assert ("linux", "opensuse") in loader.index["distros"]


def test_index_hosts(loader):
    assert "deb-01" in loader.index["hosts"]
    assert "deb-02" in loader.index["hosts"]
    assert "suse-01" in loader.index["hosts"]


def test_host_index_points_to_correct_family_and_distro(loader):
    fam, dist, node = loader.index["hosts"]["deb-01"]
    assert fam == "linux"
    assert dist == "debian"


# ------------------------------------------------------------
# NORMALIZE TESTS
# ------------------------------------------------------------

def test_normalize_family_distro(loader):
    hosts = loader.normalize(family="linux", distro="debian")
    names = {h["name"] for h in hosts}
    assert names == {"deb-01", "deb-02"}


def test_normalize_single_host(loader):
    hosts = loader.normalize(host="suse-01")
    assert len(hosts) == 1
    assert hosts[0]["name"] == "suse-01"
    assert hosts[0]["distro"] == "opensuse"


def test_normalize_invalid_host(loader):
    with pytest.raises(InventoryError):
        loader.normalize(host="no-such-host")


def test_normalize_wrong_distro(loader):
    # suse-01 is opensuse, not debian
    with pytest.raises(InventoryError):
        loader.normalize(host="suse-01", distro="debian")
