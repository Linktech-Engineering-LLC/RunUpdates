# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
Modified: 2026-04-14
 File: RunUpdates/logging/constants.py
 Version: 1.0.0
 Description: Lifecycle event constants for RunUpdates logging
"""

class LifecycleEvents:
    INIT = "INIT"                     # Program startup
    CONFIG_CHECK = "CONFIG_CHECK"     # Config file located / validated
    CONFIG_RESOLVED = "CONFIG_RESOLVED"  # Distro + update strategy resolved
    CMD_START = "CMD_START"           # Update command execution begins
    CMD_END = "CMD_END"               # Update command execution ends
    STATUS = "STATUS"                 # Status summary (success/failure)
    CLEANUP = "CLEANUP"               # Cleanup actions
    COMPLETE = "COMPLETE"             # End of run
    START_RUN = "START_RUN"           # High-level run start
    END_RUN = "END_RUN"               # High-level run end
    SKIP = "SKIP"                     # Skipped due to unsupported distro or config

LIFECYCLE_EVENTS = {
    LifecycleEvents.INIT,
    LifecycleEvents.CONFIG_CHECK,
    LifecycleEvents.CONFIG_RESOLVED,
    LifecycleEvents.CMD_START,
    LifecycleEvents.CMD_END,
    LifecycleEvents.STATUS,
    LifecycleEvents.CLEANUP,
    LifecycleEvents.COMPLETE,
    LifecycleEvents.START_RUN,
    LifecycleEvents.END_RUN,
    LifecycleEvents.SKIP,
}
