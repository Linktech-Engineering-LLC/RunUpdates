# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-15
 File: RunUpdates/logging/factory.py
 Version: 1.1.0
 Description: Project-aware logging factory with rotation, archiving, and color support.
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .handlers import ArchiveRotatingFileHandler
from .logger import Logger


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",   # Cyan
        logging.INFO: "\033[32m",    # Green
        logging.WARNING: "\033[33m", # Yellow
        logging.ERROR: "\033[31m",   # Red
        logging.CRITICAL: "\033[41m" # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        base = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{base}{self.RESET}" if color else base


class LoggerFactory:
    """
    Creates project-aware loggers with rotation, archiving, and optional color output.
    """

    def __init__(self, log_cfg: dict, project_name: str):
        self.project_name = project_name
        self.log_cfg = log_cfg

        # Determine log file path
        self.log_path = Path(log_cfg["path"])
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure the project root logger
        self._configure_root_logger()

    # ------------------------------------------------------------
    # Root Logger Setup
    # ------------------------------------------------------------
    def _configure_root_logger(self):
        root_name = self.project_name
        root_logger = logging.getLogger(root_name)

        # Set log level
        level_name = self.log_cfg.get("log_level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        root_logger.setLevel(level)

        # Prevent propagation to Python root logger
        root_logger.propagate = False

        # Clear existing handlers
        root_logger.handlers.clear()

        # Rotation settings
        archive_mode = self.log_cfg.get("archive_mode", "tgz")
        backup_count = self.log_cfg.get("backup_count", 7)
        max_bytes = self.log_cfg.get("max_bytes", 50_000_000)

        # Always use ArchiveRotatingFileHandler
        file_handler = ArchiveRotatingFileHandler(
            filename=str(self.log_path),
            mode=archive_mode,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )

        # File formatter
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # Console handler
        if self.log_cfg.get("console_enabled", True):
            stream_handler = logging.StreamHandler()

            if self.log_cfg.get("color", False):
                stream_handler.setFormatter(
                    ColorFormatter("[%(levelname)s] %(name)s: %(message)s")
                )
            else:
                stream_handler.setFormatter(
                    logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
                )

            stream_handler.setLevel(logging.INFO)
            root_logger.addHandler(stream_handler)

    # ------------------------------------------------------------
    # Logger Retrieval
    # ------------------------------------------------------------
    def get_logger(self, module: str | None) -> Logger:
        """
        Returns a wrapped logger for the given module.
        Produces:
            <Project>.Logger
            <Project>.<module>
        """
        if module:
            base_logger = logging.getLogger(f"{self.project_name}.{module}")
        else:
            base_logger = logging.getLogger(f"{self.project_name}.Logger")

        return Logger(base=base_logger, module=module or "")

    def get_logger_cfg(self) -> dict:
        return self.log_cfg
