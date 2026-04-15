# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-15
 File: RunUpdates/logging/logger.py
 Version: 2.0.0
 Description: Clean, project-aware logger wrapper for RunUpdates.
"""

import logging


def safe_level(level_name: str, fallback=logging.INFO):
    """
    Return a logging level if registered, otherwise fallback.
    Prevents crashes if AUDIT or LIFECYCLE are not registered yet.
    """
    return getattr(logging, level_name, fallback)


class Logger:
    """
    Lightweight wrapper around logging.Logger providing:
    - module-aware prefixes
    - audit() and lifecycle() helpers
    - command_* helpers
    - banner() helper
    """

    def __init__(self, base: logging.Logger, module: str):
        self._base = base
        self.module = module

        # Resolve custom levels safely
        self._audit_level = safe_level("AUDIT", logging.INFO)
        self._lifecycle_level = safe_level("LIFECYCLE", logging.INFO)
        self._trace_level = safe_level("TRACE", logging.DEBUG)

    # ------------------------------------------------------------
    # Audit + Lifecycle Logging (NO validation in RunUpdates)
    # ------------------------------------------------------------
    def audit(self, marker: str, message: str, **context):
        """
        Audit logs are structured informational events.
        No lifecycle validation in RunUpdates.
        """
        formatted = f"[{marker}] {message}"
        if self.module:
            formatted = f"[module={self.module}] {formatted}"
        if context:
            formatted += f" | context={context}"

        self._base.log(self._audit_level, formatted)

    def lifecycle(self, label: str, value: object = None):
        """
        Lifecycle logs are simple state markers.
        No validation, no enums.
        """
        msg = f"{label}={value}" if value is not None else label
        if self.module:
            msg = f"[module={self.module}] {msg}"
        self._base.log(self._lifecycle_level, msg)

    # ------------------------------------------------------------
    # Trace Logging
    # ------------------------------------------------------------
    def trace(self, msg: str):
        """
        Ultra-verbose diagnostic logging.
        """
        self._base.log(self._trace_level, self._prefix(msg))

    # ------------------------------------------------------------
    # Standard Logging Delegates
    # ------------------------------------------------------------
    def info(self, msg: str):
        self._base.info(self._prefix(msg))

    def debug(self, msg: str):
        self._base.debug(self._prefix(msg))

    def warning(self, msg: str):
        self._base.warning(self._prefix(msg))

    def error(self, msg: str):
        self._base.error(self._prefix(msg))

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _prefix(self, msg: str) -> str:
        if self.module:
            return f"[module={self.module}] {msg}"
        return msg

    # ------------------------------------------------------------
    # Command Helpers
    # ------------------------------------------------------------
    def command_start(self, cmd: str):
        self.audit("CMD_START", f"Executing command: {cmd}")

    def command_end(self, cmd: str, code: int):
        self.audit("CMD_END", f"Command finished: {cmd} | exit_code={code}")

    def command_error(self, func_name: str, error: Exception):
        self.audit(
            "CMD_FAIL",
            f"Command failed: {func_name} | {type(error).__name__}: {error}"
        )

    # ------------------------------------------------------------
    # Banner Helper
    # ------------------------------------------------------------
    def banner(self, message: str):
        line = "=" * 60
        self.info(line)
        self.info(f"== {message}")
        self.info(line)
