# RunUpdates Execution Flow

**Part of:** RunUpdates
**Document:** Execution Flow Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-26

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [High-Level Lifecycle](#3-high-level-lifecycle)
4. [Inventory Processing](#4-inventory-processing)
  1. [Load Inventory](#41-load-inventory)
  2. [Validate Schema](#42-validate-schema)
  3. [Normalize Inventory](#43-normalize-inventory)
5. [Logging Initialization](#5-logging-initialization)
6. [Host Selection](#6-host-selection)
7. [Host Processing](#7-host-processing)
  1. [Session Creation](#71-session-creation)
8. [Lifecycle Execution](#8-lifecycle-execution)
  1. [Check](#81-check)
  2. [Refresh](#82-refresh)
  3. [Update](#83-update)
  4. [Clean](#84-clean)
  5. [Reboot Detection](#85-reboot-detection)
9. [Error Classification Integration](#9-error-classification-integration)
10. [Per-Host Summaries](#10-per-host-summaries)
11. [Final Aggregation](#11-final-aggregation)
12. [Error Handling](#12-error-handling)
  1. [Inventory Errors](#121-inventory-errors)
  2. [Connection Errors](#122-connection-errors)
  3. [Command Errors](#123-command-errors)
13. [Determinism Guarantees](#13-determinism-guarantees)
14. [Future Parallel Execution](#14-future-parallel-execution)
15. [Summary](#15-summary)
16. [Notes](#16-notes)

---

## 1. Overview

This document describes the complete execution lifecycle of RunUpdates, from process startup through final result aggregation.

While **ARCHITECTURE.md** defines the structural design of the application, this document defines runtime behavior and execution sequencing.

RunUpdates is designed to be deterministic, predictable, and operator-grade. Every phase of execution is structured to produce reproducible results, auditable logs, and consistent summaries.

---

## 2. Purpose

The goals of this document are to:

* Define the exact sequence of operations performed during a RunUpdates execution.
* Explain how inventory management, sessions, logging, and summaries interact.
* Describe lifecycle stage behavior.
* Define execution-time error handling.
* Document determinism guarantees.
* Provide a reference for future concurrency support.

After these goals are established, the document describes the complete runtime lifecycle of the application.

This document serves as the authoritative execution reference for RunUpdates.

---

## 3. High-Level Lifecycle

A complete RunUpdates execution follows the sequence below.

```text
Load Inventory
        │
        ▼
Validate Schema
        │
        ▼
Normalize Inventory
        │
        ▼
Initialize Logging
        │
        ▼
Select Hosts
        │
        ▼
Process Hosts
        │
        ├─ Create Session
        ├─ Check
        ├─ Refresh
        ├─ Update (Conditional)
        ├─ Clean
        └─ Reboot Detection
        │
        ▼
Write Host Summary
        │
        ▼
Aggregate Results
        │
        ▼
Write Final Summary
```

After the lifecycle begins, every stage produces structured logs and deterministic output.

The sections below describe each phase in detail.

---

## 4. Inventory Processing

Inventory processing prepares host definitions for orchestration and execution.

The inventory must be validated and normalized before any hosts are contacted.

### 4.1 Load Inventory

RunUpdates loads `hosts.yml` using the `RunUpdatesInventoryLoader`.

The loader performs the following tasks:

* Reads the inventory file.
* Loads the raw YAML structure.
* Prepares inventory data for validation.

After inventory loading completes, schema validation begins.

If inventory loading fails:

* Execution stops immediately.
* No host communication occurs.
* An error is written to the log.

### 4.2 Validate Schema

Schema validation ensures inventory consistency before execution begins.

Validation verifies:

* Required fields are present.
* Data types are correct.
* Unknown keys are rejected.
* Port values are valid.
* Host definitions are well formed.
* `address` is always represented as a list.

After validation succeeds, inventory normalization may proceed.

If validation fails:

* An error is logged.
* No hosts are contacted.
* Execution terminates immediately.

### 4.3 Normalize Inventory

The inventory loader transforms validated inventory data into normalized runtime objects.

Normalization includes:

* Inheritance merging.
* Vault integration.
* Value flattening.
* Host normalization.

After normalization completes, two inventory representations exist:

| Representation | Purpose |
|---------------|-----------|
| `raw_yaml` | Listing and display operations |
| `normalized` | Runtime orchestration |

The orchestrator operates exclusively on normalized host definitions.

---

## 5. Logging Initialization

Logging is configured before any host processing begins.

Initialization performs the following tasks:

* Resolves log paths.
* Resolves summary paths.
* Initializes the RunUpdates logger.
* Injects the logger into PythonTools.
* Records startup lifecycle events.

After logging is initialized, host selection may begin.

PythonTools never initializes logging independently. All logging configuration originates from RunUpdates.

---

## 6. Host Selection

Host selection filters normalized inventory entries according to command-line criteria.

Supported filters include:

* `--family`
* `--distro`
* `--host`

After filtering completes, the resulting host list becomes the execution queue.

If no hosts match the supplied criteria:

* An error is logged.
* No lifecycle stages execute.
* The application terminates.

---

## 7. Host Processing

Hosts are processed in deterministic order.

Current versions execute hosts sequentially using the order defined by the normalized inventory.

After host ordering is established, RunUpdates begins processing each host individually.

Future versions may introduce parallel execution while preserving per-host ordering guarantees.

### 7.1 Session Creation

Before lifecycle execution begins, RunUpdates establishes a session for the target host.

Execution method depends on host type.

| Host Type | Session Type |
|------------|-------------|
| Local Host | `sudo_run` |
| Remote Host | `SSHSession` |

Session creation records:

- Connection attempts.
- Successful connections.
- Authentication methods.
- Connection failures.

Sensitive authentication information is never logged.

If session creation fails:

* The host is marked as failed.
* A host summary is written.
* Processing continues with the next host.

---

## 8. Lifecycle Execution

Each host progresses through the same lifecycle.

```text
check → refresh → update? → clean → reboot detection
```

After lifecycle execution begins, every stage records:

* Executed command.
* Exit code.
* Standard output.
* Standard error.
* Classification information.
* Execution timing.

### 8.1 Check

The check stage determines whether updates are available.

Example commands include:

```bash
zypper patch-check
apt list --upgradable
dnf check-update
```

Current implementations primarily rely on command return status and distro-specific behavior.

Future enhancements may provide:

* Total update counts.
* Security update counts.
* Structured update reporting.
* JSON result generation.

### 8.2 Refresh

The refresh stage updates package repository metadata.

Example commands include:

```bash
zypper refresh
apt update
dnf check-update
```

After refresh completes, repository health information becomes available for classification.

If refresh fails:

* The host is marked failed.
* Remaining stages continue.
* Failure details are included in the host summary.

### 8.3 Update

The update stage executes only when updates are available.

Example commands include:

```bash
zypper up
apt upgrade -y
dnf upgrade -y
```

After update execution completes, status information is captured for summary generation.

Failures during this stage affect only the current host.

Execution continues for all remaining hosts.

### 8.4 Clean

The clean stage performs package-management cleanup.

Example commands include:

```bash
zypper clean
apt autoremove
dnf clean all
```

After cleanup completes, lifecycle processing continues regardless of prior failures.

This stage executes even when update operations fail.

### 8.5 Reboot Detection

The reboot detection stage determines whether a system restart is required.

Common mechanisms include:

```text
openSUSE      : zypper needs-rebooting
Debian/Ubuntu : /var/run/reboot-required
Red Hat       : needs-restarting -r
```

The resulting state is normalized into a boolean value.

Example:

```json
{
  "reboot_required": true
}
```

or

```json
{
  "reboot_required": false
}
```

---

## 9. Error Classification Integration

RunUpdates separates command execution from operational classification.

Each lifecycle stage captures:

- Exit code
- Standard output
- Standard error
- Timing information

After execution data is collected, the classification engine evaluates the result.

```text
Command Execution
        │
        ▼
Raw Result
        │
        ▼
Classification Engine
        │
        ├─ Repository Health
        ├─ Update Status
        ├─ Host Status
        └─ Reboot Status
        │
        ▼
Host Summary
        │
        ▼
Fleet Summary
```

The authoritative classification rules are defined in **Error_Classification.md**.

RunUpdates intentionally separates orchestration from classification to ensure deterministic behavior and consistent reporting across supported Linux distributions.

---

## 10. Per-Host Summaries

After lifecycle execution completes, RunUpdates generates a host-specific summary.

Summary files are written as:

```text
<hostname>.json
```

Each summary contains:

* Lifecycle status.
* Update status.
* Repository health.
* Reboot state.
* Exit codes.
* Captured output.
* Timestamps.
* Lifecycle events.
* Classification results.

After a host summary is written, processing continues to the next host.

Host summaries are generated even when execution terminates early.

---

## 11. Final Aggregation

After all hosts have completed processing, RunUpdates generates the final fleet summary.

The aggregation file is written as:

```text
summary.json
```

The summary contains:

* Run start time.
* Run end time.
* Total duration.
* Host count.
* Completed host count.
* Failed host count.
* Skipped host count.
* Repository health statistics.
* Reboot requirements.
* Per-host status information.

This file represents the authoritative machine-readable result of the execution.

---

## 12. Error Handling

RunUpdates employs deterministic error handling throughout the execution lifecycle.

Errors are classified and logged consistently across all supported platforms.

### 12.1 Inventory Errors

Inventory errors are considered fatal.

Behavior:

* Stop execution immediately.
* Do not contact any hosts.
* Record the failure in the log.

### 12.2 Connection Errors

Connection failures affect only the current host.

Behavior:

* Mark host as failed.
* Write a host summary.
* Continue processing remaining hosts.

### 12.3 Command Errors

Command failures are handled at the lifecycle stage level.

Behavior:

* Log the failure.
* Record command output.
* Continue executing remaining lifecycle stages.
* Include failure status in summaries.

RunUpdates never silently ignores errors.

---

## 13. Determinism Guarantees

RunUpdates is designed around deterministic execution principles.

The application guarantees:

* Stable host ordering.
* Stable lifecycle ordering.
* Stable logging structures.
* Explicit configuration behavior.
* No hidden defaults.
* No implicit modifications.
* Reproducible output generation.

After execution completes, results remain predictable and auditable.

Given the same inventory and execution environment, RunUpdates produces equivalent operational results.

---

## 14. Future Parallel Execution

Future releases may introduce controlled concurrency.

Planned enhancements include:

* Configurable concurrency limits.
* Per-host worker execution.
* Coordinated logging.
* Deterministic aggregation behavior.
* Parallel session management.

After concurrency is introduced, lifecycle behavior will remain unchanged.

Only scheduling and execution orchestration will evolve.

---

## 15. Summary

RunUpdates executes updates through a fully deterministic lifecycle that prioritizes predictability, auditability, and operational safety.

Key characteristics include:

* Explicit execution flow.
* Deterministic behavior.
* Structured logging.
* Consistent classification.
* Reliable summaries.
* Operator-grade reporting.

This document serves as the authoritative reference for runtime execution behavior within RunUpdates.

---

## 16. Notes

This document focuses exclusively on execution sequencing and runtime behavior.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Inventory.md](Inventory.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)
* [PythonTools.md](PythonTools.md)
* [QuickStart.md](QuickStart.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

Execution behavior defined in this document is considered authoritative for all RunUpdates runtime operations.