"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-14
 File: tests/test_logging_rotation.py
 Version: 1.0.0
 Description: Description of this module
"""


import logging
import pytest
from pathlib import Path
from RunUpdates.logging import LoggerFactory

@pytest.mark.rotation
def test_rotation_handler(temp_log_dir):
    cfg = {
        "enabled": True,
        "path": str(temp_log_dir / "RunUpdates.log"),
        "rotate_logs": True,
        "archive": False,
        "max_size": "1KB",
        "backup_count": 2,
        "console": False,
    }

    factory = LoggerFactory(cfg, "RunUpdates")
    logger = factory.get_logger("rotation_test")

    # Write enough data to force rotation
    for _ in range(200):
        logger.info("x" * 200)

    log_files = list(temp_log_dir.glob("RunUpdates.log*"))
    assert len(log_files) <= 3  # main + 2 backups
