# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-15
 File: RunUpdates/logging/log_helpers.py
 Version: 1.0.1
 Description: Logging initialization helpers for RunUpdates
"""

import logging
import os
from pathlib import Path

from .factory import LoggerFactory


def resolve_paths() -> dict:
    """
    Resolve deterministic project-local paths for RunUpdates.
    - Detect install root based on the package folder
    - Detect project name from package folder
    - Build LOG_DIR and CONFIG_DIR under install root
    """

    this_file = Path(__file__).resolve()
    package_dir = this_file.parents[1]      # .../RunUpdates/RunUpdates
    install_root = package_dir              # <-- use package_dir as root

    project_name = package_dir.name         # "RunUpdates"

    log_dir = install_root / "var" / "log"
    config_dir = install_root / "etc"

    log_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    return {
        "ROOT": str(install_root),
        "LOG_DIR": str(log_dir),
        "CONFIG_DIR": str(config_dir),
        "PROJECT_NAME": project_name,
    }


def init_logger(run_cfg: dict):
    """
    Initialize logging for RunUpdates.
    - Resolve install root and log directory
    - Apply CLI overrides
    - Build deterministic log file path
    - Perform size-based rotation
    - Instantiate LoggerFactory

    Returns:
        paths: dict of resolved paths
        log_cfg: final logging configuration dict
        logger_factory: initialized LoggerFactory
    """

    # ------------------------------------------------------------
    # 1. Resolve base paths (install root, LOG_DIR, CONFIG_DIR)
    # ------------------------------------------------------------
    paths = resolve_paths()
    project_name = paths["PROJECT_NAME"]

    # Default log directory: <install_root>/var/log
    default_log_dir = paths["LOG_DIR"]

    # CLI override: --log-dir
    cli_log_dir = run_cfg.get("log_dir")
    if cli_log_dir:
        log_dir = os.path.expanduser(cli_log_dir)
    else:
        log_dir = default_log_dir

    # Ensure directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # 2. Build deterministic log file path
    # ------------------------------------------------------------
    log_file = os.path.join(log_dir, f"{project_name}.log")

    # ------------------------------------------------------------
    # 3. Build log_cfg (RunUpdates has no YAML logging config)
    # ------------------------------------------------------------
    log_cfg = {
        "enabled": True,
        "path": log_file,
        "rotate_logs": True,
        "max_bytes": 50_000_000,   # 50 MB default
        "max_age_days": 30,
        "console_enabled": not run_cfg.get("no_console", False),
        "custom_levels": {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        },
    }

    # ------------------------------------------------------------
    # 4. Instantiate LoggerFactory
    # ------------------------------------------------------------
    logger_factory = LoggerFactory(
        log_cfg=log_cfg,
        project_name=project_name
    )

    return paths, log_cfg, logger_factory


def register_custom_levels(log_cfg: dict):
    """
    Register custom logging levels and attach helper methods to logging.Logger.

    Expected format:
        log_cfg["custom_levels"] = {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        }
    """

    custom_levels = log_cfg.get("custom_levels", {})
    if not custom_levels:
        return

    # Factory for creating bound logger methods
    def make_log_method(level_value: int, method_name: str):
        def log_method(self, message, *args, **kwargs):
            if self.isEnabledFor(level_value):
                self._log(level_value, message, args, **kwargs)
        log_method.__name__ = method_name.lower()
        return log_method

    for name, value in custom_levels.items():
        upper = name.upper()

        # Register level name with Python logging
        logging.addLevelName(value, upper)

        # Expose constant: logging.AUDIT = 25
        setattr(logging, upper, value)

        # Attach logger.audit(), logger.lifecycle(), etc.
        method = make_log_method(value, upper)
        setattr(logging.Logger, upper.lower(), method)
