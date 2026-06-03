# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-02
 Modified: 2026-06-02
 File: tests/paths/test_resolve_paths.py
 Version: 1.0.0
 Description: Description of this module
"""


from RunUpdates.core.constants import PACKAGE_ROOT
from RunUpdates.utils.common import resolve_paths

def test_resolve_paths_creates_directories(tmp_path, monkeypatch):
    # Fake args
    args = type("A", (), {
        "config_dir": None,
        "schema_dir": None,
        "log_dir": None,
        "inventory": None,
        "vault_path": None,
        "vault_password_file": None,
    })

    # Force HOME to tmp_path (only affects installed mode)
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = resolve_paths(args)

    # Check directories created
    assert paths.LOG_DIR.exists()
    assert paths.SUMMARY_HOST_DIR.exists()
    assert paths.SUMMARY_RUN_DIR.exists()

    # DEV MODE DEFAULTS
    assert paths.CONFIG_DIR == (PACKAGE_ROOT / "etc").resolve()
    assert paths.SCHEMA_DIR == (PACKAGE_ROOT / "schema").resolve()
    assert paths.LOG_DIR == (PACKAGE_ROOT / "var" / "log").resolve()