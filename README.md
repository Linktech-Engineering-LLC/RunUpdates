# RunUpdates
<p align="center">

<img src="https://img.shields.io/badge/status-stable-brightgreen?style=for-the-badge" />
<img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/platform-linux-lightgrey?style=for-the-badge&logo=linux&logoColor=white" />
<img src="https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-8A2BE2?style=for-the-badge" />

</p>

RunUpdates is a deterministic, operator‑grade update orchestrator for Linux hosts.
It provides reproducible sequencing, audit‑transparent execution, and a clean, YAML‑driven model for managing package updates across heterogeneous environments.

RunUpdates is designed for engineers who want predictable behavior, clear logging, and a workflow that scales from a single workstation to a full fleet.

## ✨ Features

* **Deterministic execution pipeline**: check → refresh → update → clean → reboot (optional)

* **Inventory‑driven orchestration**: Families → Distros → Hosts with inheritance, flattening, and validation

* **Local + remote execution**

  * Local execution via sudo_run
  * Remote execution via SSHSession (keyfile + password fallback)

* **YAML‑driven distro model**: Commands and exit‑codes defined declaratively per distro

* **Operator‑grade logging**: Structured, timestamped, and suitable for audit trails

* **Flexible host selection**: --family, --distro, --host, or full‑inventory runs

* **Dry‑run mode**: Preview commands without executing them

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
RunUpdates uses a structured YAML inventory that defines:

* distro families
* package manager commands
* exit‑code interpretation
* host lists
* connection parameters

*** Example (openSUSE)

```yaml
linux:
  opensuse:
    packages:
      check: "zypper refresh && zypper patch-check --with-optional"
      refresh: "zypper refresh"
      update: "zypper --non-interactive up --auto-agree-with-licenses --replacefiles"
      clean: "zypper clean"
      reboot: "zypper needs-rebooting"

      exit_codes:
        check:
          up_to_date: [0]
          patches_available: [101]
          error: ["*"]

    port: 2222

    hosts:
      Lab-Suse-01:
        enabled: true
        address: [192.168.0.67, 10.145.156.10]
```

### Inventory hierarchy

* **Family** (e.g., linux)
* **Distro** (e.g., opensuse)
* **Hosts** (e.g., Lab-Suse-01)

RunUpdates merges:

* family defaults
* distro defaults
* host overrides

…into a flattened host object used during execution.

## 🔧 Secrets Model

Secrets are loaded from a vault file or environment variables.

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

## 🛠 Execution Pipeline

Each host runs the following steps in order:

1. check
2. refresh
3. update
4. clean
5. reboot (optional)

Each step is logged with:

* exit code
* stdout
* stderr

Failures are reported but do not stop the overall run.

## 🧱 Architecture Overview

text
main.py
 └── UpdateOrchestrator
      ├── InventoryProcessor
      ├── HostSelector
      ├── HostConnector
      │     ├── local (sudo_run)
      │     └── SSHSession
      └── HostExecutor

### Responsibilities

* **InventoryProcessor** → flattens and normalizes inventory
* **HostSelector** → determines which hosts should run
* **HostConnector** → selects local vs remote execution
* **HostExecutor** → runs the distro‑defined pipeline
* **PythonTools** → provides execution primitives and session layer

### PythonTools Integration

RunUpdates includes a shared execution layer called **PythonTools**, which provides:

* `sudo_run` for local privileged execution
* `local_command` for non‑privileged local execution
* `SSHSession` for remote execution
* injected logging
* injected secrets
* reusable helpers (in progress)

PythonTools is internal today but will eventually be extracted into a standalone Linktech Engineering library.

## 🤝 Contributing

Pull requests are welcome.

Please ensure:

* consistent formatting
* deterministic behavior
* clear logging
* no breaking changes to inventory schema

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
