# RunUpdates — Execution Flow

This document describes the full execution lifecycle of RunUpdates, from startup to final result aggregation.
It complements **ARCHITECTURE.md** by focusing on when each component runs and how the system behaves during a complete update cycle.

RunUpdates is designed to be deterministic, predictable, and operator‑grade.
The execution flow reflects these principles.

## 1. Purpose

The goal of this document is to:

* explain the exact sequence of operations during a run
* clarify how inventory, sessions, logging, and summaries interact
* define error‑handling behavior
* document determinism guarantees
* prepare for future parallel execution

This is the authoritative reference for understanding how RunUpdates performs updates.

## 2. High‑Level Lifecycle

A full RunUpdates execution follows this sequence:

1. Load inventory
2. Validate schema
3. Normalize inventory (including vault merge)
4. Initialize logging
5. Select hosts
6. Iterate through hosts
7. Create session (local via sudo_run, or SSH)
8. check
9. refresh
10. update (only if needed)
11. clean
12. reboot detection
13. Write per‑host summary
14. Final aggregation and write final summary

Each step is deterministic and produces structured logs.

## 3. Detailed Execution Flow

### 3.1 Load Inventory

RunUpdates loads hosts.yml using the **RunUpdatesInventoryLoader**.

Actions:
* read YAML
* load raw structure
* prepare for validation

Failures here stop execution immediately.

### 3.2 Validate Schema

Validation ensures:
* required fields exist
* types are correct
* no unknown keys
* no invalid ports
* no malformed host entries
* address is always a list

If validation fails:
* an error is logged
* execution stops before any host is contacted

### 3.3 Normalize Inventory

The loader performs:
* inheritance merging
* vault merging
* flattening
* normalization into host entries

Two representations are produced:
* **raw_yaml** — used for list operations
* **normalized** — used for orchestration

The orchestrator receives only normalized hosts.

### 3.4 Initialize Logging

RunUpdates:
* resolves log and summary paths
* initializes logging with explicit paths
* injects logger into PythonTools
* writes initial lifecycle entries

PythonTools never initializes logging on its own.

### 3.5 Select Hosts

The selector filters normalized hosts based on CLI arguments:

* [--family]
* [--distro]
* [--host]

If no hosts match, execution stops with an error.

### 3.6 Iterate Through Hosts

Hosts are processed in deterministic order:
* as defined by the normalized inventory
* with no parallelism (current version)

Future versions will allow concurrency while preserving per‑host ordering.

### 3.7 Create Session

For each host:
* **local execution** uses sudo_run via PythonTools
* **remote execution** uses SSHSession via PythonTools

Session creation logs:
* connection attempt
* success or failure
* authentication method (non‑sensitive)

If session creation fails:
* the host is marked as failed
* a per‑host summary is still written
* execution continues to the next host

## 4. Lifecycle Stages

The executor runs the deterministic lifecycle:

**check → refresh → update? → clean → reboot detection**

Each stage logs:
* command
* exit code
* stdout/stderr
* classification
* timing

### 4.1 refresh

Runs the distro’s refresh/update‑metadata command.

Examples:
* [zypper refresh]
* [apt update]
* [dnf check-update]

If refresh fails:
* host is marked as failed
* remaining stages still run
* summary reflects failure

### 4.2 check

Runs the distro’s “check for updates” command.

Examples:
* [zypper patch-check]
* [apt list --upgradable]
* [dnf check-update]

Current behavior:
* exit‑code interpretation only
* no parsing of update counts yet

Future versions will add:
* total update count
* security update count
* structured JSON result

### 4.3 update (conditional)

Runs only if the check stage indicates updates are available.

Examples:
* [zypper up]
* [apt upgrade -y]
* [dnf upgrade -y]

Failures here do not stop execution for other hosts.

### 4.4 clean

Runs the distro’s cleanup command.

Examples:
* [zypper clean]
* [apt autoremove]
* [dnf clean all]

This stage always runs, even if update failed.

### 4.5 reboot detection

Checks distro‑specific reboot indicators.

Examples:
* [openSUSE: zypper needs-rebooting]
* [Debian/Ubuntu: /var/run/reboot-required]
* [RedHat-family: needs-restarting -r]

Captured:
* [reboot_required: true/false]

## 5. Per‑Host Summary (Implemented)

After all lifecycle stages complete, RunUpdates writes a per‑host JSON summary:

Code
```
<hostname>.json
```

Each summary includes:
* lifecycle status
* update status
* repo health
* reboot requirement
* exit codes
* stdout/stderr
* timestamps
* lifecycle events

Summaries are written even if the host fails early.

## 6. Final Aggregation (Implemented)

After all hosts complete, RunUpdates aggregates results into:

Code
```
summary.json
```

This includes:
* run start/end
* duration
* total hosts
* completed
* failed
* skipped
* repo_broken
* reboot_required
* per‑host status map

This is the machine‑readable fleet summary.

## 7. Error Handling Flow

RunUpdates uses deterministic error handling.

### 7.1 Inventory Errors

* stop execution immediately
* no hosts are contacted

### 7.2 Connection Errors

* host marked as failed
* per‑host summary written
* execution continues

### 7.3 Command Errors

* logged with classification
* host continues through remaining stages
* summary reflects failure

RunUpdates never silently ignores errors.

## 8. Determinism Guarantees

RunUpdates guarantees:
* stable host ordering
* stable lifecycle ordering
* stable logging format
* no implicit defaults
* no hidden behavior
* reproducible results

Given the same inventory and environment, RunUpdates produces the same output.

## 9. Parallel Execution (Future)

Parallel execution will introduce:
* concurrency limits
* per‑host execution threads
* grouped logging
* deterministic ordering per host

The lifecycle remains unchanged; only scheduling changes.

### 10. Summary

The RunUpdates execution flow is:
* explicit
* deterministic
* auditable
* operator‑grade

This document defines the authoritative lifecycle for all update operations.
