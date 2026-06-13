# RunUpdates

![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech%20Engineering-Tools%20Suite-0052CC?style=flat-square&logo=powershell)
![Status](https://img.shields.io/badge/Status-Active%20Development-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?style=flat-square&logo=linux&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/RunUpdates?style=flat-square)
[![Nightly Build](https://github.com/Linktech-Engineering-LLC/RunUpdates/actions/workflows/nightly.yml/badge.svg)](https://github.com/Linktech-Engineering-LLC/RunUpdates/actions/workflows/nightly.yml)
[![Nightly Dashboard](https://img.shields.io/badge/Nightly-Dashboard-blue)](https://linktech-engineering-llc.github.io/RunUpdates/)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

RunUpdates is a deterministic, operator‑grade update orchestrator that runs on Linux and manages updates for any platform whose lifecycle is defined in YAML.

The orchestrator itself is Linux‑based, but the hosts it manages may be Linux, Windows, macOS, OS/2, or any other system with a command model defined in the inventory schema.

RunUpdates emphasizes:

* reproducible execution
* strict validation
* audit‑transparent logging
* schema‑aligned configuration
* machine‑readable summaries
* predictable operator‑grade behavior

## ✨ Core Features

### Deterministic, universal execution pipeline

A fixed, cross‑platform pipeline:

`check → parse → refresh → update? → clean → reboot?`

The pipeline is **not distro‑defined**.

All hosts follow the same lifecycle, with commands supplied by the inventory.

### YAML‑defined OS families and command models

The inventory schema defines:

* OS families (linux, windows, macos, etc.)
* distros (sub‑families)
* commands for each lifecycle step
* stdout/exit‑code semantics
* reboot detection
* host definitions
* secrets merging
* connection parameters

RunUpdates does not assume Linux hosts — it assumes **schema‑validated commands**.

### Cross‑platform orchestration

* Local execution via sudo_run
* Remote execution via SSH (keyfile preferred, password fallback)
* Any platform is supported if its lifecycle is defined in YAML

### Universal stdout‑based update detection

RunUpdates includes a universal parser that detects:

* updates available
* updates performed
* no updates needed
* repo broken
* reboot required

This works across all distros and OS families.

### Strict validation

* schema validation
* header audit mode
* fix‑headers‑only mode
* family/distro/host cross‑validation
* host family mismatch detection

### Operator‑grade logging

* structured JSON logs
* redacted secrets
* timestamped lifecycle events
* deterministic formatting

### Machine‑readable summaries

* per‑host JSON summaries
* aggregated final summary
* classification fields
* reboot indicators
* repo health

### Unified path resolution

All paths (config, schema, inventory, logs, summaries) follow:

1. CLI override
2. Environment variable
3. Development‑mode defaults
4. Installed‑mode defaults
5. Frozen‑bundle defaults (.env auto‑generated)

## 📦 Installation (Source)

RunUpdates depends on **PythonTools**.
Both must be installed in the same environment.

### 1. Clone and install PythonTools

```bash
git clone https://github.com/Linktech-Engineering-LLC/PythonTools.git
cd PythonTools
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Clone and install RunUpdates (same venv)

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
pip install -r requirements.txt
```

RunUpdates is now ready to use.

### Development Workflow

If modifying both repositories:

* keep both repos checked out
* install both in editable mode
* RunUpdates will immediately see changes in PythonTools

RunUpdates is a **consumer** of PythonTools, not a bundler.

## 🧩 Inventory Model

The inventory is a structured YAML document defining:

* OS families
* distros
* commands
* lifecycle semantics
* exit‑code or stdout rules
* hosts
* connection parameters

**Secrets are not stored in the inventory**.
They live only in the vault file (``vault.yml``).

### Inventory Hierarchy

`family → vars → distro → vars → hosts`

Example:

```yaml
linux:
  vars:
    port: 2239
  opensuse:
    vars:
      systemd: true
      systemd_mode: wait # or: async
      lifecycle:
        - refresh
        - check
        - update
        - clean
        - reboot
      commands:
        refresh: "zypper refresh" 
        check: "zypper patch-check --with-optional"
        update: "zypper --non-interactive up --auto-agree-with-licenses --recommends --replacefiles --allow-vendor-change"
        clean: "zypper clean"
        reboot: "zypper needs-rebooting"
        orphans: "zypper packages --orphaned"
        list: "zypper list-updates --all"
        reboot_now: "systemctl reboot || shutdown -r now"
      exit_codes:
        refresh:
          success: [0]
          error: ["*"]

        check:
          up_to_date: [0]
          patches_available: [100, 101]
          error: ["*"]

        update:
          success: [0]
          reboot_required: [102, 104]
          restart_services: [103]
          error: ["*"]

        reboot:
          no_reboot: [0]
          reboot_required: [102]
          restart_services: [103]
          reboot_and_restart: [104]
          error: ["*"]

    hosts:
      suse-node-01:
        enabled: true
        address: ["192.0.2.10"]
```

### Address Model

``address`` is **always a list**, even for a single address.

This ensures:

* predictable iteration
* consistent normalization
* multi‑address failover

## 🔧 Secrets Model

Secrets are stored **only** in an encrypted vault file (e.g., ``vault.yml``).
The inventory contains **no secrets**.

RunUpdates uses CLI arguments and environment variables **only to locate**:

* the vault file
* the vault password file (or inline password)

Secrets themselves are never supplied directly via environment variables or CLI.

## Vault Location

Vault path resolution:

1. ``--vault-path``
2. ``RUNUPDATES_VAULT_PATH``
3. (no default — missing value is a validation error)

Vault password resolution:

1. ``--vault-password-file`` or ``--vault-password``
2. ``RUNUPDATES_VAULT_PASSWORD_FILE``
3. (no default — missing value is a validation error)

After decrypting the vault, RunUpdates merges secrets into the normalized host objects in memory.

Secrets are:

* never logged
* never written to disk
* redacted in summaries

## 🚀 Commands
RunUpdates uses a subcommand‑driven CLI:

### Top‑level commands

| Command | Description |
| --- | --- |
| ``version`` | Show version information |
| ``help`` | Show help for a subcommand (``help ``update``, ``help ``inventory``, etc.) |
| ``inventory`` | Inspect inventory families, distros, hosts, and metadata |
| ``update`` | Run updates on selected hosts |
| ``summary`` | Show run summary information |

### 📚 Inventory Subcommand

`runupdates inventory [options]`

#### Listing Options

Code
--list-families
--list-distros
--list-hosts
--list-inventory
--show-metadata

#### Selection Options

Code
--family <name>
--distro <name>
--host <name>


### 🔧 Update Subcommand

`runupdates update [options]`

#### Target Selection

Code
--family linux
--distro <name>
--host <name>

#### Execution Options

Code
--force
--mode sequential|parallel|distro-parallel

### 📊 Summary Subcommand

`runupdates summary [options]`

#### Summary Options

Code
--latest
--list
--host <hostname>

### 🛠 Execution Flow
RunUpdates executes a deterministic lifecycle:

`check → parse → refresh → update? → clean → reboot?`

#### Step Descriptions

* **check** — run the distro‑defined check command
* **parse** — classify stdout/exit codes into universal update states
* **refresh** — refresh package metadata (only if updates are needed)
* **update** — apply updates (conditional)
* **clean** — always run; remove stale metadata and temp files
* **reboot** — detect whether a reboot is required

Each step records:

* exit code
* stdout/stderr
* classification
* timestamps

Failures do not stop the overall run.

## 📊 Summaries

### Per‑Host Summary

Each host produces:

Code
<hostname>.json

Containing:

* lifecycle status
* update status
* repo health
* reboot requirement
* exit codes
* stdout/stderr (or redacted indicators)
* timestamps

### Final Summary

summary.json includes:

* run start/end
* duration
* totals (completed, failed, skipped, repo_broken, reboot_required, etc.)
* per‑host status map

## 🧱 Architecture Overview

```
main.py
 └── UpdateOrchestrator
      ├── ConfigResolver
      ├── PathResolver
      ├── SchemaLoader
      ├── RunUpdatesInventoryLoader
      ├── VaultLoader
      ├── HostSelector
      ├── HostConnector
      │     ├── sudo_run (local)
      │     └── SSHSession (remote)
      ├── HostExecutor
      ├── UniversalCheckParser
      ├── RebootWaiter
      └── SummaryAggregator
```

### Responsibilities

* **ConfigResolver** → resolves CLI/env/default paths
* **SchemaLoader** → loads and validates schema
* **RunUpdatesInventoryLoader** → loads, merges, normalizes inventory
* **VaultLoader** → locates, decrypts, and merges vault secrets
* **HostSelector** → applies CLI filters
* **HostConnector** → local vs remote execution
* **HostExecutor** → runs deterministic lifecycle
* **UniversalCheckParser** → stdout/exit‑code classification
* **SummaryAggregator** → builds final summary

## 🧪 Error Classification

RunUpdates uses a unified classification model:

* success
* warning
* error
* fatal

Mapped from:

* exit codes
* stdout patterns
* SSH failures
* PythonTools exceptions
* repo health indicators

## 🔒 Security Model

* no dynamic code execution
* no YAML‑driven logic paths
* secrets only in vault.yml
* secrets never logged or written to disk
* SSH keyfile preferred
* deterministic logging
* strict schema validation

## 🛣 Roadmap

Planned enhancements:

* expanded OS family/distro examples
* richer structured check parsing
* improved reboot classification
* inventory diffing
* dashboard‑ready summary format

## 🤝 Contributing

Pull requests are welcome.

Please ensure:

* deterministic behavior
* no breaking schema changes
* placeholder‑only examples
* documentation updates for new features

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

* [NMS_Tools](https://github.com/Linktech-Engineering-LLC/NMS_Tools)
* [VSCode-Updater](https://github.com/Linktech-Engineering-LLC/VSCode-Updater)
* [BotScanner-Community](https://github.com/Linktech-Engineering-LLC/BotScanner-Community)
* [licensegen](https://github.com/Linktech-Engineering-LLC/licensegen)
* [rust-logger](https://github.com/Linktech-Engineering-LLC/rust-logger)