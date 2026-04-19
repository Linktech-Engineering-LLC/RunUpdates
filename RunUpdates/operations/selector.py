# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-18
 Modified: 2026-04-19
 File: RunUpdates/operations/selector.py
 Version: 1.0.0
 Description: Determines whether a host should be processed
              based on CLI arguments and host metadata.
"""

class HostSelector:
    """
    Applies selection rules for host processing:
      - --host filter
      - family/distro already handled by InventoryProcessor
      - enabled already handled by InventoryProcessor
    """

    def __init__(self, args, logger=None):
        self.args = args
        self.logger = logger

    def should_process(self, host: dict) -> bool:
        """
        Determine whether this host should be processed.

        InventoryProcessor has already:
          - validated family/distro
          - validated required fields
          - filtered disabled hosts
        """

        # 1. --host filter (single-host mode)
        if self.args.host:
            if host["name"] != self.args.host:
                if self.logger:
                    self.logger.debug(
                        f"Skipping {host['name']} (does not match --host {self.args.host})"
                    )
                return False

        if self.logger:
            self.logger.debug(f"Selected host: {host['name']}")

        return True
