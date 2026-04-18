# RunUpdates

<p align="center">

  <!-- Project Status -->
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=for-the-badge" />

  <!-- License -->
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" />

  <!-- Python Version -->
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />

  <!-- Platform -->
  <img src="https://img.shields.io/badge/platform-linux-lightgrey?style=for-the-badge&logo=linux&logoColor=white" />

  <!-- Linktech Engineering Branding -->
  <img src="https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-8A2BE2?style=for-the-badge" />

</p>

RunUpdates is a deterministic, operator‑grade update orchestrator for Linux hosts.  
It provides reproducible sequencing, audit‑transparent execution, and a clean inventory‑driven model for managing package updates across heterogeneous environments.

RunUpdates is designed for engineers who want predictable behavior, clear logging, and a workflow that scales from a single workstation to a full fleet.

---

## ✨ Features

- **Deterministic execution pipeline**  
  check → refresh → update → clean → reboot (optional)

- **Inventory‑driven orchestration**  
  Families → Distros → Hosts with inheritance and flattening

- **Local + remote execution**  
  LocalSession (sudo) and SSHSession (keyfile + password fallback)

- **Operator‑grade logging**  
  Structured, timestamped, and suitable for audit trails

- **Flexible host selection**  
  `--family`, `--distro`, `--host`, or full‑inventory runs

- **List operations**  
  Introspect families, distros, hosts, or the entire inventory

- **Dry‑run mode**  
  Preview commands without executing them

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
```
Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

RunUpdates is now ready to use.

## 🧩 Inventory Model
RunUpdates uses a structured YAML inventory:

```yaml
linux:
ubuntu:
    defaults:
    port: 22
    commands:
        check: "apt-get check"
        refresh: "apt-get update"
        update: "apt-get upgrade -y"
        clean: "apt-get autoremove -y"
    hosts:
    ub25-srvr-01:
        address: "192.168.1.10"
        enabled: true
```

## Inventory hierarchy

- **Family** (e.g., linux)
- **Distro** (e.g., ubuntu)
- **Hosts** (e.g., ub25-srvr-01)

RunUpdates merges:

- family defaults
- distro defaults
- host overrides

…into a flattened host object used during execution.

## 🔧 Secrets Model

Secrets are loaded from a vault file or environment variables.

Required fields:

```yaml
sudo_user: "elevated username"
sudo_pass: "elevated password"
keyfile: "/path/to/ssh/key"
```

**Authentication model:**

- sudo_user → SSH username
- keyfile → primary SSH authentication
- sudo_pass → fallback SSH password and sudo password

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
runupdates --family linux --distro ubuntu
```

Run against a single host:

```bash
runupdates --host ub25-srvr-01
```

Dry‑run mode:

```bash
runupdates --dry-run
```

## 🛠 Execution Pipeline

Each host runs the following steps in order:

- check
- refresh
- update
- clean
- reboot (optional)

Each step is logged with:

- exit code
- stdout
- stderr

Failures are reported but do not stop the overall run.

## 🧱 Architecture Overview

```code
main.py
 └── UpdateOrchestrator
      ├── HostSelector
      ├── HostConnector
      │     ├── LocalSession
      │     └── SSHSession
      └── HostExecutor
```

### Responsibilities

- **HostSelector** → decides whether a host should run
- **HostConnector** → decides how to connect
- **HostExecutor**   → decides what commands to run
- **InventoryProcessor** → flattens and normalizes inventory
- **ListOperations** → introspection utilities

## 🤝 Contributing

Pull requests are welcome.

Please ensure:

- consistent formatting
- deterministic behavior
- clear logging

no breaking changes to inventory schema

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
