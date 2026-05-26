# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-05-26
 File: RunUpdates/operations/executor.py
 Version: 1.0.0
 Description: Executes update commands on a host using a session object.
"""
# System Libraries
from typing import Optional
# Project Libraries
from PythonTools.net.tools import sudo_run
from PythonTools.sessions.ssh_sessions import SSHSession
from PythonTools.sessions.systemd_runner import SystemdRunner
from PythonTools.utils.common import classify_exit_code
from PythonTools.utils.parsers import Parser
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
        use_systemd = host.get("systemd", False)

        self.systemd = SystemdRunner(session, logger=self.logger, hostname=name) if use_systemd else None

        if self.logger:
            self.logger.info(f"=== Running updates for {name} ===")

        # Ordered lifecycle steps
        lifecycle = host.get("lifecycle", [])
        cmds = host.get("commands", {})
        skip_updates = False

        for step in lifecycle:
            command = cmds.get(step)
            if not command:
                continue

            # Skip update steps if up-to-date
            if skip_updates and step == "update":
                continue

            rc = self._run_step(session, host, step, command)
            status = rc.get("status") if rc is not None else None

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
                    boot = "reboot_now"
                    bcmd = cmds.get(boot)
                    status = self._run_step(session, host, boot, bcmd)
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

        # Systemd execution path
        if self.systemd and step == "update":
            result = self.systemd.run_and_wait(command, unit=f"runupdates-{name}")
            return self._map_systemd_result(result)

        # Local execution path
        if session == "local":
            rc = sudo_run(
                cmd=command,
                sudo_password=self.secrets.get("sudo_pass", "")
            )
            out, exit_code, err = rc.as_tuple
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

        # ------------------------------------------------------
        # Exit-code handling
        # ------------------------------------------------------
        rules = host.get("exit_codes", {}).get(step)

        if rules:
            status = classify_exit_code(step, exit_code, rules, name)
        else:
            if exit_code != 0:
                raise RuntimeError(
                    f"[{name}] Step '{step}' failed with exit code {exit_code}"
                )
            status = "success"

        # ------------------------------------------------------
        # ADD PARSING HERE
        # ------------------------------------------------------
        if step == "check":
            distro = host.get("distro") or host.get("family")
            parsed = Parser.parse(distro, step, out) or {}

            # Default
            status = "up_to_date"

            # summary or upgradable means updates available
            if parsed.get("summary") or parsed.get("upgradable"):
                status = "updates_available"

            # Debian update step never returns "upgraded", but keep for other distros
            if parsed.get("upgraded"):
                status = "updates_applied"

            if parsed.get("reboot_required"):
                status = "reboot_required"

        # ------------------------------------------------------
        # Return structured result
        # ------------------------------------------------------
        return {
            "status": status,
            "exit_code": exit_code,
            "output": out,
            "parsed": parsed if step == "check" else None
        }

    def _map_systemd_result(self, result) -> dict:
        """
        Normalize systemd-run result (SimpleNamespace or dict) into the standard
        command result format used by RunUpdates.
        """

        # Helper to support both dict and SimpleNamespace
        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        mapped = {
            # Core fields
            "exit_code": _get(result, "exit_code", 1),
            "stdout": _get(result, "stdout", ""),
            "stderr": _get(result, "stderr", ""),

            # Systemd-specific fields
            "unit": _get(result, "unit", None),
            "systemd_state": _get(result, "state", "unknown"),   # systemd Result=
            "success": _get(result, "success", None),

            # Optional extended metadata
            "start_time": _get(result, "start_time", None),
            "end_time": _get(result, "end_time", None),
            "duration": _get(result, "duration", None),
        }

        # Derive a normalized status for RunUpdates
        # systemd Result=success AND exit_code=0 → success
        if mapped["exit_code"] == 0 and mapped["systemd_state"] == "success":
            mapped["status"] = "success"
        else:
            mapped["status"] = "failed"

        return mapped
