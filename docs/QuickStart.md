# RunUpdates Quick Start

**Part of:** RunUpdates
**Document:** Quick Start Guide
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
3. [Installation Methods](#3-installation-methods)
   1. [Frozen Package Installation](#31-frozen-package-installation)
   2. [Source Installation](#32-source-installation)
4. [Configuration Setup](#4-configuration-setup)
5. [Vault Setup](#5-vault-setup)
   1. [Vault File](#51-vault-file)
   2. [Vault Password File](#52-vault-password-file)
   3. [Providing Vault Paths](#53-providing-vault-paths)
6. [Validating Configuration](#6-validating-configuration)
7. [Running RunUpdates](#7-running-runupdates)
8. [Reviewing Results](#8-reviewing-results)
9. [Runtime Directories](#9-runtime-directories)
10. [Common Examples](#10-common-examples)
11. [Next Steps](#11-next-steps)
12. [Summary](#12-summary)
13. [Notes](#13-notes)

---

## 1. Overview

RunUpdates is a deterministic, YAML-driven update orchestrator for Linux hosts.

The application uses inventory-driven configuration, structured logging, vault-managed credentials, and declarative classification rules to provide predictable and auditable update execution.

This guide provides the minimum information required to install, configure, validate, and execute RunUpdates.

---

## 2. Requirements

RunUpdates requires:

* A supported Linux operating system.
* A valid `hosts.yml` inventory.
* A valid vault file.
* A valid vault password file.
* Network connectivity to managed hosts.
* Appropriate authentication credentials.

Additional requirements depend on the selected installation method.

---

## 3. Installation Methods

RunUpdates supports multiple installation methods.

Available methods include:

* Frozen packages (recommended)
* Source installation

Frozen packages are recommended for operators and production deployments.

Source installation is recommended for development and testing.

### 3.1 Frozen Package Installation

RunUpdates frozen releases are available in multiple formats:

* RPM
* DEB
* TGZ
* ZIP

Install the appropriate package for your platform using the instructions provided with the release package.

Frozen packages include all required Python dependencies and do not require a Python virtual environment.

After installation completes, proceed to Configuration Setup.

### 3.2 Source Installation

Source installation is intended for developers and contributors.

Create and activate a virtual environment:

```bash
python3 -m venv venv

source venv/bin/activate
```

Install PythonTools:

```bash
pip install git+https://github.com/Linktech-Engineering-LLC/PythonTools.git
```

Clone and install RunUpdates:

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git

cd RunUpdates

pip install -e .

pip install -r requirements.txt
```

After installation completes, proceed to Configuration Setup.

Detailed build instructions are documented in [Build.md](Build.md).

---

## 4. Configuration Setup

RunUpdates expects a configuration directory containing:

```text
etc/
├── hosts.yml
└── schemata/
```

For source installations, create the directory structure:

```bash
mkdir -p etc
```

Populate the inventory:

```bash
cp templates/hosts.yml.example etc/hosts.yml
```

Create the schema link:

```bash
ln -s ../schemata etc/schemata
```

Frozen package installations typically create the required directory structure automatically.

After configuration files are present, vault configuration may begin.

---

## 5. Vault Setup

RunUpdates requires a vault file and a vault password file.

Execution will fail if either component is unavailable.

### 5.1 Vault File

The vault file:

* Must reside in a secured directory.
* Must use restrictive file permissions.
* Should not be stored alongside the inventory.
* Should not be committed to source control.

Example:

```bash
mkdir -m 700 ~/runupdates-vault

cp vault.yml ~/runupdates-vault/

chmod 600 ~/runupdates-vault/vault.yml
```

### 5.2 Vault Password File

The vault password file should be stored separately from the vault.

Example:

```bash
echo "mypassword" > ~/.vault_pass

chmod 600 ~/.vault_pass
```

### 5.3 Providing Vault Paths

Vault locations may be supplied through command-line arguments.

Example:

```bash
runupdates update \
    --vault-path ~/runupdates-vault/vault.yml \
    --vault-password-file ~/.vault_pass
```

Vault locations may also be supplied through environment variables:

```bash
export RUNUPDATES_VAULT_PATH=~/runupdates-vault/vault.yml

export RUNUPDATES_VAULT_PASSWORD_FILE=~/.vault_pass
```

After vault configuration is complete, inventory validation should be performed.

---

## 6. Validating Configuration

Validate the entire inventory:

```bash
runupdates inventory
```

Validate a specific family:

```bash
runupdates inventory --family linux
```

Validate a specific distro:

```bash
runupdates inventory --distro opensuse
```

Validate a specific host:

```bash
runupdates inventory --host leap-node
```

Inventory validation should be performed whenever inventory or schema files are modified.

---

## 7. Running RunUpdates

RunUpdates provides several subcommands:

* `inventory`
* `update`
* `summary`
* `version`
* `help`

Execute updates against all hosts:

```bash
runupdates update
```

Execute updates against a single host:

```bash
runupdates update --host leap-node
```

Execute updates against a distro:

```bash
runupdates update --distro opensuse
```

Execute updates against a family:

```bash
runupdates update --family linux
```

Detailed operational behavior is documented in `Operation.md`.

---

## 8. Reviewing Results

After execution completes, review:

* Execution logs.
* Host summaries.
* Fleet summaries.
* Repository health classifications.
* Reboot requirements.

Important output files include:

```text
summary.json
```

and:

```text
<hostname>.json
```

Classification details are documented in `Error_Classification.md`.

---

## 9. Runtime Directories

RunUpdates stores runtime artifacts in dedicated directories.

### Logs

```text
var/logs/
```

Contains:

* Active logs.
* Archived logs.
* Operator events.

### Summaries

```text
var/log/summaries/
```

Contains:

* Host summaries.
* Fleet summaries.

### PID File

```text
var/run/runupdates.pid
```

The PID file location is independent of log configuration.

---

## 10. Common Examples

Validate inventory:

```bash
runupdates inventory
```

Perform a dry run:

```bash
runupdates update --dry-run
```

Update a single host:

```bash
runupdates update --host leap-node
```

Update all Linux hosts:

```bash
runupdates update --family linux
```

Display version information:

```bash
runupdates version
```

---

## 11. Next Steps

After completing the Quick Start process, review:

* [Design.md](Design.md)
* [Inventory.md](Inventory.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Error_Classification.md](Error_Classification.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)

These documents provide detailed information about system behavior and operational design.

---

## 12. Summary

RunUpdates provides deterministic, inventory-driven update orchestration for Linux environments.

Key characteristics include:

* Inventory-driven configuration.
* Vault-managed credentials.
* Structured logging.
* Declarative classification.
* Runtime summaries.
* Deterministic execution.

This guide provides the minimum information required to install, configure, validate, and execute RunUpdates using either a frozen package or source installation.

---

## 13. Notes

This document provides introductory installation and usage guidance for RunUpdates.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Inventory.md](Inventory.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)
* [PythonTools.md](PythonTools.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

Quick Start is intended for initial deployment and first execution of RunUpdates.