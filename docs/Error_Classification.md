# Error Classification — RunUpdates

**Part of:** RunUpdates
**Document:** Error Classification Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-26

## Table of Contents
1. [Overview](#1-overview)
2. [Classification Philosophy](#2-classification-philosophy)
3. [Inventory-Based Exit-Code Model](#3-inventory-based-exit-code-model)
4. [Host Classification Categories](#4-host-classification-categories)
5. [Repository Health Classification](#5-repository-health-classification)
6. [Update Availability Classification](#6-update-availability-classification)
7. [Execution Flow Integration](#7-execution-flow-integration)
8. [PythonTools Integration](#8-pythontools-integration)
9. [Logging & Reporting](#9-logging--reporting)
10. [Examples](#10-examples)
11. [Notes](#11-notes)

---

## 1. Overview

This document describes how RunUpdates interprets
command results, classifies host states, and records
those classifications throughout the update pipeline.

Unlike traditional update tools, RunUpdates does not
assign universal meaning to exit codes.

Instead, command results are interpreted using
inventory-defined rules combined with deterministic
fallback mechanisms.

This approach allows RunUpdates to support multiple
Linux distributions without requiring code changes
for every package manager.

---

## 2. Classification Philosophy

RunUpdates is designed around several core principles.

### 2.1 Deterministic Behavior

Command interpretation must always produce the same
result given the same inventory, commands, and outputs.

### 2.2 Inventory-Driven Rules

Exit-code meanings originate from the inventory rather
than application code.

RunUpdates does not assume that:

* Exit code 0 means updates are unavailable
* Exit code 100 means updates are available
* Exit code 1 indicates failure

These interpretations are defined per distribution.

### 2.3 Distribution Independence

Different package managers use different commands,
outputs, and exit codes.

RunUpdates provides a common interpretation layer
without forcing distributions into a single behavior
model.

### 2.4 Explicit Classification

Every lifecycle stage produces a documented
classification.

No hidden assumptions or implicit interpretations
are permitted.

---

## 3. Inventory-Based Exit-Code Model

Exit-code interpretation is defined within the
inventory.

Example:

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [101]
    error: ["*"]
```

Classifications are defined per lifecycle command.

For example:

```yaml
exit_codes:
  refresh:
    success: [0]
    error: ["*"]

  check:
    up_to_date: [0]    
    patches_available: [101]
    error: ["*"]

  update:
    success: [0]
    reboot_required: [102]
    error: ["*"]
```

The executor evaluates each command against the
corresponding classification *ap.

* command can therefore use completely different
exit-code meanings then another command on the
same distribution.

---

## 4. Host Classification Categories

RunUpdates classifies host state rather than simply
classifying process exit codes.

Common classifications include:

### 4.1 Up To Date

The host does not require updates.

Typical Sources:

* Inventory exit-code match
* Distro-specific command output

### 4.2 Patches Available
*Updates are available for installation*.

Typical Sources:

* Inventory-defined exit-code mappings
* Stdout analysis fallback

### 4.3 Updated

Updates were successfully installed.

Typical Sources:

* Successful update command execution
* Post update validation

### 4.4 Reboot Required

Updates completed successfully but additional action
is necessary before the host is considered fully
updated.

Typical Sources:

* Inventory-defined reboot exit codes
* Distribution-specific reboot indicators

### 4.5 Repo Broken

Repository metadata could not be retrieved or
validated.

Hosts classified as repo_broken are excluded from
update execution unless overridden.

### 4.6 Error

Command execution completed but produced a failure
condition.

Examples include:

* Package manager failures
* Invalid command output
* Unexpected lifecycle results

### 4.7 Fatal

An unrecoverable error prevented further host
processing.

Examples include:

* Authentication failure
* Session initialization failure
* Missing required configuration
* Unexpected execution exceptions

Fatal classifications terminate processing for the
current host only.

---

## 5. Repository Health Classification

Repository availability is evaluated independently
of update availability.

RunUpdates analyzes stderr output and execution
results from repository operations.

Common indicators include:

* Repository metadata failures
* Repository synchronization failures
* Missing repositories
* Authentication failures
* Signature validation failures

Hosts classified as:

```text
repo_broken
```

are skipped during update execution.

This prevents accidental execution against hosts that
cannot reliably determine package state.

### 5.1 Force Override

When:

```text
--force
```

is specified, execution may continue despite
repository health warnings.

The  host classification remains recorded in logs and
summaries.

---

## 6. Update Availability Classification

RunUpdates uses a layered classification strategy.

### 6.1 Primary Method
Exit-code mappings defined in the inventory.

Example:

```yaml
check
  up_to_date: [0]
  patches_avail*ble: [101]
  error: ["*"]
```

### 6.2 Secondary Method

Stdout-based detection.

RunUpdates scans command output for common update
indicators.

Examples include:

```text
upgradable
updates available
patches available
```

This provides a distribution-agnostic fallback when
package-manager exit codes are unreliable.

### 6.3 Deterministic Precedence

Classification priority is:

```text
Inventory Rules
        ↓
Stdout Detection
        ↓
Generic Error Classification
```

Inventory rules always take precedence.

---

## 7. Execution Flow Integration

Classification occurs throughout the update lifecycle.

```text
CHECK
  ↓
CLASSIFY
  ↓
REFRESH
  ↓
CLASSIFY
  ↓
UPDATE
  ↓
CLASSIFY
  ↓
CLEAN
  ↓
CLASSIFY
```

Every lifecycle stage produces a deterministic result.

Classification results influence:

* Update execution decisions
* Reboot handling
* Summary generation
* Operator reporting

Classification never relies on external state.

---

## 8. PythonTools Integration

PythonTools provides the underlying execution layer.

Responsibilities include:

* Command execution
* SSH session management
* Exit-code capture
* stdout capture
* stderr capture
* Exception handling
* Secret redaction

RunUpdates performs classification using the data
returned by PythonTools.

### 8.1 Fatal Conditions

Examples include:

* SSH connection failure
* Authentication failure
* Command execution failure
* Session initialization failure
* Unexpected exceptions

These conditions are typically classified as fatal
because execution cannot continue safely.

### 8.2 Separation of Responsibilities

PythonTools performs execution.

RunUpdates performs interpretation.

This separation keeps PythonTools project-agnostic
while allowing RunUpdates to implement
inventory-specific behavior.

---

## 9. Logging & Reporting

Classification information is recorded in structured
logs and host summaries.

Logged information may include:

* Lifecycle stage
* Command
* Exit code
* Classification
* Repository health
* Update status
* Reboot requirements

Sensitive data is never recorded.

Examples include:

* Passwords
* SSH private keys
* Vault secrets
* Authentication tokens

### 9.1 Host Summaries

Per-host Summaries may contain:

```json
{
  "hostname": "web01",
  "status": "*atches_available",
  "repo_broken" false,
  "reboot_required": true
}
```

### 9.2 Aggregated Results

Classification information is also included in:

```text
summary.json
```

and other build or reporting artifacts.

---

## 10. Examples

## 10.1 Host Up To Date

```yaml
exit_code: 0
classification: up_to_date
```

### 10.2 Updates Available

```yaml
exit_code: 101
classification: patches_available
```

### 10.3 Reboot Required

```yaml
exit_code: 102
classification: reboot_required
```

### 10.4 Repository Failure
```yaml
classification: repo_broken
```

### 10.5 Authentication Failure

```yaml
classification: fatal
```

### 10.6 Package Manager Failure

```yaml
classification: error
```

---

## 11. Notes

RunUpdates does not maintain a universal exit-code
table.

Classifications originate from inventory definitions
and deterministic interpretation rules.

This design allows support for multiple Linux
distributions without embedding package-manager
semantics in application code.

The classification model is intentionally:

* Deterministic
* Inventory-driven
* Distribution-agnostic
* Auditable
* Extensible

All classification behavior described in this document
is considered authoritative for RunUpdates operation.