# RunUpdates
Deterministic, operator‑grade update orchestrator for cross‑platform systems.

**Suite:** Linktech Engineering Tools Suite  
**Maintainer:** Leon McClatchey, Linktech Engineering LLC  
**License:** MIT (source) • Proprietary (binaries)  
**Requires:** Python 3.12+  
**Version:** 1.0.0 (Stable) • Nightly: latest  
**Packaging:** DEB • RPM • TGZ • ZIP  
**PythonTools:** 0.2.0  
**Last Updated:** 2026‑09‑24


![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech%20Engineering-Tools%20Suite-0052CC?style=flat-square&logo=powershell)
![Status](https://img.shields.io/badge/Status-Active%20Development-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?style=flat-square&logo=linux&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/RunUpdates?style=flat-square)
[![Nightly Build](https://github.com/Linktech-Engineering-LLC/RunUpdates/actions/workflows/nightly.yml/badge.svg)](https://github.com/Linktech-Engineering-LLC/RunUpdates/actions/workflows/nightly.yml)
[![Nightly Dashboard](https://img.shields.io/badge/Nightly-Dashboard-blue)](https://linktech-engineering-llc.github.io/RunUpdates/)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📘 Table of Contents
1. [Overview](#-1-overview)
2. [Core Features](#-2-core-features)
3. [Installation](#-3-installation)
  1. [Install PythonTools](#31-install-pythontools)
  2. [Install RunUpdates](#32-install-runupdates)
  3. [Development Workflow](#33-development-workflow)
4. [Inventory Model](#-4-inventory-model)
  1. [Inventory Hierarchy](#41-inventory-hierarchy)
  2. [Address Model](#42-address-model)
5. [Secrets Model](#-5-secrets-model)
  1. [Vault Location](#51-vault-location)
6. [Commands](#-6-commands)
  1. [Top‑level Commands](#61-top-level-commands)
  2. [Inventory Subcommand](#62-inventory-subcommand)
  3. [Update Subcommand](#63-update-subcommand)
  4. [Summary Subcommand](#64-summary-subcommand)
7. [Execution Flow](#-7-execution-flow)
8. [Summaries](#-8-summaries)
  1. [Per‑Host Summary](#81-per-host-summary)
  2. [Final Summary](#82-final-summary)
9. [Architecture Overview](#-9-architecture-overview)
10. [Error Classification](#-10-error-classification)
11. [Security Model](#-11-security-model)
12. [Roadmap](#-12-roadmap)
13. [Contributing](#-13-contributing)
14. [License](#-14-license)
15. [Related Projects](#-15-related-projects)

---

## 🔍 1. Overview
**RunUpdates** is a deterministic, operator‑grade update orchestrator designed for Linux operators managing mixed‑platform fleets.
The orchestrator itself runs on Linux, but the hosts it manages may be Linux, Windows, macOS, or any platform whose lifecycle is defined in YAML.

RunUpdates executes a fixed, reproducible pipeline:
`check → refresh → update → clean → reboot`


All lifecycle behavior is defined in the inventory schema, not hard‑coded into the tool.
This ensures predictable, cross‑platform update behavior suitable for automation, dashboards, and fleet‑wide maintenance.

RunUpdates emphasizes:
* deterministic execution
* strict schema validation
* audit‑transparent logging
* machine‑readable summaries
* reproducible operator‑grade behavior

---

## ⚙️ 2. Core Features

### Deterministic, universal execution pipeline

A fixed, cross‑platform pipeline:

`check → refresh → update? → clean → reboot?`

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

RunUpdates uses a YAML‑driven ExitCodeClassifier to determine update states such as 
* `up_to_date`
* `success`
* `solver_warning` 
* `restart_services`
* `reboot_required`
* `error`

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

---

## 📦 3. Installation (Source)

RunUpdates depends on **PythonTools**.
Both must be installed in the same environment.

### 3.1 Clone and install PythonTools

```bash
git clone https://github.com/Linktech-Engineering-LLC/PythonTools.git
cd PythonTools
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3.2 Clone and install RunUpdates (same venv)

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
pip install -r requirements.txt
```

RunUpdates is now ready to use.

### 3.3 Development Workflow

If modifying both repositories:

* keep both repos checked out
* install both in editable mode
* RunUpdates will immediately see changes in PythonTools

RunUpdates is a **consumer** of PythonTools, not a bundler.

---

## 🧩 4. Inventory Model

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

### 4.1 Inventory Hierarchy

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

### 4.2 Address Model

``address`` is **always a list**, even for a single address.

This ensures:

* predictable iteration
* consistent normalization
* multi‑address failover

---

## 🔧 5. Secrets Model

Secrets are stored **only** in an encrypted vault file (e.g., ``vault.yml``).
The inventory contains **no secrets**.

RunUpdates uses CLI arguments and environment variables **only to locate**:

* the vault file
* the vault password file (or inline password)

Secrets themselves are never supplied directly via environment variables or CLI.

## 5.1 Vault Location

Vault path resolution:

1. `--vault-path`
2. `RUNUPDATES_VAULT_PATH`
3. (no default — missing value is a validation error)

Vault password resolution:

1. `--vault-password-file` or `--vault-password`
2. `RUNUPDATES_VAULT_PASSWORD_FILE`
3. (no default — missing value is a validation error)

After decrypting the vault, RunUpdates merges secrets into the normalized host objects in memory.

Secrets are:

* never logged
* never written to disk
* redacted in summaries

---

## 🚀 6. Commands
RunUpdates uses a subcommand‑driven CLI:

### 6.1 Top‑level commands

| Command | Description |
| --- | --- |
| `version` | Show version information |
| `help` | Show help for a subcommand (`help update`, `help inventory`, etc.) |
| `inventory` | Inspect inventory families, distros, hosts, and metadata |
| `update` | Run updates on selected hosts |
| `summary` | Show run summary information |

### 6.2 Inventory Subcommand

`runupdates inventory [options]`

#### Listing Options

```Bash
--list-families
--list-distros
--list-hosts
--list-inventory
--show-metadata
```

#### Selection Options

```Bash
--family <name>
--distro <name>
--host <name>
```

### 6.3 Update Subcommand

`runupdates update [options]`

#### Target Selection

```Bash
--family linux
--distro <name>
--host <name>
```

#### Execution Options

```Bash
--force
--mode sequential|parallel|distro-parallel
```

### 6.4 Summary Subcommand

`runupdates summary [options]`

#### Summary Options

```Bash
--latest
--list
--host <hostname>
```

---

## 🛠 7. Execution Flow
RunUpdates executes a deterministic lifecycle:

`check → refresh → update? → clean → reboot?`

Each step’s exit code is classified using the YAML‑defined `ExitCodeClassifier`.

#### Step Descriptions

* **check** — run the distro‑defined check command
* **classify** — each step’s exit code is mapped to a semantic category using the YAML-defined ExitCodeClassifier
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

---

## 📊 8. Summaries

All lifecycle events are now structured dictionaries containing {`step`, `exit_code`, `status`}.

Update and lifecycle status are derived from classifier categories, not raw exit codes.

### 8.1 Per‑Host Summary

Each host produces:
`<hostname>.json`

Containing:

* lifecycle status
* update status
* repo health
* reboot requirement
* exit codes
* stdout/stderr (or redacted indicators)
* timestamps

Lifecycle events are now structured and classifier‑driven.
No legacy string markers remain.

### 8.2 Final Summary

summary.json includes:

* run start/end
* duration
* totals (completed, failed, skipped, repo_broken, reboot_required, etc.)
* per‑host status map

Totals are computed from classifier categories.

---

## 🧱 9. Architecture Overview

```Code
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

---

## 🧪 10. Error Classification

RunUpdates uses a unified classification model:

* success
* up_to_date
* patches_available
* solver_warning
* restart_services
* reboot_required
* reboot_and_restart
* error

Mapped from:

* exit codes
* stdout patterns
* SSH failures
* PythonTools exceptions
* repo health indicators

Classifier categories are defined per‑step in the inventory’s `exit_codes` section.

These categories drive update_status, lifecycle_status, reboot_status, and semantic fields.

---

## 🔒 11. Security Model

* no dynamic code execution
* no YAML‑driven logic paths
* secrets only in vault.yml
* secrets never logged or written to disk
* SSH keyfile preferred
* deterministic logging
* strict schema validation

---

## 🛣 12. Roadmap

Planned enhancements:

* expanded OS family/distro examples
* richer structured check parsing
* improved reboot classification
* inventory diffing
* dashboard‑ready summary format
* semantic summary fields (updated, needs_reboot, needs_service_restart)
* classifier‑driven fleet summary counters
* distro‑specific semantic interpretation rules

---

## 🤝 13. Contributing

Pull requests are welcome.

Please ensure:

* deterministic behavior
* no breaking schema changes
* placeholder‑only examples
* documentation updates for new features

---

## 📄 14. License
MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 15. Related Projects

* [NMS_Tools](https://github.com/Linktech-Engineering-LLC/NMS_Tools)
* [VSCode-Updater](https://github.com/Linktech-Engineering-LLC/VSCode-Updater)
* [BotScanner-Community](https://github.com/Linktech-Engineering-LLC/BotScanner-Community)
* [licensegen](https://github.com/Linktech-Engineering-LLC/licensegen)
* [rust-logger](https://github.com/Linktech-Engineering-LLC/rust-logger)