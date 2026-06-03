# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-02
 Modified: 2026-06-02
 File: tests/paths/test_resolve_log_dir.py
 Version: 1.0.0
 Description: Description of this module
"""


from RunUpdates.core.constants import LOG_DIR_ENV
from RunUpdates.utils.common import resolve_log_dir 

def test_log_dir_cli_override(tmp_path):
    args = type("A", (), {"log_dir": str(tmp_path / "cli")})
    result = resolve_log_dir(args, tmp_path)
    assert result == (tmp_path / "cli").resolve()

def test_log_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv(LOG_DIR_ENV, str(tmp_path / "env"))
    args = type("A", (), {"log_dir": None})
    result = resolve_log_dir(args, tmp_path)
    assert result == (tmp_path / "env").resolve()

def test_log_dir_default(tmp_path):
    args = type("A", (), {"log_dir": None})
    result = resolve_log_dir(args, tmp_path)
    assert result == (tmp_path / "var" / "log").resolve()
