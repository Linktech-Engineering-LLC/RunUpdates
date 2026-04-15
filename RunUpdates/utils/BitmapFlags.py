# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-04-13
 File: RunUpdates/utils/BitmapFlags.py
 Version: 1.0.0
 Description: Bitmap flag container for RunUpdates parser
"""


class BitmapFlags:
    """
    BitmapFlags for RunUpdates.
    Stores boolean or bitwise flags representing CLI options.
    """

    def __init__(self):
        # Example flags — real ones will be added later
        self.DRY_RUN = False
        self.VERBOSE = False
        self.FORCE = False
        self.SPECIFIC_DISTRO = None

    def __repr__(self):
        return (
            f"<BitmapFlags dry_run={self.DRY_RUN} "
            f"verbose={self.VERBOSE} force={self.FORCE}>"
        )
