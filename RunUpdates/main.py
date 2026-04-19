# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-04-19
 File: RunUpdates/main.py
 Version: 1.0.0
 Description: Checks the distro and runs the updates
			  This should be executed in a python Virtual Environment:
              source ~/home/projects/Python/RunUpdates/.venv//bin/activate
"""

# System Libraries
import json
from pathlib import Path
import yaml
# Project Libraries
from .ansible.config_loader import InventoryProcessor
from .ansible.vault_loader import VaultLoader
from .logging.log_helpers import (
    init_logger,
    register_custom_levels
)
from .operations.listops import ListOperations
from .operations.orchestrator import UpdateOrchestrator
from .parser import ScriptParser
from .parser.vault import resolve_vault_password, resolve_vault_path

class InventoryLoadError(Exception):
    pass

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
def load_inventory_file(inv_path: Path, logger):
    """
    Load inventory from either:
    - a direct file path, or
    - a directory containing exactly one inventory file.

    Rules:
    1. If inv_path is a file → load it directly.
    2. If inv_path is a directory:
        a. If hosts.yml exists → load it.
        b. Else if exactly one *.yml exists → load it.
        c. Else → error.
    """

    # ------------------------------------------------------------
    # Case 1: inventory is a file
    # ------------------------------------------------------------
    if Path(inv_path).is_file():
        if logger:
            logger.debug(f"Loading inventory from file: {inv_path}")
        return { "inventory": yaml.safe_load(inv_path.read_text(encoding="utf-8"))} or {}

    # ------------------------------------------------------------
    # Case 2: inventory is a directory
    # ------------------------------------------------------------
    if not Path(inv_path).exists() or not Path(inv_path).is_dir():
        raise InventoryLoadError(f"Inventory path is not a directory or file: {inv_path}")

    # 1. Prefer hosts.yml
    hosts_file = Path(inv_path) / "hosts.yml"
    if hosts_file.exists():
        if logger:
            logger.debug(f"Loading inventory from {hosts_file}")
        return { "inventory": yaml.safe_load(hosts_file.read_text(encoding="utf-8"))} or {}

    # 2. Fallback: exactly one *.yml
    yml_files = list(Path(inv_path).glob("*.yml"))
    if len(yml_files) == 1:
        if logger:
            logger.debug(f"Loading inventory from {yml_files[0]}")
        return { "inventory": yaml.safe_load(yml_files[0].read_text(encoding="utf-8"))} or {}

    # 3. Error on ambiguity or absence
    raise InventoryLoadError(
        f"Inventory directory must contain hosts.yml or exactly one *.yml file "
        f"(found {len(yml_files)} files)"
    )
def load_secrets(context: dict) -> dict:
    secrets = {}
    vault_path = context.get("vault_path","")
    vault_password = context.get("vault_password","")
    loader = VaultLoader(vault_path, vault_password)
    secrets = loader.decrypt_yaml()
    
    return secrets 
    
    
def main():
    # --------------------------------------------------------------
    # 1. Parse CLI arguments
    # --------------------------------------------------------------
    parser = ScriptParser()
    args = parser.parse()
    context = vars(args)

    # --------------------------------------------------------------
    # 2. Initialize logging
    # --------------------------------------------------------------
    logging_ctx = initialize_logging(context)
    logger = logging_ctx["logger"]

    # --------------------------------------------------------------
    # 3. Load inventory + secrets
    # --------------------------------------------------------------
    cfg = load_inventory_file(context.get("inventory", ""), logger)
    secrets = load_secrets(context)

    inventory = cfg.get("inventory", {})

    # --------------------------------------------------------------
    # 4. Initialize InventoryProcessor
    # --------------------------------------------------------------
    proc = InventoryProcessor(
        logger=logger
    )

    # --------------------------------------------------------------
    # 5. Handle list operations via dispatch dictionary
    # --------------------------------------------------------------
    listops = ListOperations(inventory, proc, logger)

    dispatch = {
        "list_families": lambda: print(listops.list_families()),
        "list_distros":  lambda: print(listops.list_distros(args.family)),
        "list_hosts":    lambda: print(listops.list_hosts(args.family, args.distro)),
        "list_inventory": lambda: print(listops.list_inventory()),
    }

    # Determine which list flag was used
    for flag, action in dispatch.items():
        if getattr(args, flag):
            action()
            return

    # --------------------------------------------------------------
    # 6. Execute update orchestration
    # --------------------------------------------------------------
    orchestrator = UpdateOrchestrator(
        args=args,
        inventory_processor=proc,
        inventory=inventory,
        secrets=secrets,
        logger=logger
    )

    orchestrator.run()

    # --------------------------------------------------------------
    # 7. Final banner
    # --------------------------------------------------------------
    logger.banner("RunUpdates complete")
    

if __name__ == "__main__":
    main()
