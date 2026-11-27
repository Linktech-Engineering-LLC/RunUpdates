# RunUpdates Logging Architecture

**Part of:** RunUpdates
**Document:** Logging Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-26

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Logging Philosophy](#-3-logging-philosophy)
4. [Logging Components](#-4-logging-components)
   1. [RunUpdates Logging Layer](#41-runupdates-logging-layer-projectspecific)
   2. [PythonTools Logging Interface](#42-pythontools-logging-interface-projectagnostic)
5. [Logger Injection Model](#-5-logger-injection-model)
6. [NullLogger Fallback](#-6-nulllogger-fallback)
7. [Command Logging Model](#-7-command-logging-model)
   1. [Command Start](#71-command-start)
   2. [Command End](#72-command-end)
   3. [Command Error](#73-command-error)
   4. [Captured Fields](#74-captured-fields)
8. [Redaction Rules](#-8-redaction-rules)
9. [PythonTools Integration](#-9-logging-in-pythontools)
10. [Error Logging](#-10-error-logging)
11. [Log File Structure](#-11-log-file-structure)
    1. [Log Rotation and Archival](#111-log-rotation-and-archival)
    2. [Determinism Guarantees](#112-determinism-guarantees)
    3. [Parallel Execution Guarantees](#113-parallel-execution-ordering-guarantees)
12. [Error Classification Integration](#12-error-classification-integration)
13. [Future Enhancements](#-13-future-enhancements)
14. [Summary](#14-summary)
15. [Notes](#15-notes)

---

## 1. Overview

RunUpdates uses a deterministic, operator-grade logging architecture designed for auditability, reproducibility, and cross-tool consistency.

Logging is intentionally explicit, structured, and free of hidden behavior.

This document defines how logging operates, how PythonTools integrates with the logging system, how events are recorded, and how execution data becomes part of the permanent operational record.

---

## 2. Purpose

The goals of the logging system are to:

* Provide complete execution visibility.
* Preserve operational history.
* Record command execution consistently.
* Support troubleshooting and incident review.
* Enable deterministic auditing.
* Protect sensitive information through redaction.

After execution begins, all significant lifecycle events are recorded through the logging subsystem.

Logging is considered a core component of correctness within RunUpdates.

---

RunUpdates uses a deterministic, operator‑grade logging model designed for audit transparency, reproducibility, and cross‑tool consistency.
Logging is intentionally explicit, structured, and free of hidden behavior.

This document describes:

* how logging works
* how PythonTools integrates with RunUpdates logging
* what is logged
* what is never logged
* how command execution is recorded
* how errors are classified and reported

## 🧱 3. Logging Philosophy

RunUpdates follows these principles:

* **Append Only** - log entries are never overwritten or deleted
* **Deterministic** — logs always reflect the exact sequence of operations
* **Structured** — consistent formatting across all hosts and commands
* **Audit‑friendly** — timestamps, exit codes, and classifications are always present
* **Redacted** — secrets and sensitive data are never logged
* **Operator‑grade** — logs are readable, actionable, and suitable for incident review
* **Cross‑tool compatible** — consistent with NMS_Tools, VSCode-Updater, and future Linktech tools

Logging is not optional and not configurable — it is a core part of the system’s correctness model.

## 🧩 4. Logging Components

RunUpdates uses two layers:

### 4.1 RunUpdates Logging Layer (project‑specific)
Responsible for:
* resolving log paths
* initializing the logger
* formatting messages
* writing structured entries
* redacting sensitive fields

RunUpdates fully controls logging behavior.

### 4.2 PythonTools Logging Interface (project‑agnostic)

Responsible for:
* receiving an injected logger
* providing _NullLogger fallback
* exposing a minimal logging API
* never initializing logging itself

PythonTools does not know:
* where logs are stored
* how logs are formatted
* what the project’s logging policy is

RunUpdates controls all of that.

---

## 🔌 5. Logger Injection Model
At startup, RunUpdates injects its logger into PythonTools:

```python
from PythonTools.logging import set_logger
set_logger(runupdates_logger)
```

This ensures:

* all local commands (sudo_run)
* all remote commands (SSHSession.run)
* all helpers

…log through the same unified interface.

**PythonTools never initializes logging.**
It only uses what RunUpdates provides.

---

## 🧰 6. NullLogger Fallback
If RunUpdates does not inject a logger (e.g., during testing), PythonTools uses _NullLogger.

_NullLogger characteristics:

* implements .debug(), .info(), .warning(), .error()
* implements .command_start(), .command_end(), .command_error()
* all methods are no‑ops
* produces zero output

This ensures PythonTools is safe to use in:

* unit tests
* standalone scripts
* early development
* environments without logging

---

## 🛠 7. Command Logging Model
Every command executed by RunUpdates is logged with:

### 7.1 Command Start

```text
[2026-04-19 14:55:12] [host=Lab-Suse-01] [step=check] START: zypper refresh && zypper patch-check --with-optional
```

### 7.2 Command End

```text
[2026-04-19 14:55:13] [host=Lab-Suse-01] [step=check] END: exit_code=101 classification=patches_available
```

### 7.3 Command Error

```text
[2026-04-19 14:55:13] [host=Lab-Suse-01] [step=check] ERROR: exit_code=255 stderr="SSH connection failed"
```

### 7.4 Captured Fields

* timestamp
* host
* step (check/refresh/update/postcheck/clean/reboot)
* command string
* exit code
* stdout (Stdout is truncated to prevent log bloat and ensure logs remain readable and diff‑friendly.)
* stderr
* classification (from YAML exit‑code model)

This ensures complete auditability.

### 7.5 Note on Summaries

Per‑host summaries are implemented and written after each host completes its lifecycle.Operator logs are currently the authoritative record of execution.

---

## 🔐 8. Redaction Rules

RunUpdates **never logs**:

* passwords
* sudo prompts
* SSH authentication failures containing sensitive text
* private key contents
* vault file contents
* raw secrets
* environment variables containing secrets

If a command contains a password (rare), it is redacted before logging.

---

## 📦 9. PythonTools Integration

PythonTools exposes a minimal logging API:

```Python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)

logger.command_start(host, step, command)
logger.command_end(host, step, exit_code, classification)
logger.command_error(host, step, exit_code, stderr)
```

### 9.1 PythonTools responsibilities:

* call the logger at the correct times
* pass structured data
* never format messages itself
* never write files
* never store logs

### 9.2 RunUpdates responsibilities:

* define formatting
* define log file location
* define rotation policy
* define redaction rules

This separation keeps PythonTools reusable and clean.

---

## 🧪 10. Error Logging

Errors are logged deterministically:

### 10.1 Connection Errors

```text
ERROR: SSH connection failed (timeout)
```

### 10.2 Command Errors

```text
ERROR: exit_code=1 stderr="zypper: repository not found"
```

### 10.3 Inventory Errors

```text
ERROR: Missing required field: packages.update
```

### 10.4 Secrets Errors

```text
ERROR: No valid authentication method available
```

Errors never stop the pipeline unless they occur before execution begins.

---

## 🧭 11. Log File Structure

RunUpdates writes logs to a stable, non‑timestamped log file:

```text
logs/
  runupdates.log
```

This file is append‑only and persists across runs.

### 11.1 Log Rotation and Archival
Timestamped log files are **only created when logs are archived**.

Archived logs use date‑only filenames in the format:

`logs/archive/runupdates-YYYYMMDD.log`

Examples:

`runupdates-20260522.log`
`runupdates-20260523.log`

This ensures:
* deterministic naming
* clean daily grouping
* predictable sorting
* consistency with other Linktech Engineering tools

RunUpdates does not currently perform automatic rotation; archival support is planned for a future release.

### 11.2 Determinism Guarantees
* Each run appends to the same active log file
* Archived logs preserve the exact state of the file at the time of rotation
* Ordering is strictly chronological
* No log entries are overwritten

Parallel execution (future) will preserve ordering per host, even if cross‑host interleaving occurs.

### 11.3 Parallel Execution Ordering Guarantees

When parallel execution is introduced, RunUpdates will maintain strict ordering **per host**.  
Even if multiple hosts run concurrently, each host’s log entries will remain internally ordered and deterministic.  
Cross‑host interleaving may occur, but never within a single host’s sequence.

---

## 12. Error Classification Integration

RunUpdates separates logging, classification, and reporting into distinct responsibilities.

The logging system records raw execution results including:

* Exit codes
* Standard output
* Standard error
* Timing information
* Executed commands

After execution data is captured, the classification engine evaluates the results according to the rules defined in `Error_Classification.md`.

```text
Command Execution
        │
        ▼
Logging Layer
        │
        ▼
Raw Log Entry
        │
        ▼
Classification Engine
        │
        ▼
Summary Generation
```

The relationship between these components is intentionally simple:

Logging records raw facts.
Classification interprets those facts.
Summaries consume the classifications.

This separation ensures complete auditability while maintaining deterministic reporting behavior.

Additional classification details are documented in [Error_Classification.md](Error_Classification.md).

---

## 🔮 13. Future Enhancements

* JSON log output (optional)
* structured event IDs
* parallel execution log grouping
* log streaming for UI integrations

---

## 14. Summary 

The RunUpdates logging architecture is designed to provide deterministic, audit-friendly execution records. 

Key characteristics include: 
* Append-only operation. 
* Structured logging. 
* Secret redaction. 
* Unified PythonTools integration. 
* Stable log formats. 
* Deterministic ordering. 
* Cross-tool consistency. 

The logging subsystem serves as the authoritative operational record for RunUpdates execution. 

--- 

## 15. Notes 

This document focuses exclusively on logging architecture and execution recording. For related information, see: 

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Inventory.md](Inventory.md)
* [Operation.md](Operation.md)
* [PythonTools.md](PythonTools.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

The logging architecture defined in this document is considered authoritative for all RunUpdates runtime logging behavior.