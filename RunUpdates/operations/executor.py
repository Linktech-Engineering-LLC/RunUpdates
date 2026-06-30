# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-06-30
 File: RunUpdates/operations/executor.py
 Version: 1.1.0
 Description: Executes update commands on a host using a session object.
"""

# System Libraries
import json
from typing import Optional
from datetime import datetime

# Project Libraries
from PythonTools.net.tools import sudo_run
from PythonTools.sessions.systemd_runner import SystemdRunner

from PythonTools.system.events.lifecycle import record_event
from PythonTools.system.systemd.normalize import normalize_systemd_result

from PythonTools.system.updates.detection import detect_update_outcome
from PythonTools.system.updates.repo_health import detect_repo_health
from PythonTools.system.updates.parsers import Parser, parse_check_output

from PythonTools.utils.exitcodes import ExitCodeClassifier


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
            "distro": host.get("distro"),
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
            if step == "refresh":
                continue

            # Record exit code + outputs
            if rc is not None:
                exit_code = rc.get("exit_code")
                host_summary["exit_codes"][step] = exit_code
                host_summary["outputs"][step] = {
                    "stdout": rc.get("output", ""),
                    "stderr": rc.get("stderr", ""),
                }

                # Step-specific exit-code config
                exit_cfg = host.get("exit_codes", {}).get(step, {})
                classifier = ExitCodeClassifier(exit_cfg)

                if exit_code is None or not isinstance(exit_code, int):
                    exit_code = -1

                status = classifier.classify(exit_code)

                record_event(
                    host_summary,
                    {
                        "step": step,
                        "exit_code": exit_code,
                        "status": status,
                    },
                    logger=self.logger
                )

            # -----------------------------
            # CHECK STEP
            # -----------------------------
            if step == "check":
                action = self._handle_check_step(rc, host_summary, name)
                skip_updates = action == "skip_updates"
                continue

            # -----------------------------
            # LIST STEP
            # -----------------------------
            if step == "list":
                action = self._handle_list_step(rc, host_summary, name)
                skip_updates = action == "skip_updates"
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
            step_result = normalize_systemd_result(result)

            exit_cfg = host.get("exit_codes", {}).get(step, {})
            classifier = ExitCodeClassifier(exit_cfg)

            exit_code = step_result.get("exit_code")
            if exit_code is None or not isinstance(exit_code, int):
                exit_code = -1

            step_result["status"] = classifier.classify(exit_code)
            return step_result

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

        # Repo health detection
        repo_broken = detect_repo_health(err)

        if step == "check" and repo_broken:
            return {
                "status": "repo_broken",
                "exit_code": exit_code,
                "output": out,
                "parsed": None,
                "repo_broken": True,
                "repo_status": "broken",
            }

        # Exit-code handling
        rules = host.get("exit_codes", {}).get(step)
        classifier = ExitCodeClassifier(rules)

        if rules:
            status = classifier.classify(exit_code)
        else:
            if exit_code != 0:
                raise RuntimeError(f"[{name}] Step '{step}' failed with exit code {exit_code}")
            status = "success"

        # Parsing (check step only)
        parsed = None
        if step == "check":
            distro = host.get("distro") or host.get("family")
            parsed = Parser.parse(distro, step, out) or {}

            status = "up_to_date"

            if parsed.get("summary") or parsed.get("upgradable"):
                status = "updates_available"

            if parsed.get("upgraded"):
                status = "updates_applied"

            if parsed.get("reboot_required"):
                status = "reboot_required"

        return {
            "status": status,
            "exit_code": exit_code,
            "output": out,
            "parsed": parsed,
            "repo_broken": repo_broken if step == "check" else False,
            "repo_status": "broken" if repo_broken else "healthy",
        }

    def _handle_check_step(self, rc, host_summary, name):
        if rc is None:
            return "continue"

        if rc.get("repo_broken"):
            if not self.force:
                host_summary["update_status"] = "skipped"
                return "skip_updates"
            return "continue"

        status = rc.get("status")

        if status == "up_to_date":
            return "skip_updates"

        if status in ("patches_available", "updates_available"):
            return "continue"

        raise RuntimeError(f"[{name}] Unexpected check status: {status}")

    def _handle_list_step(self, rc, host_summary, name):
        distro = host_summary.get("distro")

        check_out = host_summary["outputs"].get("check", {}).get("stdout", "") or ""
        list_out = rc.get("output", "") if rc else ""

        merged = f"{check_out}\n{list_out}"
        host_summary["outputs"]["check_list_merged"] = merged

        updates_exist = parse_check_output(merged, distro)

        if not updates_exist:
            return "skip_updates"

        return "continue"

    def _handle_update_step(self, rc, host_summary):
        exit_code = rc.get("exit_code", -1)
        stdout = rc.get("output", "")
        stderr = rc.get("stderr", "")

        outcome = detect_update_outcome(exit_code, stdout, stderr)

        host_summary["update_status"] = outcome["status"]
        host_summary["updates_applied"] = outcome["updates_applied"]
        host_summary["update_severity"] = outcome["severity"]

        if "error" in outcome:
            host_summary["update_error"] = outcome["error"]

        if host_summary["lifecycle_events"]:
            last_event = host_summary["lifecycle_events"][-1]
            if last_event["step"] == "update":
                last_event["status"] = outcome["status"]
                last_event["updates_applied"] = outcome["updates_applied"]
                last_event["severity"] = outcome["severity"]
                if "error" in outcome:
                    last_event["error"] = outcome["error"]

        if outcome["severity"] == "error":
            host_summary["lifecycle_status"] = "failed"
        elif outcome["severity"] == "warning":
            host_summary["lifecycle_status"] = "completed_with_warnings"
        else:
            host_summary["lifecycle_status"] = "completed"

        return "continue"

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

            reboot_rc = self._run_step(session, host, boot, bcmd)

            if reboot_rc is not None:
                exit_code = reboot_rc.get("exit_code")
                exit_cfg = host.get("exit_codes", {}).get("reboot_now", {})
                classifier = ExitCodeClassifier(exit_cfg)

                if exit_code is None or not isinstance(exit_code, int):
                    exit_code = -1

                reboot_status = classifier.classify(exit_code)

                record_event(
                    host_summary,
                    {
                        "step": "reboot_now",
                        "exit_code": exit_code,
                        "status": reboot_status,
                    },
                    logger=self.logger
                )

            host_summary["reboot_status"] = status

    def _finalize_summary(self, host_summary):
        end = datetime.now()
        host_summary["timestamps"]["completed"] = end.isoformat(timespec="seconds")
        start = datetime.fromisoformat(host_summary["timestamps"]["started"])
        host_summary["timestamps"]["duration_seconds"] = (end - start).seconds

        if host_summary["lifecycle_status"] == "in_progress":
            host_summary["lifecycle_status"] = "completed"

        update_event = next((e for e in host_summary["lifecycle_events"] if e["step"] == "update"), None)
        if update_event:
            host_summary["update_status"] = update_event["status"]

        if any(e["status"] == "error" for e in host_summary["lifecycle_events"]):
            host_summary["lifecycle_status"] = "failed"
        else:
            host_summary["lifecycle_status"] = "completed"

    def _write_summary(self, host_summary, name):
        summary_path = self.paths.SUMMARY_HOST_DIR / f"{name}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        if self.logger:
            self.logger.info(f"Writing summary to: {summary_path}")

        with open(summary_path, "w") as f:
            json.dump(host_summary, f, indent=2)
