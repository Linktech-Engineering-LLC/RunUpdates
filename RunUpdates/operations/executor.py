# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-28
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
    def run_updates(self, host: dict, session) -> None:
        name = host["name"]
        cmds = host.get("commands", {})
        exit_map = host.get("exit_codes", {})

        if self.logger:
            self.logger.info(f"=== Running updates for {name} ===")

        # Ordered lifecycle steps
        lifecycle = ["check", "refresh", "update", "clean", "reboot"]
        skip_updates = False

        for step in lifecycle:
            command = cmds.get(step)
            if not command:
                continue

            # Skip update steps if up-to-date
            if skip_updates and step in ("refresh", "update", "clean"):
                continue

            status = self._run_step(session, host, step, command)

            # --- Decision logic ---
            if step == "check":
                if status == "up_to_date":
                    if self.logger:
                        self.logger.info(f"[{name}] System is up-to-date. Skipping update steps.")
                    skip_updates = True
                    continue

                elif status in ("patches_available", "updates_available"):
                    if self.logger:
                        self.logger.info(f"[{name}] Updates available. Continuing lifecycle.")
                    continue

                else:
                    raise RuntimeError(f"[{name}] Unexpected check status: {status}")

            # Reboot logic
            if step == "reboot":
                if status == "no_reboot":
                    if self.logger:
                        self.logger.info(f"[{name}] No reboot required, skipping")
                    continue

                if status in ("reboot_required", "restart_services", "reboot_and_restart"):
                    if self.logger:
                        self.logger.info(f"[{name}] Rebooting host due to status: {status}")
                    session.run("reboot_now")
                    continue

            # refresh: success/error handled inside _run_step
            if step == "refresh":
                continue
        if self.logger:
            self.logger.info(f"=== Completed updates for {name} ===")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run_step(self, session, host: dict, step: str, command: Optional[str]):
        """
        Execute a single step in the update lifecycle.
        """

        name = host.get("name")

        if not command:
            if self.logger:
                self.logger.debug(f"[{name}] Skipping '{step}' (no command)")
            return

        if self.dry_run:
            if self.logger:
                self.logger.info(f"[{name}] DRY-RUN: {step}: {command}")
            return

        if self.logger:
            self.logger.info(f"[{name}] {step}: {command}")

        # Local execution path
        if session == "local":
            rc = sudo_run(
                cmd=command,
                sudo_password=self.secrets.get("sudo_pass", "")
            )
            exit_code, out, err = rc.as_tuple
        else:
            result = session.run(command)
            out, exit_code, err = result.as_tuple

        # Logging
        if self.logger:
            self.logger.debug(f"[{name}] {step} exit={exit_code}")
            if out.strip():
                self.logger.debug(f"[{name}] stdout: {out.strip()}")
            if err.strip():
                self.logger.warning(f"[{name}] stderr: {err.strip()}")

        # Exit-code handling
        rules = host.get("exit_codes", {}).get(step)

        if rules:
            # Special handling (check, refresh, etc.)
            status = self._check_exit_code(host.get("name"), step, exit_code, rules)
            if self.logger:
                self.logger.debug(f"[{host.get('name')}] {step} status={status}")
            return status

        # Default behavior for steps without exit-code rules
        if exit_code != 0:
            raise RuntimeError(
                f"[{host.get('name')}] Step '{step}' failed with exit code {exit_code}"
            )

        return "success"

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
