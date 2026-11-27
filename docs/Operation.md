# RunUpdates Operation Guide

**Part of:** RunUpdates
**Document:** Operation Guide
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-26

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Operating RunUpdates](#3-operating-runupdates)
4. [Host Selection](#4-host-selection)
5. [Execution Modes](#5-execution-modes)
   1. [Normal Mode](#51-normal-mode)
   2. [Dry-Run Mode](#52-dry-run-mode)
6. [Connection Behavior](#6-connection-behavior)
   1. [Local Execution](#61-local-execution)
   2. [Remote Execution](#62-remote-execution)
   3. [Authentication](#63-authentication)
7. [Update Execution](#7-update-execution)
   1. [Lifecycle Execution](#71-lifecycle-execution)
   2. [Repository Health Handling](#72-repository-health-handling)
   3. [openSUSE Update Modes](#73-opensuse-update-modes)
8. [Monitoring Execution](#8-monitoring-execution)
9. [Reviewing Results](#9-reviewing-results)
10. [Common Operational Scenarios](#10-common-operational-scenarios)
11. [Failure Handling](#11-failure-handling)
12. [Future Enhancements](#12-future-enhancements)
13. [Summary](#13-summary)
14. [Notes](#14-notes)

---

## 1. Overview

RunUpdates is an operator-focused update orchestration tool designed to execute deterministic update workflows across one or more Linux hosts.

The application uses inventory-driven configuration, structured logging, declarative classification rules, and normalized host definitions to ensure consistent behavior across environments.

This document focuses on how operators interact with RunUpdates and how execution behaves from an operational perspective.

---

## 2. Purpose

The purpose of this document is to:

* Explain how RunUpdates is operated.
* Describe host selection behavior.
* Define execution modes.
* Explain connection behavior.
* Describe update execution from an operator perspective.
* Explain how results should be monitored and reviewed.
* Document common operational scenarios.

After reviewing this document, operators should understand how to safely execute and monitor RunUpdates across supported environments.

---

## 3. Operating RunUpdates

RunUpdates operates against hosts defined in the inventory.

Execution behavior is determined by:

* Inventory configuration.
* Host selection filters.
* Distro-specific command definitions.
* Exit-code classifications.
* Runtime options.

The inventory, execution lifecycle, logging model, and classification system are documented separately.

Operators are expected to understand the inventory being used before executing updates.

---

## 4. Host Selection

RunUpdates supports selective host execution through command-line filters.

Available filters include:

* `--family`
* `--distro`
* `--host`

Examples:

```bash
runupdates --family linux
```

```bash
runupdates --distro opensuse
```

```bash
runupdates --host suse-node-01
```

Hosts must satisfy all supplied filters.

The following selection rules apply:

* Disabled hosts are excluded.
* Hosts must match all specified filters.
* If no filters are supplied, all enabled hosts are selected.
* Invalid host and family combinations result in an error.
* Host selection is validated before execution begins.

Additional inventory details are documented in `Inventory.md`.

---

## 5. Execution Modes

RunUpdates currently supports two execution modes.

### 5.1 Normal Mode

Normal mode performs full update execution.

This includes:

* Host selection.
* Session establishment.
* Lifecycle execution.
* Logging.
* Classification.
* Summary generation.

Normal mode is the default operating mode.

### 5.2 Dry-Run Mode

Dry-run mode validates execution without making changes.

Dry-run mode performs:

* Host selection.
* Configuration validation.
* Lifecycle planning.

Dry-run mode does not perform:

* Command execution.
* SSH connections.
* Package updates.
* System modifications.

Operators should use dry-run mode before executing updates against new hosts or newly modified inventories.

Example:

```bash
runupdates --dry-run
```

---

## 6. Connection Behavior

RunUpdates automatically determines how each host should be accessed.

Connection decisions are made using normalized host definitions.

### 6.1 Local Execution

Local execution occurs when the target host is the current system.

Examples include:

* `localhost`
* `127.0.0.1`
* The system's own configured address
* Hosts explicitly configured as local

Local execution uses:

```text
sudo_run()
```

through PythonTools.

Local operations do not require SSH connectivity.

### 6.2 Remote Execution

Remote execution occurs when the target host is a remote system.

Remote execution uses:

```text
SSHSession()
```

through PythonTools.

Remote systems are accessed using addresses defined within the inventory.

### 6.3 Authentication

RunUpdates supports multiple authentication mechanisms.

Supported authentication methods include:

* SSH key authentication.
* Password authentication.
* Sudo credential elevation.

Authentication preference order is:

1. SSH key authentication
2. Password authentication

Authentication data is typically supplied through vault integration.

If no valid authentication method is available, execution fails before lifecycle processing begins.

---

## 7. Update Execution

RunUpdates executes updates using inventory-defined commands.

Commands are never hardcoded within the orchestrator.

### 7.1 Lifecycle Execution

Hosts execute the standard lifecycle defined in `Execution_Flow.md`.

The lifecycle consists of:

```text
check
refresh
update
clean
reboot detection
```

Commands are executed in deterministic order.

The following execution rules apply:

* Commands execute sequentially.
* Commands are logged before execution.
* Commands are logged after execution.
* Output is captured.
* Classifications are generated.
* Failures do not automatically stop the lifecycle.

After execution completes, summaries are generated.

### 7.2 Repository Health Handling

RunUpdates evaluates repository health during execution.

Repository problems may include:

* Missing metadata.
* Unreachable repositories.
* Repository configuration errors.
* Refresh failures.

When repository failures are detected:

* Repository health is classified.
* The condition is logged.
* Summaries are updated accordingly.

Repository classification behavior is documented in `Error_Classification.md`.

### 7.3 openSUSE Update Modes

RunUpdates does not enforce a specific openSUSE update strategy.

The update behavior is defined entirely by the inventory.

Example:

```yaml
packages:
  update: zypper up
```

or

```yaml
packages:
  update: zypper dup
```

Current environments primarily target openSUSE systems rather than SUSE Enterprise distributions.

For openSUSE systems:

* `zypper up` performs conservative upgrades.
* `zypper dup` performs full repository synchronization.

Tumbleweed systems typically require `zypper dup`.

Leap systems may use either approach depending on repository configuration.

RunUpdates executes whichever command is defined in the inventory.

---

## 8. Monitoring Execution

Operators should monitor execution using available runtime outputs.

The primary execution records include:

* Console output.
* Active log files.
* Host summary files.
* Fleet summary files.

During execution, lifecycle progress is visible through structured logging.

Logging behavior is documented in `Logging.md`.

---

## 9. Reviewing Results

After execution completes, operators should review generated artifacts.

Recommended review items include:

* Host execution status.
* Update status.
* Repository health.
* Reboot requirements.
* Logged errors.
* Fleet summary information.

Primary output files include:

```text
summary.json
```

and:

```text
<hostname>.json
```

Classification interpretation is documented in `Error_Classification.md`.

---

## 10. Common Operational Scenarios

RunUpdates supports several common operational workflows.

Typical scenarios include:

* Updating an entire environment.
* Updating a specific distro.
* Updating a single host.
* Validating inventory changes.
* Reviewing repository health.
* Identifying systems requiring reboot.
* Running audit-only dry-run executions.

Operators should select the most specific execution scope appropriate for the task.

---

## 11. Failure Handling

RunUpdates is designed to continue processing whenever practical.

Failure handling depends upon the type of failure encountered.

Inventory failures:

* Stop execution immediately.
* Prevent host processing.

Connection failures:

* Mark the host as failed.
* Continue processing remaining hosts.

Command failures:

* Are logged.
* Are classified.
* Continue through remaining lifecycle stages when possible.

Repository failures:

* Are classified independently.
* Are included in summaries.
* Do not necessarily prevent other hosts from executing.

Additional classification details are documented in `Error_Classification.md`.

---

## 12. Future Enhancements

Future releases may add:

* Parallel execution.
* Enhanced classification categories.
* Additional distro support.
* Inventory schema versioning.
* UI integrations.
* Structured execution reporting.
* Advanced repository management.

The operational workflow described in this document is expected to remain stable as these enhancements are introduced.

---

## 13. Summary

RunUpdates provides a deterministic and operator-focused update management workflow.

Key operational characteristics include:

* Inventory-driven behavior.
* Deterministic execution.
* Consistent host selection.
* Flexible execution modes.
* Structured logging.
* Declarative classification.
* Comprehensive reporting.

The operational model is designed to provide repeatable and auditable update execution across supported environments.

---

## 14. Notes

This document focuses on operational usage and runtime interaction with RunUpdates.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Inventory.md](Inventory.md)
* [Logging.md](Logging.md)
* [PythonTools.md](PythonTools.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

The operational guidance defined in this document is considered authoritative for the day-to-day use of RunUpdates.