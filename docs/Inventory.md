# RunUpdates — Inventory Model

The inventory is the core configuration source for RunUpdates.
It defines operating systems (families), distros, hosts, commands, exit‑codes, and connection parameters in a deterministic, YAML‑driven structure.

This document describes:

* the inventory hierarchy
* inheritance and normalization
* required fields
* vault integration
* selection and validation rules
* how the loader interprets the YAML
* future enhancements

The inventory is loaded and validated by the **RunUpdatesInventoryLoader**, which produces both raw and normalized representations.

## 1. Purpose of the Inventory

The inventory defines:

* which hosts exist
* which operating system (family) each host belongs to
* which distro each host uses
* which commands apply to that distro
* how exit codes should be interpreted
* how to connect to each host
* how vault secrets merge into host definitions

RunUpdates contains **no hardcoded distro logic**.
Everything comes from the inventory and vault.

## 2. Inventory Hierarchy

RunUpdates uses a three‑level hierarchy:

Code
```
family (OS) → distro → hosts
```

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
        address: 192.0.2.10
```

All examples in this document use **placeholder hostnames and RFC‑5737 test IPs**.

## 2.1 Families (Operating Systems)

A **family** represents an **operating system**.

Examples:

* linux
* windows
* macos

Each family contains one or more **distros**, which define the actual command and exit‑code behavior.

## 2.2 Distros

A distro is an OS variant that shares a command model.

Examples under linux:

* opensuse
* debian
* redhat
* arch (future)

### openSUSE Note

In the current implementation, **both Leap and Tumbleweed hosts** are grouped under the opensuse distro because they share the same command and exit‑code model as implemented today.
Future versions may split these into separate distros if update semantics diverge (e.g., [zypper up] vs [zypper dup]).

## 2.3 Hosts

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

## 3. Inheritance Model

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

## 4. Vault Integration

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

## 4.1 Merge Rules

* Vault values override inventory values when both define the same field.
* Missing vault entries do not disable a host.
* Validation ensures required secrets exist before execution.

## 4.2 Example Vault Entry

```yaml
suse-node-01:
  sudo-user: root
  sudo_pass: secret
  keyfile: /home/user/.ssh/id_rsa
```
After merge, the normalized host includes both inventory and vault fields.

## 5. Normalization Pipeline

The **RunUpdatesInventoryLoader** produces two representations:

### 5.1 raw_yaml

* exact structure from disk
* used for list operations
* preserves comments, ordering, formatting

### 5.2 normalized

Flattened host entries used by the orchestrator.

Example normalized host:

```yaml
{
  "family": "linux",
  "distro": "opensuse",
  "host": "suse-node-01",
  "enabled": true,
  "address": "192.0.2.10",
  "port": 2222,
  "username": "root",
  "keyfile": "/home/user/.ssh/id_rsa",
  "packages": { ... },
  "exit_codes": { ... }
}
```

### 5.3 Pipeline Flow

1. Load raw inventory YAML
2. Load raw vault YAML
3. Index families, distros, hosts
4. Apply inheritance
5. Merge vault secrets
6. Normalize into host objects
7. Apply CLI filters (--family, --distro, --host)
8. Validate selection
9. Return final host list to orchestrator

## 6. Required Fields

### 6.1 At the distro level

* packages
* exit_codes
* hosts

### 6.2 At the host level

* enabled
* address

### 6.3 Optional fields

* port
* multiple addresses (list)
* vault‑provided fields
* future: tags, roles, metadata

## 7. Validation Rules

The loader enforces:

* required keys exist
* no unknown keys
* ports are valid integers
* hosts have valid addresses
* disabled hosts cannot be selected
* commands must be strings
* exit‑code blocks must be well‑formed
* vault secrets must match expected types

### 7.1 Family/Host Consistency Rule

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

## 8. Distro Command Model

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

## 9. Exit‑Code Model

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

## 10. Inventory Scope

The RunUpdates inventory is RunUpdates‑specific.

* It is **not** a global schema for all tools.
* Other tools (e.g., BotScanner) will define their own schema.
* The global inventory abstraction layer sits above RunUpdates and is not documented here.

This document describes only the RunUpdates inventory model.

## 11. Design Principles

The inventory model reflects RunUpdates’ core philosophy:

* **Truthful state reporting** — no optimistic abstractions
* **Deterministic behavior** — predictable, reversible actions
* **Declarative configuration** — no hidden logic
* **Distro‑agnostic execution** — everything comes from YAML
* **Auditability** — normalized host objects show exactly what will run

## 12. Planned Enhancements

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

## 13. Summary

The inventory is:

* declarative
* deterministic
* extensible
* validated
* normalized
* merged with vault secrets

It is the single source of truth for all RunUpdates behavior.
 