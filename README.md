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

---

# ✨ Features

- **Deterministic execution pipeline**  
  refresh → check → update? → clean → reboot?

- **Inventory‑driven orchestration**  
  Families → Distros → Hosts with inheritance, flattening, and strict validation

- **Local + remote execution**  
  - Local execution via `sudo_run`  
  - Remote execution via `SSHSession` (keyfile preferred, password fallback)

- **Declarative distro model**  
  Commands, exit‑codes, and reboot indicators defined per distro

- **Operator‑grade logging**  
  Structured, timestamped, redacted, and suitable for audit trails

- **Flexible host selection**  
  `--family`, `--distro`, `--host`, or full‑inventory runs

- **Dry‑run mode**  
  Preview commands without executing them

- Machine‑readable summaries (planned)  
  Per‑host JSON summaries will be added in a future release.

---

# 📦 Installation

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
RunUpdates is now ready to use.

## 🧩 Inventory Model
RunUpdates uses a structured YAML inventory that defines:

* distro families
* package manager commands
* exit‑code interpretation
* host lists
* connection parameters
* raw_yaml is used for list operations
* normalized inventory is used for orchestration

**Example (openSUSE)**

**Note:** All values below (ports, addresses, hostnames) are placeholders. Replace them with your actual environment.

```yaml
linux:
  opensuse:
    packages:
      check: "zypper patch-check --with-optional"
      refresh: "zypper refresh" 
      update: "zypper --non-interactive up --auto-agree-with-licenses --recommends --replacefiles --allow-vendor-change"
      clean: "zypper clean"
      orphans: "zypper packages --orphaned"
      list: "zypper list-updates --all"
      reboot: "zypper needs-rebooting"
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

    port: nnnn # Non-Standard Port used for ssh

    hosts:
      sample_host:
        enabled: true
        address: [nnn.nnn.nnn.nnn, nnn.nnn.nnn.nnn]
```

### Inventory hierarchy

* **Family** (e.g., linux)
* **Distro** (e.g., opensuse)
* **Hosts** (e.g., Lab-Suse-01)

RunUpdatesInventoryLoader performs inheritance merging and normalization before orchestration begins.

## 🔧 Secrets Model

Secrets are loaded from a vault file or environment variables.
RunUpdates injects secrets into PythonTools at startup.

* secrets are passed explicitly
* no global state
* no implicit injection

### Required fields

```yaml
username: "ssh username"
password: "optional ssh + sudo password"
keyfile: "/path/to/private/key"
```

### Authentication model

* **username** → SSH username
* **keyfile** → primary SSH authentication
* **password** → fallback SSH authentication + sudo password

At least one authentication method must be available.

RunUpdates injects secrets into PythonTools at startup.
Secrets are never logged or written to disk.

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
runupdates --host Lab-Suse-01
```

Dry‑run mode:

```bash
runupdates --dry-run
```

## 🛠 Execution Flow

Each host runs the following steps in order:

1. refresh
2. check
  * backend‑specific parsing (zypper/dnf/apt)
  * Interprets exit codes according to the inventory schema
  * Output parsing for patch counts is planned for the next release
3. update (only if needed)
4. clean (always)
5. reboot detection

Failures do not stop the overall run.

Each step is logged with:

* exit code
* stdout/stderr
* classification (success/warning/error/fatal)

Failures do not stop the overall run.

For full details, see:
![📄 Execution](docs/Execution_Flow.md)

## 🧱 Architecture Overview

text
main.py
 └── UpdateOrchestrator
      ├── HostSelector (CLI filtering)
      ├── HostConnector
      │     ├── LocalSession (sudo_run)
      │     └── SSHSession
      └── HostExecutor (runs distro-defined pipeline)

      RunUpdatesInventoryLoader
      ├── YAML loading
      ├── schema validation
      ├── inheritance merging
      └── normalization (flattening)

### Responsibilities

* **RunUpdatesInventoryLoader** → loads, validates, and normalizes inventory
* **HostSelector** → determines which hosts should run
* **HostConnector** → selects local vs remote execution
* **HostExecutor** → runs the distro‑defined pipeline
* **PythonTools** → provides execution primitives and session layer

For full architecture details:
![📄 ARCHITECTURE](ARCHITECTURE.md)

## 🧪 Error Classification

RunUpdates uses a unified, distro‑agnostic classification model:

* success
* warning
* error
* fatal

Mapped from exit codes and PythonTools exceptions.

Full classification rules:

![📄 Error_Classification](docs/Error_Classification.md)

## 🔒 Security Model

RunUpdates is designed with a minimal attack surface:

* no dynamic code execution
* no YAML‑driven logic paths
* no secrets in logs
* SSH keyfile preferred
* deterministic logging
* strict inventory validation

Full security policy:
![📄 SECURITY](SECURITY.md)

## 🛣 Roadmap

The next release will introduce:

* backend‑specific parsing for check output (zypper/dnf/apt)
* structured JSON results for the check operation
* per‑host JSON summaries
* improved reboot classification
* expanded distro support

### PythonTools Integration

RunUpdates is built on top of **PythonTools**, a shared execution substrate used across the Linktech Engineering Tools Suite.
PythonTools provides deterministic, operator‑grade primitives for command execution, session management, and structured logging.

PythonTools supplies:

* sudo_run for privileged local execution
* local_command for non‑privileged local execution
* SSHSession for remote execution
* structured logging injection
* secrets injection
* consistent return structures
* reusable helpers for orchestration workflows

PythonTools is now a standalone micro‑library maintained alongside RunUpdates, NMS_Tools, BotScanner, TimerDeck, and future tools.
RunUpdates relies on PythonTools for all execution‑layer behavior, ensuring consistent, reproducible results across local and remote hosts.

## 🤝 Contributing

Pull requests are welcome.

Please ensure:

* deterministic behavior
* no breaking changes to the inventory schema
* clear, structured logging
* placeholder‑only examples
* documentation updates for new features

Full guidelines:
![📄 CONTRIBUTING](CONTRIBUTING.md)

## 📄 License
MIT License — see LICENSE for details.

## 🔗 Related Projects

RunUpdates is part of the Linktech Engineering Tools Suite.  
You may also find these projects useful:

- **NMS_Tools**  
  A suite of deterministic Nagios-compatible monitoring tools with structured logging and operator‑grade output.  
  https://github.com/Linktech-Engineering-LLC/NMS_Tools

- **VSCode-Updater**  
  A cross‑platform, operator‑grade updater for Visual Studio Code with deterministic logging and reproducible workflows.  
  https://github.com/Linktech-Engineering-LLC/VSCode-Updater

- **BotScanner**  
  A lightweight, deterministic scanning tool for identifying automated traffic patterns and bot signatures.  
  https://github.com/Linktech-Engineering-LLC/BotScanner

- **licensegen**  
  A simple, reproducible license generator supporting SPDX identifiers and clean header injection.  
  https://github.com/Linktech-Engineering-LLC/licensegen

- **rust_logger**  
  A minimal, deterministic logging library for Rust projects with operator‑grade formatting.  
  https://github.com/Linktech-Engineering-LLC/rust_logger
