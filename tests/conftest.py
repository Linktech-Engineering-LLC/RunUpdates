"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-14
 File: tests/conftest.py
 Version: 1.0.0
 Description: Description of this module
"""
# System Libraries

import pytest
from pathlib import Path
import tempfile
import shutil

from RunUpdates.logging.factory import LoggerFactory

@pytest.fixture
def temp_log_dir():
    """
    Provides a temporary directory for logging and rotation tests.
    Automatically cleaned up after the test.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="runupdates_logs_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def base_log_cfg(temp_log_dir):
    """
    Minimal config dict expected by LoggerFactory tests.
    Must include 'path' because tests reference base_log_cfg['path'].
    """
    log_path = temp_log_dir / "test_runupdates.log"

    return {
        "path": str(log_path),
        "level": "INFO",
        "project": "RunUpdates",
    }


@pytest.fixture
def logger_factory(base_log_cfg):
    """
    Returns a LoggerFactory instance configured with base_log_cfg.
    """
    return LoggerFactory(base_log_cfg, project_name="RunUpdates")