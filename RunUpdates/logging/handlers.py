# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-15
 File: RunUpdates/logging/handlers.py
 Version: 1.0.0
 Description: Description of this module
"""

# system imports
import os
import logging
import time
import tarfile
import zipfile
import glob
from logging.handlers import RotatingFileHandler


def get_project_logger():
    """
    Determine the project name from the module path and return its logger.
    Example:
        RunUpdates.logging.handlers -> RunUpdates.Logger
    """
    pkg = __package__  # e.g., "RunUpdates.logging"
    if pkg:
        project = pkg.split(".")[0]  # "RunUpdates"
    else:
        project = "DefaultProject"

    return logging.getLogger(f"{project}.Logger")


class ArchiveRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename: str, mode: str = "tgz", *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.archive_mode = mode

    def doRollover(self):
        super().doRollover()

        rotated_file = f"{self.baseFilename}.1"
        if os.path.exists(rotated_file):
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

            # Determine archive name
            if self.archive_mode == "tgz":
                archive_name = f"{self.baseFilename}.{timestamp}.tgz"
                with tarfile.open(archive_name, "w:gz") as tar:
                    tar.add(rotated_file, arcname=os.path.basename(rotated_file))

            elif self.archive_mode == "zip":
                archive_name = f"{self.baseFilename}.{timestamp}.zip"
                with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(rotated_file, arcname=os.path.basename(rotated_file))

            else:
                archive_name = rotated_file

            os.remove(rotated_file)

            # Enforce backup count
            ext = "tgz" if self.archive_mode == "tgz" else "zip"
            archives = sorted(
                glob.glob(f"{self.baseFilename}.*.{ext}"),
                key=os.path.getmtime,
            )

            if len(archives) > self.backupCount:
                for old_archive in archives[: -self.backupCount]:
                    os.remove(old_archive)

        # Reopen new log file
        self.stream = self._open()
