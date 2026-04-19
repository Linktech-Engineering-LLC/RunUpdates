# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-19
 Modified: 2026-04-19
 File: PythonTools/sessions/local_sessions.py
 Version: 1.0.0
 Description: Description of this module
"""
# System Libraries
from types import SimpleNamespace
# Project Libraries
from PythonTools.net_tools import local_command, sudo_run


class LocalSession:
    """
    Reusable local execution session.
    Provides a unified interface for running commands locally,
    with optional sudo support and injected logging.
    """

    def __init__(self, logger=None, sudo_password=None):
        """
        :param logger: Optional logger with .debug(), .info(), .error(), etc.
        :param sudo_password: Optional sudo password for privileged commands.
        """
        self.logger = logger
        self.sudo_password = sudo_password

    # ------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------
    def run(self, command: str, use_sudo: bool = False):
        """
        Execute a command locally.

        :param command: Shell command to run.
        :param use_sudo: Whether to run the command with sudo.
        :return: SimpleNamespace(stdout, stderr, code, msg, returncode, as_tuple)
        """

        if self.logger:
            mode = "sudo" if use_sudo else "local"
            self.logger.debug(f"[LocalSession] Executing ({mode}): {command}")

        if use_sudo:
            result = sudo_run(command, sudo_password=self.sudo_password)
        else:
            out, code, err = local_command(command)
            result = SimpleNamespace(
                msg=out,
                code=code,
                err=err,
                stdout=out,
                stderr=err,
                returncode=code,
                as_tuple=(out, code, err),
            )

        if self.logger:
            self.logger.debug(
                f"[LocalSession] Result code={result.code}, stdout={result.stdout}, stderr={result.stderr}"
            )

        return result

    # ------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------
    def close(self):
        """
        Included for interface compatibility with SSHSession.
        Local sessions do not maintain persistent state.
        """
        if self.logger:
            self.logger.debug("[LocalSession] close() called (no-op)")
        return True
