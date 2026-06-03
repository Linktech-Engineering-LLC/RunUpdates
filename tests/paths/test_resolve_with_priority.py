# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-02
 Modified: 2026-06-02
 File: tests/paths/test_resolve_with_priority.py
 Version: 1.0.0
 Description: Description of this module
"""


from PythonTools.ansible.helpers import resolve_with_priority

def test_cli_wins_over_env_and_default():
    result = resolve_with_priority(cli_value="~/cli", env_value="/env", default="/default")
    assert str(result).endswith("cli")

def test_env_used_when_cli_missing():
    result = resolve_with_priority(cli_value=None, env_value="~/env", default="/default")
    assert str(result).endswith("env")

def test_default_used_when_cli_and_env_missing(tmp_path):
    default = tmp_path / "default"
    result = resolve_with_priority(cli_value=None, env_value=None, default=default)
    assert result == default.resolve()

def test_returns_none_when_all_missing():
    assert resolve_with_priority(None, None, None) is None

def test_expands_user_home(monkeypatch):
    monkeypatch.setenv("HOME", "/fakehome")
    result = resolve_with_priority(cli_value="~/logs", env_value=None, default=None)
    assert str(result) == "/fakehome/logs"
