# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-19
 File: RunUpdates/operations/orchestrator.py
 Version: 1.0.0
 Description: High-level coordinator for the RunUpdates execution pipeline.
"""
# System Libraries
# Project Libraries
from PythonTools.net_tools import sudo_run, local_command
from .selector import HostSelector
from .connector import HostConnector
from .executor import HostExecutor
from ..ansible.config_loader import load_inventory

class UpdateOrchestrator:
    """
    Coordinates:
      - InventoryProcessor (provided externally)
      - HostSelector (CLI filtering only)
      - HostConnector
      - HostExecutor
      - Shared execution tools from PythonTools
    """

    def __init__(self, args, inventory_processor, secrets, inventory, logger=None):
        """
        :param args: Parsed CLI arguments
        :param inventory_processor: InventoryProcessor instance
        :param secrets: Vault-loaded secrets (contains sudo password)
        :param inventory: Parsed inventory dictionary
        :param logger: Optional logger
        """
        self.args = args
        self.proc = inventory_processor
        self.secrets = secrets
        self.inventory = inventory
        self.logger = logger

        # Subsystems
        self.selector = HostSelector(args, logger=logger)

        # Pass shared execution tools into connector/executor
        self.connector = HostConnector(
            secrets,
            logger=logger,
        )

        self.executor = HostExecutor(
            secrets=self.secrets,
            logger=logger,
            dry_run=args.dry_run,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self):
        """
        Main orchestration entrypoint.
        """

        if self.logger:
            self.logger.info("=== Starting RunUpdates Orchestration ===")

        # 1. Flatten inventory for the selected family/distro/host
        hosts = self.proc.flatten(
            inventory=self.inventory,
            family=self.args.family,
            distro=self.args.distro,
            host=self.args.host,
        )

        if self.logger:
            self.logger.debug(f"Flattened {len(hosts)} hosts for processing")

        # 2. Iterate hosts
        for host in hosts:
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
