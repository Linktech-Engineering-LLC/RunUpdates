# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-19
 File: RunUpdates/operations/executor.py
 Version: 1.0.0
 Description: Executes update commands on a host using a session object.
"""
# System Libraries
from typing import Optional
# Project Libraries
from PythonTools.net_tools import sudo_run
from PythonTools.sessions.ssh_sessions import SSHSession

class HostExecutor:
    """
    Executes update commands on a host using a connection descriptor.

    Connection descriptor from HostConnector.connect():
        - "local"
        - SSHConnectionInfo(...)
    """

    def __init__(self, secrets: dict, logger=None, dry_run: bool = False):
        self.secrets = secrets
        self.logger = logger
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_updates(self, host: dict, conn_info) -> None:
        """
        Execute the update lifecycle for a host.

        Host dict fields:
          - name
          - commands: dict with keys:
                check
                refresh
                update
                clean
                reboot (optional)
        """

        name = host["name"]
        cmds = host.get("commands", {})

        if self.logger:
            self.logger.info(f"=== Running updates for {name} ===")

        # 1. Establish session
        if conn_info == "local":
            session = "local"
        else:
            session = SSHSession(
                hostname=conn_info.hostname,
                port=conn_info.port,
                username=conn_info.username,
                keyfile=conn_info.keyfile,
                password=conn_info.password,
                logger=self.logger,
            )
            session.connect()

        try:
            # 2. Execute lifecycle steps
            self._run_step(session, host, "check", cmds.get("check"))
            self._run_step(session, host, "refresh", cmds.get("refresh"))
            self._run_step(session, host, "update", cmds.get("update"))
            self._run_step(session, host, "clean", cmds.get("clean"))

            reboot_cmd = cmds.get("reboot")
            if reboot_cmd:
                self._run_step(session, name, "reboot", reboot_cmd)

        finally:
            # 3. Close session
            if session != "local":
                session.close()

        if self.logger:
            self.logger.info(f"=== Completed updates for {name} ===")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run_step(self, session, host: dict, step: str, command: Optional[str]):
        """
        Execute a single step in the update lifecycle.
        """

        if not command:
            if self.logger:
                self.logger.debug(f"[{host.get("name")}] Skipping '{step}' (no command)")
            return

        if self.dry_run:
            if self.logger:
                self.logger.info(f"[{host.get("name")}] DRY-RUN: {step}: {command}")
            return

        if self.logger:
            self.logger.info(f"[{host.get("name")}] {step}: {command}")

        # Local execution path
        if session == "local":
            rc = sudo_run(
                cmd=command,
                sudo_password=self.secrets.get("sudo_pass", "")
            )
            exit_code, out, err = rc.as_tuple

        # Remote execution path
        else:
            result = session.run(command)
            out, exit_code, err = result.as_tuple

        # Logging
        if self.logger:
            self.logger.debug(f"[{host.get("name")}] {step} exit={exit_code}")
            if out.strip():
                self.logger.debug(f"[{host.get("name")}] stdout: {out.strip()}")
            if err.strip():
                self.logger.warning(f"[{host.get("name")}] stderr: {err.strip()}")

        # Failure handling
        rules = host["exit_codes"].get(step)
        if rules:
            status = self._check_exit_code(host.get("name"), step, exit_code, rules)
            if self.logger:
                self.logger.debug(f"[{host.get("name")}] {step} status={status}")
        else:
            # Default behavior
            raise RuntimeError(
                f"Host '{host.get("name")}' step '{step}' failed with exit code {exit_code}"
            )

    def _check_exit_code(self, host_name, step, exit_code, rules):
        """
        rules = {
            "success": [...],
            "up_to_date": [...],
            "patches_available": [...],
            "error": ["*"]
        }
        """
        # Wildcard error rule
        if "error" in rules and "*" in rules["error"]:
            # If exit code is explicitly listed in any non-error category → OK
            for category, values in rules.items():
                if category == "error":
                    continue
                if exit_code in values:
                    return category  # e.g., "patches_available"

            # Otherwise → error
            raise RuntimeError(
                f"Host '{host_name}' step '{step}' failed with exit code {exit_code}"
            )

        # No wildcard → strict matching
        for category, values in rules.items():
            if exit_code in values:
                return category

        raise RuntimeError(
            f"Host '{host_name}' step '{step}' failed with exit code {exit_code}"
        )
