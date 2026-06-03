# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
 Modified: 2026-05-31
 File: RunUpdates/main.py
 Version: 1.0.0
 Description: Checks the distro and runs the updates
			  This should be executed in a python Virtual Environment:
              source ~/home/projects/Python/RunUpdates/.venv//bin/activate
"""

import os
from pathlib import Path
import yaml
import json

# PythonTools imports (generic only)
from PythonTools.ansible.vault import VaultLoader, VaultError
from PythonTools.ansible.loader import InventoryLoadError
from PythonTools.ansible.helpers import load_yaml
from PythonTools.log_helpers.helpers import (
    init_logger,
    build_log_cfg,
    register_custom_levels
)
from PythonTools.utils.common import json_output
# RunUpdates components
from RunUpdates.operations.listops import ListOperations
from RunUpdates.operations.orchestrator import UpdateOrchestrator
from RunUpdates.parser import ScriptParser
from RunUpdates.ansible.loader import RunUpdatesInventoryLoader
from RunUpdates.core.constants import PROJECT_NAME


# ------------------------------------------------------------
# Safety checks
# ------------------------------------------------------------

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

    log_cfg = build_log_cfg(context)
    logger_factory = init_logger(log_cfg, PROJECT_NAME)

    register_custom_levels(log_cfg)

    logger = logger_factory.get_logger("loader")

    logger.banner("RunUpdates Starting")
    logger.audit("RUNUPDATES_LOGGER_INIT", "Logger initialized successfully")
    logger.lifecycle("RUNUPDATES_LOADER_SETUP", "Loader setup complete")

    return {
        "factory": logger_factory,
        "logger": logger,
        "config": log_cfg,
        "paths": {
            "LOG_DIR": context["paths"].LOG_DIR,
            "CONFIG_DIR": context["paths"].CONFIG_DIR,
            "SCHEMA_DIR": context["paths"].SCHEMA_DIR,
            "PROJECT_NAME": PROJECT_NAME,
        }
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

    # ------------------------------------------------------------
    # Case 1: direct file
    # ------------------------------------------------------------
    if inv_path.is_file():
        if logger:
            logger.debug(f"Loading inventory from file: {inv_path}")
        return load_yaml(inv_path)

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
        return load_yaml(hosts_file)

    # Fallback: exactly one *.yml
    yml_files = list(inv_path.glob("*.yml"))
    if len(yml_files) == 1:
        if logger:
            logger.debug(f"Loading inventory from {yml_files[0]}")
        return load_yaml(yml_files[0])

    raise InventoryLoadError(
        f"Inventory directory must contain hosts.yml or exactly one *.yml file "
        f"(found {len(yml_files)} files)"
    )
# ------------------------------------------------------------
# Vault loading
# ------------------------------------------------------------
def load_secrets(context: dict) -> dict:
    vault_path = context["paths"].VAULT_PATH
    vault_password_file = context["paths"].VAULT_PASSWORD_FILE

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

def handle_summary(*, latest: bool, list_all: bool, host: str | None,
                   summary_dir: Path, logger):

    summary_dir = Path(summary_dir)

    if not summary_dir.exists():
        logger.error(f"Summary directory does not exist: {summary_dir}")
        return

    # Collect summary files
    files = sorted(
        summary_dir.glob("*.json")
    ) + sorted(
        summary_dir.glob("*.yml")
    )

    if not files:
        logger.info("No summary files found.")
        return

    # Filter by host if requested
    if host:
        filtered = []
        for f in files:
            try:
                if f.suffix == ".json":
                    data = json.loads(f.read_text())
                else:
                    data = yaml.safe_load(f.read_text())

                if data.get("host") == host:
                    filtered.append(f)
            except Exception as e:
                logger.warning(f"Failed to read summary file {f}: {e}")

        files = filtered

        if not files:
            logger.info(f"No summaries found for host '{host}'.")
            return

    # --list: list all summary files
    if list_all:
        for f in files:
            print(f.name)
        return

    # --latest: show the most recent summary
    if latest:
        latest_file = files[-1]
        print(latest_file.read_text())
        return

    # Default: show latest if no flags provided
    latest_file = files[-1]
    print(latest_file.read_text())

# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------

def main():
    # 1. Parse CLI arguments
    parser = ScriptParser()
    args = parser.parse()
    paths = parser.paths
    if args.command == "help":
        topic = args.topic

        # No topic → show global help
        if not topic:
            parser.print_help()
            return

        # Topic-specific help
        match topic:
            case "inventory":
                parser.inventory_parser.print_help()
            case "update":
                parser.update_parser.print_help()
            case "summary":
                parser.summary_parser.print_help()
            case _:
                print(f"Unknown help topic: {topic}")
                parser.parser.print_help()

        return
    if args.command == "version":
        print(f"RunUpdates {parser.VERSION_STRING}")
        return


    context = {"PROJECT_NAME": PROJECT_NAME, "args": args, "paths": paths}
    
    # 2. Initialize logging
    logging_ctx = initialize_logging(context)
    logger = logging_ctx["logger"]

    # 3. Load and validate inventory
    raw_inventory = load_inventory_file(context["paths"].INVENTORY_PATH, logger)

    # Initialize schema-driven loader
    loader = RunUpdatesInventoryLoader(
        inventory_path=context["paths"].INVENTORY_PATH,
        schema_path=context["paths"].SCHEMA_DIR / "hosts.schema.yml"
    )
    if args.command != "summary":
        # Normalize inventory into host objects (filtered)
        normalized_inventory = loader.normalize(
            family = getattr(args, "family", None),
            distro = getattr(args, "distro", None),
            host = getattr(args, "host", None),
        )
        
    match args.command:
        
        case "inventory":
            LISTING_FLAGS = (
                "list_families",
                "list_distros",
                "list_hosts",
                "list_inventory",
                "show_metadata",
            )
            # Determine if any listing flag is active
            active_flag = next(
                (flag for flag in LISTING_FLAGS if getattr(args, flag, False)),
                None
            )

            # Handle listing BEFORE vault loading
            listops = ListOperations(raw_inventory, logger)
            match active_flag:
                case "list_families":
                    dsp = listops.list_families()
                case "list_distros":
                    dsp = listops.list_distros(args.family)
                case "list_hosts":
                    dsp = listops.list_hosts(args.family, args.distro)
                case "list_inventory":
                    dsp = listops.list_inventory()
                case "show_metadata":
                    dsp = listops.show_metadata(args.family, args.distro, args.host)
                case _:
                    dsp = listops.list_inventory()
            if args.json:
                print(json_output(dsp, force_color=args.color))
            else:
                print(json.dumps(dsp, indent=2))
            return
        case "update":
            # Load secrets (only for update operations)
            context["secrets"] = load_secrets(context)
            assert_sudo_available(context.get("secrets", {}).get("sudo_pass"))
            assert_not_root()
            # Execute update orchestration
            orchestrator = UpdateOrchestrator(
                context,
                hosts=normalized_inventory,
                logger=logger
            )
            orchestrator.run()
        case "summary":
            # Summary does NOT have family/distro/host
            handle_summary(
                latest=args.latest,
                list_all=args.list,
                host=args.host,
                summary_dir=context["paths"].SUMMARY_RUN_DIR,
                logger=logger,
            )
        case _:
            raise RuntimeError(f"Unknown command: {args.command}")



    # 9. Final banner
    logger.banner("RunUpdates complete")


if __name__ == "__main__":
    main()
