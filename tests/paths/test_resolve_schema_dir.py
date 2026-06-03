# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-02
 Modified: 2026-06-02
 File: tests/paths/test_resolve_schema_dir.py
 Version: 1.0.0
 Description: Description of this module
"""


from RunUpdates.core.constants import SCHEMA_ENV, PACKAGE_ROOT
from RunUpdates.utils.common import resolve_schema_dir

def test_schema_cli_override(monkeypatch, tmp_path):
    args = type("A", (), {"schema_dir": str(tmp_path / "cli")})
    config_dir = tmp_path / "config"
    result = resolve_schema_dir(args, config_dir)
    assert result == (tmp_path / "cli").resolve()

def test_schema_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv(SCHEMA_ENV, str(tmp_path / "env"))
    args = type("A", (), {"schema_dir": None})
    config_dir = tmp_path / "config"
    result = resolve_schema_dir(args, config_dir)
    assert result == (tmp_path / "env").resolve()

def test_schema_default_dev_mode(tmp_path):
    args = type("A", (), {"schema_dir": None})
    config_dir = tmp_path / "config"
    result = resolve_schema_dir(args, config_dir)

    # DEV MODE DEFAULT
    assert result == (PACKAGE_ROOT / "schema").resolve()
