# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-31
 Modified: 2026-05-31
 File: RunUpdates/utils/paths.py
 Version: 1.0.0
 Description: Description of this module
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class Paths:
    CONFIG_DIR: Path
    SCHEMA_DIR: Path
    LOG_DIR: Path
    SUMMARY_HOST_DIR: Path
    SUMMARY_RUN_DIR: Path
    INVENTORY_PATH: Optional[Path]
    VAULT_PATH: Optional[Path]
    VAULT_PASSWORD_FILE: Optional[Path]

