# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-05-31
 File: RunUpdates/operations/executor.py
 Version: 1.0.0
 Description: Executes update commands on a host using a session object.
"""
# System Libraries
from typing import Optional
import json
from datetime import datetime
# Project Libraries
from PythonTools.net.tools import sudo_run
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

    def __init__(self, context, logger=None):
        self.context = context
        self.args = context["args"]
        self.paths = context["paths"]
        self.secrets = context.get("secrets", {})
        self.logger = logger
        self.dry_run = getattr(self.args, "dry_run", False)
        self.force = getattr(self.args, "force", False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_updates(self, host: dict, session) -> dict:
        name = host["name"]
        use_systemd = host.get("systemd", False)

        self.systemd = SystemdRunner(session, logger=self.logger, hostname=name) if use_systemd else None

        # -----------------------------
        # Initialize summary
        # -----------------------------
        host_summary = {
            "host": name,
            "lifecycle_status": "in_progress",
            "update_status": None,
            "repo_status": None,
            "reboot_status": None,
            "exit_codes": {},
            "parsed": None,
            "lifecycle_events": [],
            "outputs": {},
            "timestamps": {
                "started": datetime.now().isoformat(timespec="seconds"),
                "completed": None,
                "duration_seconds": None,
            },
        }

        if self.logger:
            self.logger.info(f"=== Running updates for {name} ===")

        lifecycle = host.get("lifecycle", [])
        cmds = host.get("commands", {})
        skip_updates = False

        # -----------------------------
        # Lifecycle loop
        # -----------------------------
        for step in lifecycle:
            command = cmds.get(step)
            if not command:
                continue

            # Skip update step if flagged
            if skip_updates and step == "update":
                continue

            # Run the step
            rc = self._run_step(session, host, step, command)

            # Record exit code + outputs
            if rc is not None:
                host_summary["exit_codes"][step] = rc.get("exit_code")
                host_summary["outputs"][step] = {
                    "stdout": rc.get("output", ""),
                    "stderr": rc.get("stderr", ""),
                }

            # -----------------------------
            # CHECK STEP
            # -----------------------------
            if step == "check":
                action = self._handle_check_step(rc, host_summary, name)

                if action == "skip_updates":
                    skip_updates = True
                continue

            # -----------------------------
            # UPDATE STEP
            # -----------------------------
            if step == "update":
                if skip_updates:
                    continue
                self._handle_update_step(rc, host_summary)
                continue

            # -----------------------------
            # REBOOT STEP
            # -----------------------------
            if step == "reboot":
                self._handle_reboot_step(rc, host, cmds, session, name, host_summary)
                continue

            # refresh/clean/etc. naturally continue
            continue

        # -----------------------------
        # Finalize summary
        # -----------------------------
        self._finalize_summary(host_summary)

        # -----------------------------
        # Write summary file
        # -----------------------------
        self._write_summary(host_summary, name)

        if self.logger:
            self.logger.info(f"=== Completed updates for {name} ===")
            
        return host_summary

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
        # Repo health detection (only during 'check' step)
        # ------------------------------------------------------
        repo_broken = False
        if step == "check" and err:
            REPO_FAILURE_PATTERNS = (
                "Failed to download metadata",
                "Cannot download repomd.xml",
                "All mirrors were tried",
                "Status code: 404",
                "repodata/repomd.xml",
                "No such file or directory: repodata",
                "Error: repomd.xml",
                "Cannot prepare internal mirrorlist",
                "No URLs in mirrorlist",
                "There are no enabled repositories",   # NEW
            )

            lowered = err.lower()
            if any(p.lower() in lowered for p in REPO_FAILURE_PATTERNS):
                repo_broken = True
                if self.logger:
                    self.logger.lifecycle(
                        "REPO_HEALTH_FAIL",
                        f"[{name}] Repository metadata appears broken"
                    )

        # Define repo_status AFTER repo_broken is known
        repo_status = "broken" if repo_broken else "healthy"
        # If the repository is broken, skip exit-code handling entirely
        if step == "check" and repo_broken:
            if self.logger:
                self.logger.debug(f"[{name}] Skipping exit-code rules due to broken repo")
            return {
                "status": "repo_broken",
                "exit_code": exit_code,
                "output": out,
                "parsed": None,
                "repo_broken": True,
                "repo_status": "broken",
            }

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
            "parsed": parsed if step == "check" else None,
            "repo_broken": repo_broken if step == "check" else False,
            "repo_status": repo_status if step == "check" else None,
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

    def _record_event(self, summary: dict, event: str):
        summary["lifecycle_events"].append(event)
        if self.logger:
            self.logger.lifecycle(event)

    def _handle_check_step(self, rc, host_summary, name):
        if rc is None:
            return "continue"

        host_summary["repo_status"] = rc.get("repo_status")

        if rc.get("repo_broken"):
            self._record_event(host_summary, "REPO_HEALTH_FAIL")
            if not self.force:
                self._record_event(host_summary, "SKIP_REPO_BROKEN")
                host_summary["update_status"] = "skipped"
                host_summary["lifecycle_status"] = "skipped"
                return "skip_updates"
            else:
                self._record_event(host_summary, "FORCE_CONTINUE_REPO_BROKEN")

        status = rc.get("status")

        if status == "up_to_date":
            host_summary["update_status"] = "up_to_date"
            host_summary["lifecycle_status"] = "completed"
            self._record_event(host_summary, "UP_TO_DATE")
            return "skip_updates"

        if status in ("patches_available", "updates_available"):
            host_summary["update_status"] = status
            self._record_event(host_summary, "UPDATES_AVAILABLE")
            return "continue"

        raise RuntimeError(f"[{name}] Unexpected check status: {status}")

    def _handle_update_step(self, rc, host_summary):
        if rc and rc.get("exit_code") == 0:
            host_summary["update_status"] = "updates_applied"
            self._record_event(host_summary, "UPDATES_APPLIED")
        else:
            host_summary["update_status"] = "failed"
            host_summary["lifecycle_status"] = "failed"
            self._record_event(host_summary, "UPDATE_FAILED")

    def _handle_reboot_step(self, rc, host, cmds, session, name, host_summary):
        status = rc.get("status") if rc else None

        if status == "no_reboot":
            if self.logger:
                self.logger.info(f"[{name}] No reboot required, skipping")
            return

        if status in ("reboot_required", "restart_services", "reboot_and_restart"):
            if self.logger:
                self.logger.info(f"[{name}] Rebooting host due to status: {status}")
            boot = "reboot_now"
            bcmd = cmds.get(boot)
            self._run_step(session, host, boot, bcmd)
            host_summary["reboot_status"] = status

    def _finalize_summary(self, host_summary):
        end = datetime.now()
        host_summary["timestamps"]["completed"] = end.isoformat(timespec="seconds")
        start = datetime.fromisoformat(host_summary["timestamps"]["started"])
        host_summary["timestamps"]["duration_seconds"] = (end - start).seconds

        if host_summary["lifecycle_status"] == "in_progress":
            host_summary["lifecycle_status"] = "completed"

    def _write_summary(self, host_summary, name):
        summary_path = self.paths.SUMMARY_HOST_DIR / f"{name}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        if self.logger:
            self.logger.info(f"Writing summary to: {summary_path}")
        with open(summary_path, "w") as f:
            json.dump(host_summary, f, indent=2)
