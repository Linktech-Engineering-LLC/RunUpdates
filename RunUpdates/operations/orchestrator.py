# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-18
 File: RunUpdates/operations/orchestrator.py
 Version: 1.0.0
 Description: High-level coordinator for the RunUpdates execution pipeline.
"""
# System Libraries
from typing import List

from .selector import HostSelector
from .connector import HostConnector
from .executor import HostExecutor


class UpdateOrchestrator:
    """
    Coordinates:
      - InventoryProcessor (provided externally)
      - HostSelector
      - HostConnector
      - HostExecutor

    This class does not perform any update logic itself.
    It simply orchestrates the flow.
    """

    def __init__(self, args, inventory_processor, secrets, logger=None):
        """
        :param args: Parsed CLI arguments
        :param inventory_processor: InventoryProcessor instance (already loaded)
        :param secrets: Vault-loaded secrets
        :param logger: Optional logger
        """
        self.args = args
        self.proc = inventory_processor
        self.secrets = secrets
        self.logger = logger

        # Subsystems
        self.selector = HostSelector(args, logger=logger)
        self.connector = HostConnector(secrets, logger=logger)
        self.executor = HostExecutor(logger=logger, dry_run=args.dry_run)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self):
        """
        Main orchestration entrypoint.
        """

        if self.logger:
            self.logger.info("=== Starting RunUpdates Orchestration ===")

        # 1. Flatten inventory for the selected family/distro
        hosts: List[dict] = self.proc.flatten(
            family=self.args.family,
            distro=self.args.distro,
        )

        if self.logger:
            self.logger.debug(f"Flattened {len(hosts)} hosts for processing")

        # 2. Iterate hosts
        for host in hosts:
            name = host["name"]

            # 2a. Selection filter
            if not self.selector.should_process(host):
                continue

            # 2b. Connect
            try:
                session = self.connector.connect(host)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{name}] Connection failed: {e}")
                continue

            # 2c. Execute update lifecycle
            try:
                self.executor.run_updates(host, session)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{name}] Update failed: {e}")
            finally:
                # Always close remote sessions
                if hasattr(session, "close"):
                    session.close()

        if self.logger:
            self.logger.info("=== RunUpdates Orchestration Complete ===")
