# RunUpdates

![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech%20Engineering-Tools%20Suite-0052CC?style=flat-square&logo=powershell)
![Status](https://img.shields.io/badge/Status-Active%20Development-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?style=flat-square&logo=linux&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/RunUpdates?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

RunUpdates is a deterministic, operator‑grade update orchestrator for Linux hosts.
It provides reproducible sequencing, audit‑transparent execution, and a clean, YAML‑driven model for managing package updates across heterogeneous environments.

RunUpdates is designed for engineers who want predictable behavior, clear logging, and a workflow that scales from a single workstation to a full fleet.

## ✨ Core Features
### Deterministic execution pipeline
`refresh → check → update? → clean → reboot?`
Every step is logged, timestamped, and classified.

### Inventory‑driven orchestration

A structured YAML inventory defines:
* OS families
* distros
* commands
* exit‑code interpretation
* lifecycle steps
* host lists
* connection parameters

Inventory is validated, normalized, and flattened before execution.

### Local + remote execution

* Local execution via sudo_run
* Remote execution via SSH (keyfile preferred, password fallback)

### Declarative distro model

Each distro defines its own commands, lifecycle, and exit‑code semantics.

### Operator‑grade logging

Structured, timestamped, redacted logs suitable for audit trails.

### Machine‑readable summaries

Per‑host JSON summaries and a final aggregated summary.

### Unified path resolution
All paths (config, schema, inventory, logs, summaries) follow a strict priority:

1. CLI override
2. Environment variable
3. Development‑mode defaults
4. Installed‑mode defaults
5. Frozen‑bundle defaults

Environment paths support ~ expansion and normalization.

## 📦 Installation (Source)

RunUpdates depends on the PythonTools package.
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

If you are actively modifying both repositories:
* Keep both repos checked out locally
* Install both in editable mode (pip install -e .)
* RunUpdates will immediately see changes made in PythonTools

This mirrors the intended architecture:

**RunUpdates is a consumer of PythonTools, not a bundler of it.**

## 🧩 Inventory Model

RunUpdates uses a structured YAML inventory defining:

* operating system families
* distros
* commands
* exit‑code interpretation
* lifecycle steps
* host lists
* connection parameters
* secrets merged from vault/environment

### Inventory Hierarchy

`family (OS) → distro → hosts`

Examples of families:

* linux
* windows
* macos

Examples of distros under linux:

* opensuse
* debian
* redhat

#### Example

```yaml
linux:
  opensuse:
    packages:
      refresh: "zypper refresh"
      check: "zypper patch-check --with-optional"
      update: "zypper --non-interactive up --auto-agree-with-licenses"
      clean: "zypper clean"
      reboot: "zypper needs-rebooting"

    exit_codes:
      check:
        up_to_date: [0]
        patches_available: [100, 101]
        error: ["*"]

    port: 2222

    hosts:
      suse-node-01:
        enabled: true
        address: ["192.0.2.10"]
```

#### Address Model
`address` is **always a list**, even when only one address is present.

This ensures:

* consistent normalization
* predictable iteration
* multi‑address failover support

## 🔧 Secrets Model

Secrets are loaded from a vault file or environment variables.

Required fields

```yaml
username: "ssh username"
password: "optional ssh + sudo password"
keyfile: "/path/to/private/key"
```

## Authentication Model

* **username** → SSH username
* **keyfile** → primary SSH authentication
* **password** → fallback SSH authentication + sudo password

Secrets are:

* merged into normalized host objects
* never logged
* never written to disk

## 🚀 Usage

### List operations

```bash
runupdates --list-families
runupdates --list-distros
runupdates --list-hosts
runupdates --list-inventory
```

### Execute updates

Run against a family:

```bash
runupdates --family linux
```

Run against a specific distro:

```bash
runupdates --family linux --distro opensuse
```

Run against a single host:

```bash
runupdates --host suse-node-01
```

Dry‑run mode:

```bash
runupdates --dry-run
```

## 🛠 Execution Flow

Each host runs the following steps:

1. refresh
2. check
3. update (only if needed)
4. clean
5. reboot detection

Each step records:

* exit code
* stdout/stderr
* classification
* timestamps

Failures do **not** stop the overall run.

## 📊 Summaries

### Per‑Host Summary

Each host produces:

`<hostname>.json`

Containing:

* lifecycle status
* update status
* repo health
* reboot requirement
* exit codes
* stdout/stderr
* timestamps

### Final Summary

`summary.json` includes:

* run start/end
* duration
* totals (completed, failed, skipped, repo_broken, reboot_required, etc.)
* per‑host status map

## 🧱 Architecture Overview

Code
```
main.py
 └── UpdateOrchestrator
      ├── HostSelector
      ├── HostConnector
      │     ├── sudo_run (local)
      │     └── SSHSession (remote)
      ├── HostExecutor
      └── SummaryWriter

RunUpdatesInventoryLoader
 ├── YAML loading
 ├── schema validation
 ├── inheritance merging
 ├── vault merging
 └── normalization
```

### Responsibilities

* **RunUpdatesInventoryLoader** → loads, validates, normalizes inventory
* **HostSelector** → applies CLI filters
* **HostConnector** → selects local vs remote execution
* **HostExecutor** → runs the distro‑defined pipeline
* **PythonTools** → execution primitives

Summary generation is integrated into the HostExecutor (per‑host summaries) and the UpdateOrchestrator (final summary).

## 🧪 Error Classification

RunUpdates uses a unified classification model:

* success
* warning
* error
* fatal

Mapped from:

* exit codes
* SSH failures
* PythonTools exceptions

## 🔒 Security Model

* no dynamic code execution
* no YAML‑driven logic paths
* no secrets in logs
* SSH keyfile preferred
* deterministic logging
* strict inventory validation

### Environment Variables (Ansible‑Style Naming)

RunUpdates supports environment variables for vault configuration using the pattern:

Code
```
<APPLICATION_NAME>_<VARIABLE>
```

For RunUpdates, the following variables are recognized:

[RUNUPDATES_VAULT_PATH]

Path to the encrypted vault file.

Example:

```bash
export RUNUPDATES_VAULT_PATH="$HOME/ansible/vault.yml"
```

[RUNUPDATES_VAULT_PASSWORD_FILE]

Path to the file containing the vault password.

Example:

```bash
export RUNUPDATES_VAULT_PASSWORD_FILE="$HOME/.ansible/password"
```

Resolution Order
RunUpdates resolves vault configuration in this order:

1. CLI arguments  
  ([--vault-path], [--vault-password-file], [--vault-password])

2. Environment variables  
  ([RUNUPDATES_VAULT_PATH], [RUNUPDATES_VAULT_PASSWORD_FILE])

3. Defaults  
  (none today — missing values cause a validation error)

## 🛣 Roadmap

Upcoming enhancements:

* structured check parsing (zypper/dnf/apt)
* improved reboot classification
* expanded distro support
* inventory diffing
* dashboard‑ready summary format

## 🤝 [Contributing](CONTRIBUTING.md)

Pull requests are welcome.

Please ensure:

* deterministic behavior
* no breaking changes to the inventory schema
* placeholder‑only examples
* documentation updates for new features

## 📄 [License](LICENSE)
MIT License — see LICENSE for details.

## 🔗 Related Projects

* [NMS_Tools](https://github.com/Linktech-Engineering-LLC/NMS_Tools)
* [VSCode-Updater](https://github.com/Linktech-Engineering-LLC/VSCode-Updater)
* [BotScanner-Community](https://github.com/Linktech-Engineering-LLC/BotScanner-Community)
* [licensegen](https://github.com/Linktech-Engineering-LLC/licensegen)
* [rust-logger](https://github.com/Linktech-Engineering-LLC/rust-logger)