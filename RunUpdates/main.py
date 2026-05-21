# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-17
 File: RunUpdates/main.py
 Version: 1.0.0
 Description: Checks the distro and runs the updates
			  This should be executed in a python Virtual Environment:
              source ~/home/projects/Python/RunUpdates/.venv//bin/activate
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon

"""
RunUpdates main entry point.
Checks the distro and runs the updates.
"""

import os
from pathlib import Path
import yaml

# RunUpdates imports
from RunUpdates.parser import ScriptParser
from RunUpdates.core.constants import (
    PROJECT_NAME,
    PROJECT_VERSION,
)
from RunUpdates.utils.common import (
    resolve_inventory_path,
    resolve_vault_path,
    resolve_vault_password_file,
)

# PythonTools imports (generic only)
from PythonTools.logging.helpers import (
    init_logger,
    register_custom_levels
)
from PythonTools.ansible.vault import VaultLoader, VaultError
from PythonTools.ansible.loader import GenericInventoryLoader, InventoryError
# RunUpdates components
from RunUpdates.operations.listops import ListOperations
from RunUpdates.operations.orchestrator import UpdateOrchestrator


# ------------------------------------------------------------
# Safety checks
# ------------------------------------------------------------

class InventoryLoadError(Exception):
    pass


def assert_not_root():
    if os.geteuid() == 0:
        raise RuntimeError("RunUpdates must not be executed as root")


def assert_sudo_available(sudo_password):
    if sudo_password is None:
        raise RuntimeError("No sudo password available for non-root execution")


# ------------------------------------------------------------
# Logging initialization
# ------------------------------------------------------------

def initialize_logging(context: dict) -> dict:
    """
    Initialize RunUpdates logging system.
    """

    paths, log_cfg, logger_factory = init_logger(context)

    register_custom_levels(log_cfg)

    logger = logger_factory.get_logger("loader")

    logger.banner("RunUpdates Starting")
    logger.audit("RUNUPDATES_LOGGER_INIT", "Logger initialized successfully")
    logger.lifecycle("RUNUPDATES_LOADER_SETUP", "Loader setup complete")

    return {
        "factory": logger_factory,
        "logger": logger,
        "config": log_cfg,
        "paths": paths,
    }


# ------------------------------------------------------------
# Inventory loading
# ------------------------------------------------------------

def load_inventory_file(inv_path: Path, logger):
    """
    Resolve an inventory file or directory and return the raw YAML dict.
    This function does NOT validate or normalize — that is handled by
    GenericInventoryLoader in PythonTools.
    """

    inv_path = Path(inv_path)

    # ------------------------------------------------------------
    # Case 1: direct file
    # ------------------------------------------------------------
    if inv_path.is_file():
        if logger:
            logger.debug(f"Loading inventory from file: {inv_path}")
        return yaml.safe_load(inv_path.read_text(encoding="utf-8")) or {}

    # ------------------------------------------------------------
    # Case 2: directory
    # ------------------------------------------------------------
    if not inv_path.exists() or not inv_path.is_dir():
        raise InventoryLoadError(f"Inventory path is not a directory or file: {inv_path}")

    # Prefer hosts.yml
    hosts_file = inv_path / "hosts.yml"
    if hosts_file.exists():
        if logger:
            logger.debug(f"Loading inventory from {hosts_file}")
        return yaml.safe_load(hosts_file.read_text(encoding="utf-8")) or {}

    # Fallback: exactly one *.yml
    yml_files = list(inv_path.glob("*.yml"))
    if len(yml_files) == 1:
        if logger:
            logger.debug(f"Loading inventory from {yml_files[0]}")
        return yaml.safe_load(yml_files[0].read_text(encoding="utf-8")) or {}

    raise InventoryLoadError(
        f"Inventory directory must contain hosts.yml or exactly one *.yml file "
        f"(found {len(yml_files)} files)"
    )


# ------------------------------------------------------------
# Vault loading
# ------------------------------------------------------------

def load_secrets(context: dict) -> dict:
    vault_path = context.get("vault_path")
    vault_password_file = context.get("vault_password_file")

    if not vault_path:
        raise VaultError("vault_path missing from context")

    if not vault_password_file:
        raise VaultError("vault_password_file missing from context")

    loader = VaultLoader(
        vault_path,
        vault_password_file,
        program_name=PROJECT_NAME
    )
    secrets = loader.decrypt_yaml()

    if not isinstance(secrets, dict):
        raise VaultError("Vault decrypted but did not contain a top-level dictionary")

    required_keys = ["sudo_user", "sudo_pass", "keyfile"]

    for key in required_keys:
        if key not in secrets:
            raise VaultError(f"Missing required secret: {key}")
        if not secrets[key]:
            raise VaultError(f"Secret '{key}' is empty or null")

    secrets["keyfile"] = os.path.expanduser(secrets["keyfile"])

    return secrets


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------

def main():
    # 1. Parse CLI arguments
    parser = ScriptParser()
    args = parser.parse()
    context = vars(args)

    # 2. Initialize logging
    logging_ctx = initialize_logging(context)
    logger = logging_ctx["logger"]

    # 3. Load raw inventory YAML
    inv_path = Path(resolve_inventory_path(context.get("inventory", "")))
    # Load raw YAML
    raw_inventory = load_inventory_file(inv_path, logger)
    
    # 4. Load secrets
    secrets = load_secrets(context)

    assert_sudo_available(secrets.get("sudo_pass"))
    assert_not_root()

    # 5. Schema path
    schema_path = Path(__file__).resolve().parent / "schema" / "hosts.schema.yml"

    # 6. Initialize schema-driven loader
    loader = GenericInventoryLoader(
        inventory_path=inv_path,
        schema_path=schema_path
    )
    # 7. Normalize inventory into host objects
    normalized_inventory = loader.normalize()

    # 8. List operations (raw inventory)
    listops = ListOperations(raw_inventory, logger)

    dispatch = {
        "list_families": lambda: print(listops.list_families()),
        "list_distros": lambda: print(listops.list_distros(args.family)),
        "list_hosts": lambda: print(listops.list_hosts(args.family, args.distro)),
        "list_inventory": lambda: print(listops.list_inventory()),
    }

    for flag, action in dispatch.items():
        if getattr(args, flag):
            action()
            return

    # 9. Execute update orchestration (flattened inventory)
    orchestrator = UpdateOrchestrator(
        args=args,
        inventory=normalized_inventory,
        secrets=secrets,
        logger=logger
    )

    orchestrator.run()

    # 7. Final banner
    logger.banner("RunUpdates complete")


if __name__ == "__main__":
    main()
