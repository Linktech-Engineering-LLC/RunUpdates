# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-18
 File: RunUpdates/operations/selector.py
 Version: 1.0.0
 Description: Determines whether a host should be processed
              based on CLI arguments and host metadata.
"""

class HostSelector:
    """
    Applies selection rules for host processing:
      - enabled flag
      - --host filter
      - family/distro already handled by InventoryProcessor
      - future: --force, --dry-run, --skip-disabled, etc.
    """

    def __init__(self, args, logger=None):
        """
        :param args: Parsed CLI arguments
        :param logger: Optional logger
        """
        self.args = args
        self.logger = logger

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------
    def should_process(self, host: dict) -> bool:
        """
        Determine whether this host should be processed.

        Host object fields (from InventoryProcessor.flatten()):
          - name
          - enabled
          - family
          - distro
          - address
          - port
          - commands
        """

        # 1. Enabled flag
        if not host.get("enabled", True):
            if self.logger:
                self.logger.debug(f"Skipping {host['name']} (disabled)")
            return False

        # 2. --host filter (single-host mode)
        if self.args.host:
            if host["name"] != self.args.host:
                if self.logger:
                    self.logger.debug(
                        f"Skipping {host['name']} (does not match --host {self.args.host})"
                    )
                return False

        # 3. Future: --force, --skip-disabled, etc.

        if self.logger:
            self.logger.debug(f"Selected host: {host['name']}")

        return True
