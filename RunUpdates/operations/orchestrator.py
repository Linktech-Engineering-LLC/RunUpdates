# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-05-22
 File: RunUpdates/operations/orchestrator.py
 Version: 1.0.0
 Description: High-level coordinator for the RunUpdates execution pipeline.
"""
# System Libraries
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

    def __init__(self, args, secrets, hosts, logger=None):
        self.args = args
        self.secrets = secrets
        self.hosts = hosts
        self.logger = logger
        self.mode = args.mode

        self.selector = HostSelector(args, logger=logger)
        self.connector = HostConnector(secrets, logger=logger)
        self.executor = HostExecutor(
            secrets=self.secrets,
            logger=logger,
            dry_run=args.dry_run,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self):
        if self.logger:
            self.logger.info("=== Starting RunUpdates Orchestration ===")

        if self.mode == "sequential":
            self._run_sequential()
        else:
            raise NotImplementedError(f"Mode '{self.mode}' not implemented yet")

        if self.logger:
            self.logger.info("=== RunUpdates Orchestration Complete ===")

    def _run_sequential(self):
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
                self.executor.run_updates(host, session)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{name}] Update failed: {e}")
            finally:
                if hasattr(session, "close"):
                    session.close()

        if self.logger:
            self.logger.info("=== RunUpdates Orchestration Complete ===")
