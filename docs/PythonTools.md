# RunUpdates PythonTools Integration

**Part of:** RunUpdates
**Document:** PythonTools Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates, PythonTools
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Design Principles](#3-design-principles)
4. [Architecture Overview](#4-architecture-overview)
5. [Logging Integration](#5-logging-integration)
   1. [Logger Injection](#51-logger-injection)
   2. [NullLogger Fallback](#52-nulllogger-fallback)
6. [Secrets Integration](#6-secrets-integration)
7. [Execution Primitives](#7-execution-primitives)
   1. [Local Command Execution](#71-local-command-execution)
   2. [Privileged Local Execution](#72-privileged-local-execution)
   3. [Remote Execution](#73-remote-execution)
8. [Return Structures](#8-return-structures)
9. [Helpers](#9-helpers)
   1. [Current Helpers](#91-current-helpers)
   2. [Planned Helpers](#92-planned-helpers)
10. [Boundaries and Responsibilities](#10-boundaries-and-responsibilities)
11. [Distribution and Versioning](#11-distribution-and-versioning)
12. [RunUpdates Integration](#12-runupdates-integration)
13. [Summary](#13-summary)
14. [Notes](#14-notes)

---

## 1. Overview

PythonTools is a standalone execution library used by RunUpdates to provide deterministic command execution across local and remote systems.

PythonTools is not an internal RunUpdates component. It is a reusable, project-agnostic dependency that provides command execution, SSH connectivity, logging integration, and secret injection.

RunUpdates relies on PythonTools as its execution layer but retains responsibility for orchestration, configuration management, classification, and reporting.

---

## 2. Purpose

PythonTools exists to provide a shared execution platform for Linktech Engineering tools.

Its goals are to:

* Provide deterministic execution behavior.
* Provide consistent return structures.
* Eliminate duplicate execution code.
* Support secure authentication methods.
* Support injected logging.
* Remain independent from downstream applications.

After PythonTools returns execution results, downstream applications are responsible for interpreting those results.

---

## 3. Design Principles

PythonTools was designed around several core principles.

### Deterministic

Execution results are structured, predictable, and stable.

### Minimal

PythonTools avoids unnecessary dependencies, hidden behavior, and implicit state.

### Project-Agnostic

PythonTools contains no knowledge of:

* YAML structures
* Inventory models
* Operating system classifications
* Exit-code interpretation
* Application orchestration

### Injectable

Logging and secrets are always provided externally.

### Reusable

PythonTools is intended to serve multiple downstream applications.

---

## 4. Architecture Overview

PythonTools provides execution services only.

```text
RunUpdates
        │
        ▼
PythonTools
        │
        ├─ local_command()
        ├─ sudo_run()
        └─ SSHSession()
```
PythonTools executes commands and returns results.

RunUpdates consumes those results and applies operational meaning.

The relationship between components remains intentionally simple:

* PythonTools executes commands.
* RunUpdates performs classification.
* RunUpdates generates summaries.

---

## 5. Logging Integration

PythonTools supports externally supplied logging.

### 5.1 Logger Injection

PythonTools does not initialize logging.

Instead, downstream tools provide a logger:

```Python
from PythonTools.logging import set_logger

set_logger(runupdates_logger)
```

After logger injection, all execution pathways use the supplied logger.

### 5.2 NullLogger Fallback

If no logger is provided, PythonTools uses NullLogger.

Characteristics include:

* Supports all logging APIs.
* Produces no output.
* Requires no configuration.
* Prevents execution failures caused by missing loggers.

This allows PythonTools to operate safely in:

* Unit tests
* Development environments
* Standalone scripts

---

## 6. Secrets Integration

PythonTools does not load, validate, or manage secrets.

Secrets are supplied by downstream applications:

```Python
from PythonTools.secrets import set_secrets

set_secrets(secrets_dict)
```

Common secret types include:

* Usernames
* Passwords
* SSH keys
* Authentication tokens

PythonTools uses these values only during execution.

PythonTools never:

* Logs secrets.
* Persists secrets.
* Validates inventory structures.

---

## 7. Execution Primitives

PythonTools provides three primary execution mechanisms.

### 7.1 Local Command Execution

Non-privileged commands execute through local_command().

Example:
```Python
result = local_command("ls -la")
```

Typical uses include:

* Environment inspection
* Diagnostics
* Status collection

### 7.2 Privileged Local Execution

Privileged commands execute through sudo_run().

Example:
```Python
result = sudo_run("zypper refresh")
```

Characteristics include:

* Secure password handling.
* Captured output.
* Captured exit codes.
* Deterministic results.

Passwords are never written to logs.

### 7.3 Remote Execution

Remote execution occurs through SSHSession.

Example:
```Python
session = SSHSession(
    address="192.0.2.10",
    port=2222,
    username="admin",
    keyfile="/path/to/key",
    password="fallback"
)

result = session.run("zypper up")
```

Authentication priority:

1. SSH key authentication
2. Password authentication

SSHSession manages:

* Connection establishment
* Session lifecycle
* Command execution
* Output collection
* Error normalization

Transport failures are converted into deterministic exceptions.

---

## 8. Return Structures

All execution interfaces return a common structure.

Example:
```Python
{
    "stdout": "...",
    "stderr": "...",
    "exit_code": 0,
    "ok": True
}
```

Characteristics include:

* Consistent keys.
* Consistent types.
* Consistent behavior across local and remote execution.

PythonTools records facts but does not interpret those facts.

Classification occurs in downstream applications.

---

## 9. Helpers

PythonTools includes supporting utilities that simplify common operations.

### 9.1 Current Helpers

Current helper functionality includes:

* NullLogger
* Logging injection
* Secrets injection
* SSH session management
* Local execution wrappers

### 9.2 Planned Helpers

Future helper functionality may include:

* Network helpers
* Operating system helpers
* Command helpers
* File helpers

Additional helper functionality will be added as requirements stabilize.

---

## 10. Boundaries and Responsibilities

PythonTools intentionally limits its scope.

PythonTools must not:

* Load YAML.
* Manage inventory.
* Interpret exit codes.
* Understand operating system models.
* Initialize logging.
* Store secrets.
* Define orchestration logic.
* Define update workflows.

After execution completes, responsibility transfers to the downstream application.

This separation preserves portability and maintainability.

---

## 11. Distribution and Versioning

PythonTools is maintained as an independent repository.

It is currently distributed as source code and is not published to public package repositories.

*** Local Installation

Example installation:
```Shell
pip install -e .
```

Editable installation allows downstream projects to immediately consume updates.

### Repository Layout

```Plain Text
PythonTools/
├── logging.py
├── secrets.py
├── sessions.py
├── commands.py
└── helpers/
```

### Versioning

PythonTools maintains its own versioning independent of downstream applications.

---

## 12. RunUpdates Integration

RunUpdates treats PythonTools as a stable execution dependency.

RunUpdates consumes:

* local_command()
* sudo_run()
* SSHSession()
* set_logger()
* set_secrets()

RunUpdates does not access PythonTools internals.

The separation between the projects is intentional.

PythonTools provides execution.

RunUpdates provides:

* Inventory management.
* Orchestration.
* Classification.
* Logging policy.
* Summary generation.

This separation allows both projects to evolve independently.

---

## 13. Summary

PythonTools provides deterministic execution services for RunUpdates and other Linktech Engineering applications.

Key characteristics include:

* Consistent execution behavior.
* Unified return structures.
* Local and remote execution support.
* Logging integration.
* Secret injection.
* Clear responsibility boundaries.

PythonTools serves as the execution foundation while downstream tools provide operational behavior.

---

## 14. Notes

This document focuses exclusively on PythonTools integration and execution services.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Inventory.md](Inventory.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)
* [QuickStart.md](QuickStart.md)
* [Schema_Reference.md](Schema_Reference.md)
* [Troubleshooting.md](Troubleshooting.md)

PythonTools behavior described in this document is considered authoritative for all RunUpdates execution-layer interactions.