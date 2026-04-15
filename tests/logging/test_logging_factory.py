"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-14
 File: tests/test_logging_factory.py
 Version: 1.0.0
 Description: Description of this module
"""


import logging
import pytest
from pathlib import Path

@pytest.mark.logging
def test_logger_factory_creates_log_file(logger_factory, base_log_cfg):
    log_path = Path(base_log_cfg["path"])
    assert log_path.exists(), "Log file should be created on factory init"

@pytest.mark.logging
def test_logger_names(logger_factory):
    root_logger = logging.getLogger("RunUpdates.Logger")
    assert root_logger.name == "RunUpdates.Logger"

    module_logger = logger_factory.get_logger("update_runner")
    assert module_logger._base.name == "RunUpdates.update_runner"
