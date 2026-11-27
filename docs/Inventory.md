# RunUpdates Inventory Model

**Part of:** RunUpdates
**Document:** Inventory Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-26

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Inventory Hierarchy](#3-inventory-hierarchy)
   1. [Families](#31-families-operating-systems)
   2. [Distros](#32-distros)
   3. [Hosts](#33-hosts)
4. [Inheritance Model](#4-inheritance-model)
5. [Vault Integration](#5-vault-integration)
   1. [Merge Rules](#51-merge-rules)
   2. [Example Vault Entry](#52-example-vault-entry)
6. [Normalization Pipeline](#6-normalization-pipeline)
   1. [Raw Inventory](#61-raw_yaml)
   2. [Normalized Inventory](#62-normalized)
   3. [Pipeline Flow](#63-pipeline-flow)
7. [Required Fields](#7-required-fields)
   1. [Required Distro Fields](#71-at-the-distro-level)
   2. [Required Host Fields](#72-required-host-fields)
   3. [Optional Fields](#73-optional-fields)
8. [Validation Rules](#8-validation-rules)
   1. [Family and Host Consistency](#81-family-and-host-consistency-rule)
9. [Distro Command Model](#9-distro-command-model)
10. [Exit-Code Model](#10-exitcode-model)
11. [Inventory Scope](#11-inventory-scope)
12. [Design Principles](#12-design-principles)
13. [Planned Enhancements](#13-planned-enhancements)
14. [Summary](#14-summary)
15. [Notes](#15-notes)

---

## 1. Overview

The inventory is the core configuration source for RunUpdates.

It defines operating system families, distributions, hosts, command definitions, exit-code mappings, and connection parameters using a deterministic YAML-based model.

The inventory is loaded and validated by the `RunUpdatesInventoryLoader`, which produces both raw and normalized representations for use throughout the application.

This document defines the structure, behavior, and interpretation of the RunUpdates inventory model.

---

## 2. Purpose

The inventory serves as the authoritative source of configuration for RunUpdates.

The goals of the inventory model are to:

* Define which hosts exist.
* Associate hosts with operating system families and distributions.
* Define update lifecycle commands.
* Define exit-code classifications.
* Provide connection configuration.
* Integrate vault-provided secrets.
* Support deterministic execution.

After the inventory is loaded and validated, all execution behavior derives from the normalized inventory model.

RunUpdates contains no hardcoded distribution-specific execution logic.

---

## 3. Inventory Hierarchy

RunUpdates uses a three-level hierarchy:

```text
Family
    └─ Distro
          └─ Host

Example:

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
      refresh:
        success: [0]
        error: ["*"]

    port: 2222

    hosts:
      suse-node-01:
        enabled: true
        address: [ 192.0.2.10 ]
```

All examples in this document use **placeholder hostnames and RFC‑5737 test IPs**.

### 3.1 Families (Operating Systems)

A **family** represents an **operating system**.

Examples:

* linux
* windows
* macos

Each family contains one or more **distros**, which define the actual command and exit‑code behavior.

### 3.2 Distros

A distro is an OS variant that shares a command model.

Examples under linux:

* opensuse
* debian
* redhat
* arch (future)

#### openSUSE Note

In the current implementation, **both Leap and Tumbleweed hosts** are grouped under the opensuse distro because they share the same command and exit‑code model as implemented today.
Future versions may split these into separate distros if update semantics diverge (e.g., [zypper up] vs [zypper dup]).

### 3.3 Hosts

A host defines:

* enabled: true/false
* address: always a list, even when only a single address is provided
* port: optional override
* future: tags, roles, metadata

Example:

```yaml
hosts:
  suse-node-01:
    enabled: true
    address: [ 192.0.2.10 ]
```

---

## 4. Inheritance Model

RunUpdates supports inheritance at three levels:

1. Family defaults
2. Distro defaults
3. Host overrides

Example:

```yaml
linux:
  defaults:
    port: 22

  opensuse:
    port: 2222
    hosts:
      suse-node-01:
        port: 2200
```

Normalization produces:

| Level |	Port |
| *--- | *---* |
| Family default | 22 |
| Distro default | 2222 |
| Host override |	2200 |

## 5. Vault Integration

RunUpdates loads:

1. **Full inventory YAML**
2. **Full vault YAML**
3. **Merges them into a unified host model**

Vault entries may include:

* SSH usernames
* SSH keys
* passwords
* tokens
* future: per‑host metadata

### 5.1 Merge Rules

* Vault values override inventory values when both define the same field.
* Missing vault entries do not disable a host.
* Validation ensures required secrets exist before execution.

### 5.2 Example Vault Entry

```yaml
suse-node-01:
  sudo-user: root
  sudo_pass: secret
  keyfile: /home/user/.ssh/id_rsa
```
After merge, the normalized host includes both inventory and vault fields.

---

## 6. Normalization Pipeline

The **RunUpdatesInventoryLoader** produces two representations:

### 6.1 raw_yaml

* exact structure from disk
* used for list operations
* preserves comments, ordering, formatting

### 6.2 normalized

Flattened host entries used by the orchestrator.

Example normalized host:

```yaml
{
  "family": "linux",
  "distro": "opensuse",
  "host": "suse-node-01",
  "enabled": true,
  "address": [ "192.0.2.10" ],
  "port": 2222,
  "username": "root",
  "keyfile": "/home/user/.ssh/id_rsa",
  "packages": { ... },
  "exit_codes": { ... }
}
```

### 6.3 Pipeline Flow

1. Load raw inventory YAML
2. Load raw vault YAML
3. Index families, distros, hosts
4. Apply inheritance
5. Merge vault secrets
6. Normalize into host objects
7. Apply CLI filters (--family, --distro, --host)
8. Validate selection
9. Return final host list to orchestrator

---

## 7. Required Fields

### 7.1 Required Distro Fields

* packages
* exit_codes
* hosts

### 7.2 Required Host Fields

* enabled
* address

### 7.3 Optional fields

* port
* multiple addresses (list)
* vault‑provided fields
* future: tags, roles, metadata

---

## 8. Validation Rules

The loader enforces:

* required keys exist
* no unknown keys
* ports are valid integers
* hosts have valid addresses
* disabled hosts cannot be selected
* commands must be strings
* exit‑code blocks must be well‑formed
* vault secrets must match expected types

### 8.1 Family and Host Consistency Rule

If the user specifies:

Code
```
--family X --host Y
```

Then:

* host Y **must** belong to family X
* otherwise RunUpdates raises an exception and stops

Example invalid:

Code
```
--family linux --host win-node-01
```

---

## 9. Distro Command Model

Each distro defines:

* refresh
* check
* update
* clean
* reboot
* optional: reboot_now

Commands are executed **exactly as written**.

RunUpdates does not modify or interpret commands beyond:

* substitution (future)
* exit‑code classification

## 10. Exit‑Code Model

Each command has a mapping:

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [100]
    error: ["*"]
```

The executor uses this to classify results.

This model is distro‑agnostic and fully declarative.

---

## 11. Inventory Scope

The RunUpdates inventory is RunUpdates‑specific.

* It is **not** a global schema for all tools.
* Other tools (e.g., BotScanner) will define their own schema.
* The global inventory abstraction layer sits above RunUpdates and is not documented here.

This document describes only the RunUpdates inventory model.

---

## 12. Design Principles

The inventory model reflects RunUpdates’ core philosophy:

* **Truthful state reporting** — no optimistic abstractions
* **Deterministic behavior** — predictable, reversible actions
* **Declarative configuration** — no hidden logic
* **Distro‑agnostic execution** — everything comes from YAML
* **Auditability** — normalized host objects show exactly what will run

---

## 13. Planned Enhancements

Future versions will add:

* schema versioning
* repo definitions
* GPG key imports
* host tags and grouping
* package‑level filtering
* pre/post list commands
* structured check parsing
* vault schema validation
* inventory diffing

---

## 14. Summary

The inventory is:

* declarative
* deterministic
* extensible
* validated
* normalized
* merged with vault secrets

It is the single source of truth for all RunUpdates behavior.

---

## 15. Notes

This document focuses exclusively on inventory structure, validation, normalization, and runtime interpretation.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)
* [PythonTools.md](PythonTools.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

The inventory model defined in this document is considered authoritative for all RunUpdates host and distro configuration.