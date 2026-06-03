# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-05-31
 File: RunUpdates/operations/orchestrator.py
 Version: 1.0.0
 Description: High-level coordinator for the RunUpdates execution pipeline.
"""
# System Libraries
from datetime import datetime
import json

# Project Libraries
from .selector import HostSelector
from .connector import HostConnector
from .executor import HostExecutor

class UpdateOrchestrator:
    """
    Coordinates:
      - InventoryProcessor (provided externally)
      - HostSelector (CLI filtering only)
      - HostConnector
      - HostExecutor
      - Shared execution tools from PythonTools
    """

    def __init__(self, context, hosts, logger=None):
        self.context = context
        self.args = context["args"]
        self.secrets = context.get("secrets",{})
        self.hosts = hosts
        self.logger = logger
        self.paths = context["paths"]
        self.mode = getattr(self.args, "mode", "sequential")

        self.selector = HostSelector(self.args, logger=logger)
        self.connector = HostConnector(self.secrets, logger=logger)
        self.executor = HostExecutor(
            context=self.context,
            logger=logger,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self):
        if self.logger:
            self.logger.info("=== Starting RunUpdates Orchestration ===")

        match self.mode:
            case "sequential":
                self._run_sequential()
            case "parallel":
                self._run_parallel()
            case "distro-parallel":
                self._run_distro_parallel()
            case _:
                raise NotImplementedError(f"Mode '{self.mode}' not implemented yet")
        if self.logger:
            self.logger.info("=== RunUpdates Orchestration Complete ===")

    def _run_parallel(self):
        raise NotImplementedError("Parallel execution not implemented yet")
    def _run_distro_parallel(self):
        raise NotImplementedError("Parallel execution not implemented yet")

    def _run_sequential(self):
        host_summaries = []   # NEW: collect per-host summaries

        for host in self.hosts:
            name = host["name"]

            # 2a. CLI-based selection filter
            if not self.selector.should_process(host):
                continue

            # 2b. Connect
            try:
                session = self.connector.connect(host)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{name}] Connection failed: {e}")
                continue

            # NEW: handle boolean/None returns
            if not session:
                if self.logger:
                    self.logger.error(f"[{name}] Connection failed: no SSH session returned")
                continue

            # 2c. Execute update lifecycle
            try:
                summary = self.executor.run_updates(host, session)   # NEW: capture summary
                host_summaries.append(summary)                       # NEW: store it
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{name}] Update failed: {e}")
            finally:
                if hasattr(session, "close"):
                    session.close()

        # NEW: aggregate and write final summary
        final_summary = self.aggregate_run_summary(host_summaries)
        self.write_final_summary(final_summary)

        if self.logger:
            self.logger.info("=== RunUpdates Orchestration Complete ===")

    def aggregate_run_summary(self, host_summaries: list[dict]) -> dict:
        run_start = min(
            datetime.fromisoformat(h["timestamps"]["started"])
            for h in host_summaries
        )
        run_end = max(
            datetime.fromisoformat(h["timestamps"]["completed"])
            for h in host_summaries
        )

        totals = {
            "hosts_total": len(host_summaries),
            "hosts_completed": 0,
            "hosts_failed": 0,
            "hosts_skipped": 0,
            "repo_broken": 0,
            "updates_applied": 0,
            "up_to_date": 0,
            "reboot_required": 0,
        }

        host_states = {}

        for h in host_summaries:
            state = h["lifecycle_status"]
            host_states[h["host"]] = state

            if state == "completed":
                totals["hosts_completed"] += 1
            elif state == "failed":
                totals["hosts_failed"] += 1
            elif state == "skipped":
                totals["hosts_skipped"] += 1

            # Repo health
            if h.get("repo_status") == "broken":
                totals["repo_broken"] += 1

            # Update status
            if h.get("update_status") == "updates_applied":
                totals["updates_applied"] += 1
            if h.get("update_status") == "up_to_date":
                totals["up_to_date"] += 1

            # Reboot
            if h.get("reboot_status") in ("reboot_required", "reboot_and_restart"):
                totals["reboot_required"] += 1

        return {
            "run_started": run_start.isoformat(timespec="seconds"),
            "run_completed": run_end.isoformat(timespec="seconds"),
            "duration_seconds": int((run_end - run_start).total_seconds()),
            "totals": totals,
            "hosts": host_states,
        }

    def write_final_summary(self, final_summary: dict):
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        summary_path = self.paths.SUMMARY_RUN_DIR / f"final-{timestamp}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)  
        with open(summary_path, "w") as f:
            json.dump(final_summary, f, indent=2)
        latest_link = self.paths.SUMMARY_RUN_DIR / "latest.json"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(summary_path.name)
