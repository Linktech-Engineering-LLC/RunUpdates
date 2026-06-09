# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-31
 File: RunUpdates/utils/common.py
 Version: 1.0.0
 Description: Description of this module
        RunUpdates-specific utility functions.
        This module contains ONLY logic that belongs to the RunUpdates project.
        Generic helpers live in PythonTools.utils.common.
"""

import sys
import os
from pathlib import Path

# Import generic helpers from PythonTools
from PythonTools.ansible.helpers import resolve_with_priority
from PythonTools.parser.errors import CheckArgError

# Import RunUpdates-specific constants
from RunUpdates.core.constants import (
    CONFIG_ENV,
    INVENTORY_ENV,
    LOG_DIR_ENV,
    SCHEMA_ENV,
    VAULT_PATH_ENV,
    VAULT_PASSWORD_ENV,
    PACKAGE_ROOT,
    PROJECT_ROOT,
    INSTALL_ROOT,
    MODE
)
from .paths import Paths

def is_dev_mode() -> bool:
    # Dev mode: repo checkout with etc/ and var/ next to package
    return (PROJECT_ROOT / "etc").exists() and (PROJECT_ROOT / "var").exists()
# -------------------------------------------------------------
# Resolve Config & Schema folders
# -------------------------------------------------------------
def resolve_config_dir(args) -> Path:
    env = os.getenv(CONFIG_ENV)

    if MODE == "DEV":
        default = PACKAGE_ROOT / "etc"
    else:
        default = INSTALL_ROOT / "etc"

    return resolve_with_priority(args.config_dir, env, default)
def resolve_schema_dir(args, config_dir) -> Path:
    env = os.getenv(SCHEMA_ENV)
    default = config_dir / "schema"
    return resolve_with_priority(args.schema_dir, env, default)
def resolve_log_dir(args, default_base: Path) -> Path:
    """
    Resolve the log directory for RunUpdates.

    Priority:
      1. CLI override: --log-dir
      2. Environment variable: RUNUPDATES_LOG_DIR
      3. Default: <default_base>/var/log
    """
    env = os.getenv(LOG_DIR_ENV)
    default = default_base / "var" / "log"
    return resolve_with_priority(cli_value = args.log_dir, env_value = env, default = default)

def resolve_paths(args) -> Paths:
    """
    Resolve ALL runtime paths for RunUpdates.
    Centralized, freeze-safe, no dev-tree assumptions.
    """

    # Base config directory (raw CLI value)
    config_dir = resolve_config_dir(args)

    # Everything derives from CONFIG_DIR
    schema_dir = resolve_schema_dir(args, config_dir)
    log_dir = resolve_log_dir(args, config_dir.parent)

    # Summaries live under LOG_DIR
    summary_host_dir = log_dir / "summaries" / "hosts"
    summary_run_dir  = log_dir / "summaries" / "runs"

    # Inventory + vault
    inventory_path = resolve_inventory_path(args.inventory, config_dir)
    vault_path = resolve_vault_path(args.vault_path)
    vault_password_file = resolve_vault_password_file(args.vault_password_file)

    # Ensure directories exist
    log_dir.mkdir(parents=True, exist_ok=True)
    summary_host_dir.mkdir(parents=True, exist_ok=True)
    summary_run_dir.mkdir(parents=True, exist_ok=True)

    return Paths(
        CONFIG_DIR=config_dir,
        SCHEMA_DIR=schema_dir,
        LOG_DIR=log_dir,
        SUMMARY_HOST_DIR=summary_host_dir,
        SUMMARY_RUN_DIR=summary_run_dir,
        INVENTORY_PATH=inventory_path,
        VAULT_PATH=vault_path,
        VAULT_PASSWORD_FILE=vault_password_file,
    )

# ------------------------------------------------------------
# Inventory resolution logic (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_inventory_path(args_inventory: str | None, config_dir: Path) -> Path:
    env_value = os.getenv(INVENTORY_ENV)
    default_path = config_dir / "hosts.yml"
    return resolve_with_priority(args_inventory, env_value, default_path)
# ------------------------------------------------------------
# Vault path resolution (RunUpdates-specific)
# ------------------------------------------------------------

def resolve_vault_path(args_vault: str | None) -> Path | None:
    env_value = os.getenv(VAULT_PATH_ENV)
    path = resolve_with_priority(args_vault, env_value, default=None)
    return path if path else None

def resolve_vault_password_file(args_password_file: str | None) -> Path | None:
    env_value = os.getenv(VAULT_PASSWORD_ENV)
    path = resolve_with_priority(args_password_file, env_value, default=None)
    return path if path else None

# ------------------------------------------------------------
# Family / Distro / Host validation (RunUpdates-specific)
# ------------------------------------------------------------

def validate_family_distro_host(inventory_data, family, distro, host):
    """
    Validate that the selected family/distro/host exist in the RunUpdates inventory.
    This enforces the RunUpdates schema:
      inventory:
        family:
          distro:
            hosts: [...]
    """

    if not inventory_data:
        raise CheckArgError("Inventory data is empty or failed to load")

    # Validate family
    if family not in inventory_data:
        raise CheckArgError(f"Family '{family}' not found in inventory")

    family_block = inventory_data[family]

    # Validate distro
    if distro:
        if distro not in family_block:
            raise CheckArgError(
                f"Distro '{distro}' not found under family '{family}'"
            )
        distro_block = family_block[distro]
    else:
        distro_block = None

    # Validate host
    if host:
        if not distro:
            raise CheckArgError(
                f"Host '{host}' specified but no distro selected"
            )

        if distro_block is None:
            raise CheckArgError(
                f"Distro '{distro}' not found under family '{family}'"
            )

        hosts = distro_block.get("hosts", [])
        if host not in hosts:
            raise CheckArgError(
                f"Host '{host}' not found under {family}/{distro}"
            )
