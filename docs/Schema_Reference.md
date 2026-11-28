# RunUpdates Schema Reference

**Part of:** RunUpdates
**Document:** Schema Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Schema Philosophy](#3-schema-philosophy)
4. [Root Structure](#4-root-structure)
5. [Family Schema](#5-family-schema)
   1. [Family Variables](#51-family-variables)
6. [Distro Schema](#6-distro-schema)
   1. [Variables](#61-variables)
   2. [Lifecycle](#62-lifecycle)
   3. [Commands](#63-commands)
   4. [Exit Codes](#64-exit-codes)
   5. [Hosts](#65-hosts)
7. [Host Schema](#7-host-schema)
   1. [Required Fields](#71-required-fields)
   2. [Optional Fields](#72-optional-fields)
8. [Inheritance Rules](#8-inheritance-rules)
9. [Validation Rules](#9-validation-rules)
   1. [Structural Validation](#91-structural-validation)
   2. [Type Validation](#92-type-validation)
   3. [Semantic Validation](#93-semantic-validation)
10. [Reserved Fields](#10-reserved-fields)
11. [Example Inventory](#11-example-inventory)
12. [Schema Versioning](#12-schema-versioning)
13. [Summary](#13-summary)
14. [Notes](#14-notes)

---

## 1. Overview

This document defines the formal schema used by RunUpdates inventory files.

The inventory schema describes:

* Operating-system families.
* Family variables.
* Distro definitions.
* Lifecycle definitions.
* Command definitions.
* Exit-code classifications.
* Host definitions.
* Inheritance behavior.

The inventory schema is validated before execution begins.

Inventory behavior is documented in `Inventory.md`.

This document defines only valid structure, field usage, and validation rules.

---

## 2. Purpose

The purpose of the schema is to provide a deterministic and validated configuration model.

The schema exists to:

* Define valid inventory structure.
* Enforce consistent field types.
* Prevent configuration ambiguity.
* Support inheritance and normalization.
* Provide predictable validation behavior.
* Enable future schema evolution.

After validation succeeds, the inventory may be normalized and used by the orchestrator.

---

## 3. Schema Philosophy

The RunUpdates schema follows several core principles.

* Explicit configuration.
* Deterministic behavior.
* Declarative execution.
* No hidden defaults.
* Strict validation.
* Human-readable structure.

Every value must be explicitly defined.

RunUpdates does not invent missing configuration values during execution.

---

## 4. Root Structure

The inventory root contains one or more operating-system families.

Example:

```yaml
linux:
  vars:
    port: 2222
  opensuse:
    ...
  redhat:
    ...
  debian:
    ...
```

The root structure is interpreted as:

```text
Operating System Family
    ├─ vars
    └─ distro
            ├─ vars
            ├─ lifecycle
            ├─ commands
            ├─ exit_codes
            └─ hosts
```

Each family may contain one or more distro definitions.

---

## 5. Family Schema

A family represents a broad operating-system category.

Examples include:

* linux
* windows (future)
* macos (future)

Family names are user-defined and must be unique within the inventory.

### 5.1 Family Variables

A family may define inherited variables.

Example:

```yaml
linux:
  vars:
    port: 2222
```

Family variables are inherited by all child distros and hosts unless overridden.

Common family variables may include:

* Port numbers.
* Connection settings.
* Default behavior flags.

---

## 6. Distro Schema

A distro defines execution behavior for a specific operating-system variant.

Examples include:

* opensuse
* redhat
* debian

Each distro may contain:

* vars
* lifecycle
* commands
* exit_codes
* hosts

### 6.1 Variables

Distro variables provide distro-specific configuration.

Example:

```yaml
vars:
  systemd: true
  systemd_mode: wait
```

Current commonly used variables include:

* systemd
* systemd_mode

Additional variables may be added in future versions.

### 6.2 Lifecycle

A distro may define its execution lifecycle.

Example:

```yaml
lifecycle:
  - refresh
  - check
  - list
  - update
  - clean
  - reboot
```

Lifecycle entries define execution order.

Each entry references a command key defined in the commands section.

Lifecycle sequences may differ between distros.

### 6.3 Commands

Commands define executable actions.

Example:

```yaml
commands:
  refresh: "zypper refresh"
  check: "zypper patch-check --with-optional"
  update: "zypper dup"
  clean: "zypper clean"
  reboot: "zypper needs-rebooting"
```

Commands are executed exactly as defined.

RunUpdates does not modify command behavior.

Common commands include:

* refresh
* check
* list
* update
* clean
* reboot
* reboot_now

Additional command names may be introduced in future versions.

### 6.4 Exit Codes

Exit-code definitions map command results to classifications.

Example:

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [100, 101]
    error: ["*"]
```

Exit-code definitions are organized by command name.
Each command may contain one or more classifications.

Supported patterns include:

* Exact exit-code matching.
* Wildcard matching (`"*"`).
* Exclusion rules (`"!1"`).

Detailed classification behavior is documented in [Error_Classification.md](Error_Classification.md).

### 6.5 Hosts

Each distro contains a hosts block.

Example:

```yaml
hosts:
  host01:
    enabled: true
    address:
      - 192.0.2.10
```

Hosts are defined as a dictionary of host names.

Host names must be unique within the distro.
---

## 7. Host Schema

Each host *represents a single managed system*

### 7.1 Required Fields

| Field | Type | Description |
|---------|-------|---------|
| address | list[string] | One or more host addresses |

Address is always represented as a list, even when only a single address exists.

Example:

```yaml
address:
  - 192.0.2.10
```

### 7.2 Optional Fields

| Field | Type | Description |
|---------|--------|---------|
| enabled | bool | enables or disables host execution |
| vm_host | string | Parent virtualization host |
| port | integer | Host-specific port override |
| systemd | bool | Host-specific system override |
| systemd_mode | string | Host-specific systemd mode override |

Example:
```yaml
host01:
  enabled: true
  address:
    - 192.0.2.10
    - 198.51.100.10
```
Hosts may define multiple addresses.

Connection behavior is determined by runtime logic.

---

## 8. Inheritance Rules

RunUpdates supports variable inheritance.

Inheritance order is:

1. Family variables.
2. Distro variables.
3. Host overrides.

Example:

```yaml
linux:
  vars:
    port: 2222
  opensuse:
    vars:
      systemd: true
```

The most specific value always takes precedence.

After inheritance is applied, the inventory is normalized into runtime host objects.

---

## 9. Validation Rules

RunUpdates performs strict validation before execution begins.

### 9.1 Structural Validation

Validation verifies:

* At least one family exists.
* Distros are correctly nested beneath families.
* Hosts are correctly nested beneath distros.
* Required structures exist.
* Required fields exist.

After structural validation succeeds, type validation may begin.

### 9.2 Type Validation

Validation verifies:

* Strings are strings.
* Integers are integers.
* Booleans are booleans.
* Lists are lists.
* Dictionaries are dictionaries.

All values must match their expected types.

### 9.3 Semantic Validation

Validation verifies:

* Host names are unique.
* Addresses are not empty.
* Lifecycle entries are valid.
* Commands contain executable strings.
* Exit-code definitions are well-formed.
* Override relationships are valid.

Inventories failing validation are rejected before execution begins.

---

## 10. Reserved Fields

The following names are reserved for schema evolution:

* schema_version
* metadata
* groups
* tags
* repos
* keys
* packages

Reserved fields may become active in future schema versions.

---

## 11. Example Inventory

The example below demonstrates a simplified valid inventory.

```yaml
linux:
  vars:
    port: 2222
  opensuse:
    vars:
      systemd: true
      systemd_mode: wait
    lifecycle:
      - refresh
      - check
      - update
      - clean
      - reboot
    commands:
      refresh: "zypper refresh"
      check: "zypper patch-check"
      update: "zypper dup"
      clean: "zypper clean"
      reboot: "zypper needs-rebooting"
    exit_codes:
      check:
        up_to_date: [0]
        patches_available: [100, 101]
        error: ["*"]
    hosts:
      host01:
        enabled: true
        address:
          - 192.0.2.10
```

All examples in this document use placeholder values.

---

## 12. Schema Versioning

The current schema version is:

```yaml
version: 1.2
```

Future releases may introduce explicit inventory version declarations.

Example:

```yaml
schema_version: 2
```

Version changes may require:

* Migration guidance.
* Release notes.
* Schema updates.
* Documentation updates.

Breaking changes must be accompanied by a schema version increment.

---

## 13. Summary

The RunUpdates schema provides a deterministic and validated inventory model.

Key characteristics include:

* Explicit configuration.
* Strict validation.
* Declarative execution.
* Variable inheritance.
* Command-driven behavior.
* Distro-specific classifications.
* Stable normalization.

This document serves as the authoritative reference for the RunUpdates inventory schema.

## 14. Notes

This document defines the formal schema used by RunUpdates inventory files.

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
* [QuickStart.md](QuickStart.md)
* [Troubleshooting.md](Troubleshooting.md)

The schema definitions documented here are considered authoritative for inventory validation and normalization behavior.

The implementation of the schema is defined by `hosts.schema.yml`.