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
import json
import re
from typing import Optional
from datetime import datetime
from typing import Dict, Any
# Project Libraries
from PythonTools.net.tools import sudo_run
from PythonTools.sessions.systemd_runner import SystemdRunner
from PythonTools.utils.exitcodes import ExitCodeClassifier
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
                host_summary["exit_codes"][step] = rc.get("exit_code")
                host_summary["outputs"][step] = {
                    "stdout": rc.get("output", ""),
                    "stderr": rc.get("stderr", ""),
                }
                # NEW: classify exit code using YAML
                exit_code = rc.get("exit_code")
                # Step-specific exit-code config
                exit_cfg = host.get("exit_codes", {}).get(step, {})                # Normalize None or non-int values
                classifier = ExitCodeClassifier(exit_cfg)
                if exit_code is None or not isinstance(exit_code, int):
                    exit_code = -1   # or any sentinel you prefer
    
                status = classifier.classify(exit_code)
                host_summary["lifecycle_events"].append({
                    "step": step,
                    "exit_code": exit_code,
                    "status": status,
                })

            # -----------------------------
            # CHECK STEP
            # -----------------------------
            if step == "check":
                action = self._handle_check_step(rc, host_summary, name)

                skip_updates = action == "skip_updates"
                continue

            if step == "list":
                # treat list as part of check phase
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

    def _detect_distro(self, lines, output):
        # openSUSE
        for line in lines:
            lower = line.lower()
            if re.match(r"^[vui]\s+\|", lower):
                return "opensuse"
            if "found" in lower and "patch" in lower:
                return "opensuse"
            if "0 patches needed" in lower or "no patches found" in lower:
                return "opensuse"
        if "Available Version" in output and "Current Version" in output:
            return "opensuse"

        # Debian/Ubuntu
        for line in lines:
            if line.startswith("Inst ") or "upgradable from" in line:
                return "debian"

        # RedHat/Fedora
        for line in lines:
            lower = line.lower()
            if "updates available" in lower:
                return "redhat"
            parts = line.split()
            if len(parts) >= 3 and any(char.isdigit() for char in parts[1]):
                return "redhat"

        # Arch
        for line in lines:
            if "->" in line:
                return "arch"

        # Alpine
        for line in lines:
            if "Upgrading" in line and "to" in line:
                return "alpine"

        # Flatpak
        if "Updates:" in output:
            return "flatpak"

        # Snap
        if "will be updated" in output:
            return "snap"

        return None

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
            step_result = self._map_systemd_result(result)

            # Step-specific exit-code config
            exit_cfg = host.get("exit_codes", {}).get(step, {})
            classifier = ExitCodeClassifier(exit_cfg)
            # Normalize exit code
            exit_code = step_result.get("exit_code")
            if exit_code is None or not isinstance(exit_code, int):
                exit_code = -1

            # Classify using YAML
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
        classifier = ExitCodeClassifier(rules)
        if rules:
            status = classifier.classify(exit_code)
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

        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        mapped = {
            "exit_code": _get(result, "exit_code", 1),
            "stdout": _get(result, "stdout", ""),
            "stderr": _get(result, "stderr", ""),
            "unit": _get(result, "unit", None),
            "systemd_state": _get(result, "state", "unknown"),
            "success": _get(result, "success", None),
            "start_time": _get(result, "start_time", None),
            "end_time": _get(result, "end_time", None),
            "duration": _get(result, "duration", None),
        }

        # IMPORTANT: Do NOT classify status here.
        # The orchestrator will classify using YAML rules.
        mapped["status"] = "unknown"

        return mapped

    def _record_event(self, summary: Dict[str, Any], event: Dict[str, Any]):
        summary["lifecycle_events"].append(event)
        if self.logger:
            self.logger.lifecycle(event)

    def _handle_check_step(self, rc, host_summary, name):
        if rc is None:
            return "continue"

        # Repo health
        if rc.get("repo_broken"):
            if not self.force:
                host_summary["update_status"] = "skipped"
                return "skip_updates"
            return "continue"

        status = rc.get("status")

        # Up-to-date → skip update step
        if status == "up_to_date":
            return "skip_updates"

        # Updates available → continue lifecycle
        if status in ("patches_available", "updates_available"):
            return "continue"

        raise RuntimeError(f"[{name}] Unexpected check status: {status}")

    def _handle_list_step(self, rc, host_summary, name):
        distro = host_summary.get("distro")

        # Safe retrieval of check output
        check_out = host_summary["outputs"].get("check", {}).get("stdout", "") or ""

        # Safe retrieval of list output
        list_out = rc.get("output", "") if rc else ""

        # Merge safely
        merged = f"{check_out}\n{list_out}"

        # Store merged output for debugging
        host_summary["outputs"]["check_list_merged"] = merged

        # Parse
        updates_exist = self._parse_check_output(merged, distro)

        if not updates_exist:
            return "skip_updates"

        return "continue"

    def _handle_update_step(self, rc, host_summary):
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

            # Record reboot_now event
            if reboot_rc is not None:
                exit_code = reboot_rc.get("exit_code")
                exit_cfg = host.get("exit_codes", {}).get("reboot_now", {})
                classifier = ExitCodeClassifier(exit_cfg)
                if exit_code is None or not isinstance(exit_code, int):
                    exit_code = -1

                reboot_status = classifier.classify(exit_code)

                host_summary["lifecycle_events"].append({
                    "step": "reboot_now",
                    "exit_code": exit_code,
                    "status": reboot_status,
                })

            host_summary["reboot_status"] = status

    def _finalize_summary(self, host_summary):
        end = datetime.now()
        host_summary["timestamps"]["completed"] = end.isoformat(timespec="seconds")
        start = datetime.fromisoformat(host_summary["timestamps"]["started"])
        host_summary["timestamps"]["duration_seconds"] = (end - start).seconds

        if host_summary["lifecycle_status"] == "in_progress":
            host_summary["lifecycle_status"] = "completed"

        # Determine update_status from classifier
        update_event = next((e for e in host_summary["lifecycle_events"] if e["step"] == "update"), None)
        if update_event:
            host_summary["update_status"] = update_event["status"]

        # Determine lifecycle_status from classifier categories
        if any(e["status"] == "error" for e in host_summary["lifecycle_events"]):
            host_summary["lifecycle_status"] = "failed"
        else:
            host_summary["lifecycle_status"] = "completed"
            

    def _parse_check_output(self, output: str, distro: str) -> bool:
        if not output:
            return False

        distro = (distro or "").lower()
        lines = [line.strip() for line in output.splitlines() if line.strip()]

        if not distro:
            auto = self._detect_distro(lines, output)
            if auto:
                distro = auto
                if self.logger:
                    self.logger.debug(f"Distro autodetected as {auto}")
            else:
                if self.logger:
                    self.logger.debug("Distro autodetection failed; using fallback")

        match distro:
            case "opensuse":
                return self._parse_opensuse(lines, output)

            case "debian":
                return self._parse_debian(lines)

            case "redhat":
                return self._parse_redhat(lines)

            case "arch":
                return self._parse_arch(lines)

            case "alpine":
                return self._parse_alpine(lines)

            case "flatpak":
                return self._parse_flatpak(output)

            case "snap":
                return self._parse_snap(output)

            case _:
                return self._parse_fallback(lines)

    def _parse_opensuse(self, lines, output):
        updates_found = False

        for line in lines:
            lower = line.lower()

            # Patches available
            if "found" in lower and "patch" in lower:
                updates_found = True
                break

            # Updates available (compact mode)
            if re.match(r"^[vui]\s+\|", lower):
                updates_found = True
                break

        if updates_found:
            return True

        # Explicit no patches
        for line in lines:
            lower = line.lower()
            if (
                "no patches found" in lower
                or "0 patches needed" in lower
                or "nothing to do" in lower
            ):
                return False

        # Table mode
        if "Available Version" in output and "Current Version" in output:
            for line in lines:
                if "|" in line and not line.startswith(("Repository", "Name", "Arch")):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        if parts[2] != parts[3]:
                            return True

        return False
    def _parse_debian(self, lines):
        for line in lines:
            # apt-get -s upgrade
            if line.startswith("Inst "):
                return True

            # apt list --upgradable
            if "upgradable from" in line:
                return True

        return False
    def _parse_redhat(self, lines):
        for line in lines:
            lower = line.lower()

            # dnf check-update summary
            if "updates available" in lower:
                return True

            # Table rows: pkg version repo
            parts = line.split()
            if len(parts) >= 3 and not line.startswith("Last metadata"):
                # Version-like token in column 2
                if any(char.isdigit() for char in parts[1]):
                    return True

        return False
    def _parse_arch(self, lines):
        for line in lines:
            # pacman -Qu format: pkgname version -> newversion
            if "->" in line:
                return True

        return False
    def _parse_alpine(self, lines):
        for line in lines:
            # apk upgrade -s format: Upgrading pkg to version
            if "Upgrading" in line and "to" in line:
                return True

        return False
    def _parse_flatpak(self, output):
        # Flatpak prints "Updates:" when updates exist
        if "Updates:" in output:
            return True
        return False
    def _parse_snap(self, output):
        # Snap prints "will be updated" when updates exist
        if "will be updated" in output:
            return True
        return False
    def _parse_fallback(self, lines):
        for line in lines:
            tokens = line.split()

            # Look for version-like tokens
            if any(token.isdigit() for token in tokens):
                # Look for update-related keywords
                lower = line.lower()
                if any(keyword in lower for keyword in ["update", "upgrade", "upgradable"]):
                    return True

        return False


    def _write_summary(self, host_summary, name):
        summary_path = self.paths.SUMMARY_HOST_DIR / f"{name}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        if self.logger:
            self.logger.info(f"Writing summary to: {summary_path}")
        with open(summary_path, "w") as f:
            json.dump(host_summary, f, indent=2)
