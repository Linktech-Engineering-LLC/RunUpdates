# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-15
 File: RunUpdates/main.py
 Version: 1.0.0
 Description: Checks the distro and runs the updates
			  This should be executed in a python Virtual Environment:
              source ~/home/projects/Python/RunUpdates/.venv//bin/activate
"""

# System Libraries

# Project Libraries
from .ansible.config_loader import InventoryProcessor
from .logging.log_helpers import (
    init_logger,
    register_custom_levels
)
from .parser import ScriptParser
from .parser.vault import resolve_vault_password, resolve_vault_path

def initialize_logging(context: dict) -> dict:
    """
    Initialize RunUpdates logging system:
    - Resolve log directory and file paths
    - Perform size-based rotation (ArchiveLog-equivalent)
    - Initialize logger factory
    - Register custom log levels (optional)
    - Emit lifecycle banners

    Returns a unified logging context.
    """

    # 1. Resolve paths + build log config
    #    init_logger() must:
    #    - determine LOG_DIR
    #    - expand ~ and environment overrides
    #    - perform rotation if needed
    #    - return (paths, log_cfg, logger_factory)
    paths, log_cfg, logger_factory = init_logger(
        context
    )

    # 2. Register custom levels (TRACE, AUDIT, LIFECYCLE)
    register_custom_levels(log_cfg)

    # 3. Create logger for RunUpdates loader
    logger = logger_factory.get_logger("loader")

    # 4. Lifecycle banners (RunUpdates equivalents)
    # --- START BANNER ---
    logger.banner("RunUpdates Starting")
    logger.audit("RUNUPDATES_LOGGER_INIT", "Logger initialized successfully")
    logger.lifecycle("RUNUPDATES_LOADER_SETUP", "Loader setup complete")

    # 5. Unified logging context
    return {
        "factory": logger_factory,
        "logger": logger,
        "config": log_cfg,
        "paths": paths,
    }
def load_inventory(cfg_dir: str, context: dict, log=None):
    pass
def main():
    parser = ScriptParser()
    args = parser.parse()
    context = vars(args)
    logging_ctx = initialize_logging(context)
    logger = logging_ctx["logger"]
    inventory = load_inventory(args.inventory, context, logger)

    print(logging_ctx)
    print(inventory)
    logger.banner("RunUpdates complete")
    

if __name__ == "__main__":
    main()
