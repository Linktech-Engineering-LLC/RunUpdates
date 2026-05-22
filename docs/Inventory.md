# RunUpdates — Inventory Model

The inventory is the core configuration source for RunUpdates.
It defines families, distros, hosts, commands, exit‑codes, and connection parameters in a deterministic, YAML‑driven structure.

This document describes:
* the inventory hierarchy
* how inheritance and normalization work
* what fields are required
* how the loader interprets the YAML
* future enhancements to the model

The inventory is loaded and validated by the **RunUpdatesInventoryLoader**, which produces both raw and normalized representations.

## 1. Purpose of the Inventory

The inventory defines:
* which hosts exist
* which distro each host belongs to
* which commands apply to that distro
* how exit codes should be interpreted
* how to connect to each host

RunUpdates does **not** contain hardcoded distro logic.
Everything comes from the inventory.

## 2. Inventory Hierarchy
The inventory uses a three‑level hierarchy:

`family → distro → hosts`

Example:
```Yaml
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
      lab-suse-01:
        enabled: true
        address: 192.168.1.10
```

### 2.1 Families

A family groups related distros.

Examples:
* linux
* debian-family (future)
* redhat-family (future)

### 2.2 Distros

Each distro defines:
* package commands
* exit‑code mappings
* default SSH port
* optional overrides

### 2.3 Hosts

Each host defines:
* enabled: true/false
* address (string or list)
* port (optional override)
* future: tags, roles, metadata

## 3. Inheritance Model

RunUpdates supports inheritance at three levels:
1. **Family defaults**
2. **Distro defaults**
3. **Host overrides**

Example:

```Yaml
linux:
  defaults:
    port: 22

  opensuse:
    port: 2222
    hosts:
      node1:
        port: 2200
```

Normalization produces:
| Level | Port |
| --- | --- |
| Family default | 22 |
| Distro default | 2222 |
| Host override | 2200 |

## 4. Normalization Process

The **RunUpdatesInventoryLoader** produces two representations:

### 4.1 raw_yaml
* exact structure from disk
* used for list operations
* preserves comments, ordering, and formatting

### 4.2 normalized

Flattened host entries used by the orchestrator.

Example normalized host:

```Yaml
{
  "family": "linux",
  "distro": "opensuse",
  "host": "lab-suse-01",
  "enabled": true,
  "address": "192.168.1.10",
  "port": 2222,
  "packages": {
    "refresh": "...",
    "check": "...",
    "update": "...",
    "clean": "...",
    "reboot": "..."
  },
  "exit_codes": {
    "refresh": { "success": [0], "error": ["*"] },
    "check": { ... },
    "update": { ... },
    "reboot": { ... }
  }
}
```
This is what the orchestrator receives.

## 5. Required Fields

### 5.1 At the distro level

* packages
* exit_codes
* hosts

### 5.2 At the host level

* enabled
* address

### 5.3 Optional fields

* port
* multiple addresses (list)
* future: tags, roles, metadata

## 6. Validation Rules

The loader enforces:
* required keys exist
* no unknown keys
* ports are valid integers
* hosts have valid addresses
* disabled hosts cannot be selected
* commands must be strings
* exit‑code blocks must be well‑formed

Validation failures stop execution before any host is contacted.

## 7. Distro Command Model

Each distro defines:
* refresh
* check
* update
* clean
* reboot
* optional: reboot_now

These commands are executed exactly as written.

RunUpdates does **not** modify or interpret commands beyond:
* substitution (future)
* exit‑code classification

## 8. Exit‑Code Model

Each command has a mapping:
```Yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [100, 101]
    error: ["*"]
```
The executor uses this to classify results.

This model is distro‑agnostic and fully declarative.

## 9. Planned Enhancements

Future versions will add:
* schema versioning
* repo definitions
* GPG key imports
* host tags and grouping
* package‑level filtering
* pre/post list commands
* structured check parsing
* per‑host summaries

## 10. Summary

The inventory is:
* declarative
* deterministic
* extensible
* validated
* normalized

It is the single source of truth for all RunUpdates behavior.
