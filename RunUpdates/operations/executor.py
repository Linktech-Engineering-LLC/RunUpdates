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
# Project5 Libraries
from PythonTools.net_tools import sudo_run

class HostExecutor:
    """
    Executes update commands on a host using a session object.
    Session must expose:
        run(command: str) -> (exit_code, stdout, stderr)
    """

    def __init__(self, secrets: dict, logger=None, dry_run: bool = False):
        self.secrets = secrets
        self.logger = logger
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_updates(self, host: dict, session) -> None:
        """
        Execute the update lifecycle for a host.

        Host dict fields (from InventoryProcessor.flatten()):
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

        # 1. check
        self._run_step(session, name, "check", cmds.get("check"))

        # 2. refresh
        self._run_step(session, name, "refresh", cmds.get("refresh"))

        # 3. update
        self._run_step(session, name, "update", cmds.get("update"))

        # 4. clean
        self._run_step(session, name, "clean", cmds.get("clean"))

        # 5. reboot (optional)
        reboot_cmd = cmds.get("reboot")
        if reboot_cmd:
            self._run_step(session, name, "reboot", reboot_cmd)

        if self.logger:
            self.logger.info(f"=== Completed updates for {name} ===")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run_step(self, session, host_name: str, step: str, command: Optional[str]):
        """
        Execute a single step in the update lifecycle.
        """

        if not command:
            if self.logger:
                self.logger.debug(f"[{host_name}] Skipping '{step}' (no command)")
            return

        if self.dry_run:
            if self.logger:
                self.logger.info(f"[{host_name}] DRY-RUN: {step}: {command}")
            return

        if self.logger:
            self.logger.info(f"[{host_name}] {step}: {command}")

        if session == "local":
            rc = sudo_run(cmd = command, sudo_password = self.secrets.get("sudo_pass",""))
            exit_code, out, err = rc.as_tuple
        else:
            exit_code, out, err = session.run(command)

        if self.logger:
            self.logger.debug(f"[{host_name}] {step} exit={exit_code}")
            if out.strip():
                self.logger.debug(f"[{host_name}] stdout: {out.strip()}")
            if err.strip():
                self.logger.warning(f"[{host_name}] stderr: {err.strip()}")

        if exit_code != 0:
            raise RuntimeError(
                f"Host '{host_name}' step '{step}' failed with exit code {exit_code}"
            )
