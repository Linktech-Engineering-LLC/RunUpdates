# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-02
 Modified: 2026-06-02
 File: tests/paths/test_resolve_config_dir.py
 Version: 1.0.0
 Description: Description of this module
"""


from RunUpdates.core.constants import CONFIG_ENV, PACKAGE_ROOT
from RunUpdates.utils.common import resolve_config_dir

def test_config_dir_cli_override(monkeypatch, tmp_path):
    args = type("A", (), {"config_dir": str(tmp_path / "cli")})
    result = resolve_config_dir(args)
    assert result == (tmp_path / "cli").resolve()

def test_config_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv(CONFIG_ENV, str(tmp_path / "env"))
    args = type("A", (), {"config_dir": None})
    result = resolve_config_dir(args)
    assert result == (tmp_path / "env").resolve()

def test_config_dir_default_dev_mode(monkeypatch):
    monkeypatch.setenv(CONFIG_ENV, "")
    args = type("A", (), {"config_dir": None})
    result = resolve_config_dir(args)
    assert result == (PACKAGE_ROOT / "etc").resolve()
