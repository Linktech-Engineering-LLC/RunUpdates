"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-14
 File: tests/test_logging_levels.py
 Version: 1.0.0
 Description: Description of this module
"""


import logging
import pytest

@pytest.mark.lifecycle
def test_lifecycle_logging(logger_factory):
    logger = logger_factory.get_logger("runner")

    logger.lifecycle("STARTUP")
    logger.lifecycle("CONFIG_LOADED", value="ok")

@pytest.mark.lifecycle
def test_audit_logging(logger_factory):
    logger = logger_factory.get_logger("runner")

    logger.audit("CMD_START", "Running command")
    logger.audit("CMD_END", "Finished", exit_code=0)

@pytest.mark.lifecycle
def test_invalid_lifecycle_marker_raises(logger_factory):
    logger = logger_factory.get_logger("runner")

    with pytest.raises(ValueError):
        logger.audit("INVALID", "Should fail")
